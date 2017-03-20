# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.CassetteContainer import CassetteContainer
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

        self.params['specification'] = """
<h3>General description</h3>
A print line is used for screen-printing metallization pastes and for drying and firing the pastes afterwards.
The machine accepts cassettes which are unloaded one wafer at a time.
Each wafer then travels to a number of printers and dryers, before entering a firing furnace.
Lastly, all units are placed in an infinitely sized container.\n
<h3>Description of the algorithm</h3>
There are two types of loops to simulate the print line tool.
The first one runs the wafer load-in process before the first printing step.
The second loop runs the printers, so there is a separate instance for each printer.
<p>The first loop for wafer load-in consists of the following steps:
<ol>
<li>Wait for signal from first printer</li>
<li>Pick up a wafer if not already available</li>
<li>If current cassette had been empty pause momentarily to simulate loading a new stack</li>
<li>If the first position on the belt is empty, load the wafer onto it</li>
</ol>
The printer loop performs the following actions if there is a wafer available at the end of its input belt:
<ol>
<li>Remove wafer from input belt and move the belt forward by one position</li>
<li>If the current printer is the first printer in the line, send a signal to the wafer load-in process to continue</li>
<li>Wait for a certain amount of time to simulate the printing action.
The waiting time can be the belt position movement time or the printing time, depending on which is higher.</li>
<li>Start a separate process for drying or firing</li>
</ol>
The drying or firing processes hold the wafer for a set amount of time to simulate these processes.
After a drying step the wafer is placed on the input belt of the next printer and after a firing step it is placed in an output container of infinite size.
<p>If there is no wafer availalbe for printing then the second loop performs the following actions:</p>
<ol>
<li>Move the input belt forward by one position</li>
<li>If the current printer is the first printer in the line, send a signal to the wafer load-in process to continue</li>
<li>Wait for a set amount of time to simulate the belt movement action</li>
</ol>
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "PrintLine"        
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input"
        self.params['max_cassette_no_type'] = "configuration"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"
        self.params['time_new_cassette_type'] = "automation"
        self.params['units_on_belt_input'] = 8
        self.params['units_on_belt_input_desc'] = "Number of units that fit on the belt between wafer source and printer"
        self.params['units_on_belt_input_type'] = "configuration"
        
        self.params['time_step'] = 1/1
        self.params['time_step_desc'] = "Time for one wafer to progress one position on belts (seconds)"
        self.params['time_step_type'] = "automation"
        self.params['time_print'] = 25/10
        self.params['time_print_desc'] = "Time to print one wafer (seconds)"
        self.params['time_print_type'] = "process"
        self.params['time_dry'] = 90
        self.params['time_dry_desc'] = "Time for one wafer to go from printer to dryer and "
        self.params['time_dry_desc'] += "to next input (printing or firing) (seconds)"
        self.params['time_dry_type'] = "process"
        
        self.params['no_print_steps'] = 3
        self.params['no_print_steps_desc'] = "Number of print and dry stations"
        self.params['no_print_steps_type'] = "configuration"
        
        self.params['firing_tool_length'] = 10/1
        self.params['firing_tool_length_desc'] = "Travel distance for wafers in the last dryer and firing furnace (meters)"
        self.params['firing_tool_length_type'] = "configuration"
        self.params['firing_belt_speed'] = 5/1 # 5 is roughly 200 ipm
        self.params['firing_belt_speed_desc'] = "Belt speed of last dryer and firing furnace (meters per minute)"
        self.params['firing_belt_speed_type'] = "process"

        self.params['unit_distance'] = 2/10
        self.params['unit_distance_desc'] = "Minimal distance between wafers on firing furnace (meters)"
        self.params['unit_distance_type'] = "configuration"
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)
        
        self.time_dry = self.params['time_dry']        
        self.no_print_steps = self.params['no_print_steps'] 
        self.time_fire = int(60*self.params['firing_tool_length']//self.params['firing_belt_speed'])

        ### Input ###
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'])

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
        if (not (self.output_text == None)) and (max(time_out) < (60*self.params['unit_distance']/self.params['firing_belt_speed'])):
            string = "[" + self.params['type'] + "][" + self.params['name'] + "] WARNING: Wafer distance in firing furnace below set minimum"
            self.output_text.sig.emit(string)

        self.start_time = []
        self.first_run = []
        self.idle_times_internal = []
        for i in range(self.params['no_print_steps']):
            self.idle_times_internal.append(0)
            self.first_run.append(True)
            self.start_time.append(0)

        self.next_step = self.env.event() # triggers load-in from cassette
        # start belt before printers; otherwise next_step will be triggered already
        # and a different one will be created
        self.env.process(self.run_belt()) 

        for i in range(self.params['no_print_steps']):
            self.env.process(self.run_printer(i))

    def report(self):        
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.output.container.level
        production_hours = (self.env.now - self.start_time[0])/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)            

        self.utilization.append(self.output.container.level)
        
        for i in range(len(self.idle_times_internal)):
            if self.first_run[i]:
                idle_time = 0
            elif ((self.env.now-self.start_time[i]) > 0):
                idle_time = 100-100*self.idle_times_internal[i]/(self.env.now-self.start_time[i])
            self.utilization.append(["Print " + str(i),round(idle_time,1)])        

    def prod_volume(self):
        return self.output.container.level
        
    def run_belt(self): # For first belt
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']

        cassette = yield self.input.input.get() # receive first cassette
        wafer_counter = cassette_size

        while True:
            yield self.next_step

            if not wafer_counter:
                yield self.input.output.put(cassette) # return empty cassette
                cassette = yield self.input.input.get() # receive new cassette
                wafer_counter = cassette_size
                yield self.env.timeout(time_new_cassette)

            if (not self.belts[0][0]):                 
                self.belts[0][0] = True
                wafer_counter -= 1
                
#                string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Put wafer from cassette on belt" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG
           
    def run_printer(self, num):
        time_step = self.params['time_step']
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
                    self.next_step.succeed() # let first belt run
                    self.next_step = self.env.event() # make new event                
                    
                yield self.env.timeout(time_out) # belt movement time determined by the slowest: print time or by belt speed
              
#                string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Printed a wafer on printer " + str(num) #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

                # place wafer in dryer or firing furnace after printing
                if (num < (self.no_print_steps-1)):
                    self.env.process(self.dry_wafer(num))
                else:
                    self.env.process(self.fire_wafer())

            else:
                # if cannot print: move belt and wait
                self.belts[num].rotate(1)
                
                if (not num):
                    self.next_step.succeed() # let first belt run
                    self.next_step = self.env.event() # make new event                 
                    
                yield self.env.timeout(time_step) # belt movement time determined by user defined value               

                if not self.first_run[num]:
                    self.idle_times_internal[num] += time_step

    def dry_wafer(self,num): # inline process is continuous so it requires a timeout            
    
        yield self.env.timeout(self.time_dry)
        self.belts[num+1][0] = True
            
#        string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Dried a wafer on dryer " + str(num) #DEBUG
#        self.output_text.sig.emit(string) #DEBUG

    def fire_wafer(self): # inline process is continuous so it requires a timeout       
            
        yield self.env.timeout(self.time_fire)
        yield self.output.container.put(1)
        
#        string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Fired a wafer" #DEBUG
#        self.output_text.sig.emit(string) #DEBUG
    
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