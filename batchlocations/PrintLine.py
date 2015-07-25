# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import simpy
import collections

"""
Current implementation highly optimized for speed
Tried various implementations including numpy matrices containing wafer positions

Define microstops for printers
Make run_belt more sophisticated: Reload cassettes independently when empty

"""

class PrintLine(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []
        self.diagram = """blockdiag {
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Belt0"];
                       C [label = "Printer0"];
                       D [label = "Dryer0"];                       
                       E [label = "Belt1"];
                       F [label = "Printer1"];
                       G [label = "Dryer1"];
                       H [label = "Belt2"];
                       I [label = "Printer2"];                     
                       J [label = "Firing furnace"];
                       K [label = "Output"];
                       A -> B -> C -> D -> E -> F -> G -> H -> I -> J -> K;
                       D -> E [folded];
                       H -> I [folded];
                       } """        
        
        self.params = {}
        self.params['specification'] = "PrintLine consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Print and dry stations\n"
        self.params['specification'] += "- Firing furnace\n"
        self.params['specification'] += "- Output container (infinite)\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The machine accepts cassettes which are unloaded one unit at a time. "
        self.params['specification'] += "Each wafer then travels to a number of printers and dryers, "
        self.params['specification'] += "before entering a firing furnace. "
        self.params['specification'] += "Lastly, all units are placed in an infinitely sized container.\n"
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"        
        self.params['units_on_belt_input'] = 8
        self.params['units_on_belt_input_desc'] = "Number of units that fit on the belt between wafer source and printer"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one position on belts (seconds)"
        self.params['time_print'] = 2.5
        self.params['time_print_desc'] = "Time to print one wafer (seconds)"
        self.params['time_dry'] = 90
        self.params['time_dry_desc'] = "Time for one wafer to go from printer to dryer and "
        self.params['time_dry_desc'] += "to next input (printing or firing) (seconds)"
        
        self.params['no_print_steps'] = 3
        self.params['no_print_steps_desc'] = "Number of print and dry stations"
        
        self.params['firing_tool_length'] = 10.0
        self.params['firing_tool_length_desc'] = "Length of last dryer and firing furnace (meters)"
        self.params['firing_belt_speed'] = 5.0 # 5 is roughly 200 ipm
        self.params['firing_belt_speed_desc'] = "Belt speed of last dryer and firing furnace (meters per minute)"

        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers on firing furnace (meters)"        
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)    
        
        self.time_dry = self.params['time_dry']        
        self.no_print_steps = self.params['no_print_steps'] 
        self.time_fire = int(60*self.params['firing_tool_length']//self.params['firing_belt_speed'])
#        self.verbose = self.params['verbose'] #DEBUG
        
#        if (self.params['verbose']): #DEBUG     
#            string = str(self.env.now) + " - [PrintLine][" + self.params['name'] + "] Added a print line" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represents belts ###
        self.belts = []
        for i in  range(self.params['no_print_steps']):            
            self.belts.append(collections.deque([False for rows in range(self.params['units_on_belt_input']+1)]))
        
        ### Infinite output container ###
        self.output = InfiniteContainer(self.env,"output")

        ### Check whether wafers will overlap ###
        time_out = []
        time_out.append(self.params['time_step'])
        time_out.append(self.params['time_print'])
        if (max(time_out) < (60*self.params['unit_distance']/self.params['firing_belt_speed'])):
            string = "[PrintLine][" + self.params['name'] + "] <span style=\"color: red\">WARNING: Wafer distance in firing furnace below set minimum</span>"
            self.output_text.sig.emit(string)

        self.start_time = []
        self.first_run = []
        self.idle_times_internal = []
        for i in range(self.params['no_print_steps']):
            self.idle_times_internal.append(0)
            self.first_run.append(True)
            self.start_time.append(0)

        for i in range(self.params['no_print_steps']):
            self.env.process(self.run_printer(i))

        self.next_step = self.env.event() # triggers load-in from cassette
        self.env.process(self.run_belt())      

    def report(self):
        string = "[PrintLine][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)
        self.output_text.sig.emit(string)
        
        self.utilization.append("PrintLine")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.output.container.level
        production_hours = (self.env.now - self.start_time[0])/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)            
        
        for i in range(len(self.idle_times_internal)):
            if self.first_run[i]:
                idle_time = 100.0
            elif ((self.env.now-self.start_time[i]) > 0):
                idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time[i])
            self.utilization.append(["p" + str(i),round(idle_time,1)])        

    def prod_volume(self):
        return self.output.container.level
        
    def run_belt(self): # For first belt
        wafer_counter = 0
        restart = True # start with new cassette
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        wafer_available = False
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            yield self.next_step
            
            if (not wafer_available): # if we don't already have a wafer in position try to get one
                yield self.input.container.get(1)
                wafer_available = True

            if (restart):
                #time delay for loading new cassette if input had been completely empty
                yield self.env.timeout(time_new_cassette)
                restart = False
            
            if (not self.belts[0][0]): 
                self.belts[0][0] = True
                wafer_available = False
                wafer_counter += 1
                
#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Put wafer from cassette on belt" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                    
            if (wafer_counter == cassette_size):
                # if current cassette is empty and there are more cassettes available, delay to load a new cassette                                   
                wafer_counter = 0                
                restart = True
           
    def run_printer(self, num):
        time_step = self.params['time_step']
#        verbose = self.params['verbose'] #DEBUG
        time_outs = []
        time_outs.append(time_step)
        time_outs.append(self.params['time_print'])
        time_out = max(time_outs)
        
        while True:            
            if (self.belts[num][-1]):
                # if last belt position contains a wafer, start printing
                
                if self.first_run[num]:
                    self.start_time[num] = self.env.now
                    self.first_run[num] = False    
            
                # remove wafer from belt
                self.belts[num][-1] = False

                # move belt and perform print
                self.belts[num].rotate(1)

                if (not num):                    
                    yield self.next_step.succeed() # let first belt run
                    self.next_step = self.env.event() # make new event                
                    
                yield self.env.timeout(time_out) # belt movement time determined by the slowest: print time or by belt speed
              
#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Printed a wafer on printer " + str(num) #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG

                # place wafer in dryer or firing furnace after printing
                if (num < (self.no_print_steps-1)):
                    self.env.process(self.dry_wafer(num))
                else:
                    self.env.process(self.fire_wafer())

            else:
                # if cannot print: move belt and wait
                self.belts[num].rotate(1)
                
                if (not num):                    
                    yield self.next_step.succeed() # let first belt run
                    self.next_step = self.env.event() # make new event                 
                    
                yield self.env.timeout(time_step) # belt movement time determined by user defined value               

                if not self.first_run[num]:
                    self.idle_times_internal[num] += time_step

    def dry_wafer(self,num): # inline process is continuous so it requires a timeout            
    
        yield self.env.timeout(self.time_dry)
        self.belts[num+1][0] = True
            
#        if (self.verbose): #DEBUG
#            string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Dried a wafer on dryer " + str(num) #DEBUG
#            self.output_text.sig.emit(string) #DEBUG

    def fire_wafer(self): # inline process is continuous so it requires a timeout       
            
        yield self.env.timeout(self.time_fire)
        yield self.output.container.put(1)
        
#        if (self.verbose): #DEBUG
#            string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Fired a wafer" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
    
    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(3600/self.params['time_print'])
        throughputs.append(3600/self.params['time_step'])
        return min(throughputs)
            
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)