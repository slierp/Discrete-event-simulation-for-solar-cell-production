# -*- coding: utf-8 -*-
from __future__ import division
from batchlocations.BatchContainer import BatchContainer
import simpy

class PrintLine(object):
        
    def __init__(self, _env, _output=None, _params = {}):
        self.env = _env
        self.output_text = _output
        self.utilization = []
        
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
        self.params['specification'] += "Lastly, all units are placed in an infinitely sized container."
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input"
        self.params['units_on_belt_input'] = 8
        self.params['units_on_belt_input_desc'] = "Number of units that fit on the belt between wafer source and printer"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one unit to progress one position (seconds)"
        self.params['time_cassette_to_belt'] = 1.0
        self.params['time_cassette_to_belt_desc'] = "Time for placing one unit onto the first belt (seconds)"
        self.params['time_print'] = 2.0
        self.params['time_print_desc'] = "Time to print one wafer (seconds)"
        self.params['time_dry'] = 90
        self.params['time_dry_desc'] = "Time for one wafer to go from printer to dryer and "
        self.params['time_dry_desc'] += "to next input (printing or firing) (seconds)"
        
        self.params['no_print_steps'] = 3
        self.params['no_print_steps_desc'] = "Number of print and dry stations"
        
        self.params['firing_tool_length'] = 7.0
        self.params['firing_tool_length_desc'] = "Distance between firing furnace input and output (meters)"
        self.params['firing_belt_speed'] = 5.0 # 5 is roughly 200 ipm
        self.params['firing_belt_speed_desc'] = "Speed at which all units travel (meters per minute)"
        #self.params['firing_unit_distance'] = 0.2
        #self.params['firing_unit_distance_desc'] = "Minimal distance between wafers (meters)")
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool"
        self.params.update(_params)
        
        #if (self.params['verbose']):               
        #    string = str(self.env.now) + " - [PrintLine][" + self.params['name'] + "] Added a print line"
        #    self.output_text.sig.emit(string)

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represents belts ###
        self.belts = [[0 for col in range(self.params['units_on_belt_input'])] for row in range(self.params['no_print_steps'])]
        #np.zeros((self.params['no_print_steps'],self.params['units_on_belt_input']))
        
        ### Array of zeroes represents dryers ###
        self.dryers = [[0 for col in range(self.params['time_dry'])] for row in range(self.params['no_print_steps'])]
        #np.zeros((self.params['no_print_steps'],self.params['time_dry']))

        ### List represents single lane firing furnace ###
        self.firing_lane = [0] * int(60*self.params['firing_tool_length']//self.params['firing_belt_speed'])
        #np.zeros((1,60*self.params['firing_tool_length']//self.params['firing_belt_speed']))
        
        ### Infinite output container ###
        self.output = InfiniteContainer(self.env,"output")

        self.start_time = []
        self.first_run = []
        self.idle_times_internal = []
        for i in range(self.params['no_print_steps']+1): # plus one for the firing furnace
            self.idle_times_internal.append(0)
            self.first_run.append(True)
            self.start_time.append(0)

        self.next_step = self.env.event() # triggers load-in from cassette

        for i in range(self.params['no_print_steps']):
            self.env.process(self.run_printer(i))
            self.env.process(self.run_dryer_load_out(i))

        self.env.process(self.run_belt())
        self.env.process(self.run_dryers())        
        self.env.process(self.run_firing_lane())
        self.env.process(self.run_firing_load_out())

    def report(self):
        #string = "[PrintLine][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)
        #self.output_text.sig.emit(string)
        
        self.utilization.append("PrintLine")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.output.container.level
        production_hours = (self.env.now - self.start_time[0])/3600
        self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        
        for i in range(len(self.idle_times_internal)):
            if self.first_run[i]:
                idle_time = 100.0
            else:
                idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time[i])
            self.utilization.append(["p" + str(i),round(idle_time,1)])
        
        self.utilization[len(self.utilization)-1][0] = "f0"

    def run_belt(self): # For first belt      
        while True:
            yield self.next_step

            yield self.input.container.get(1)
            yield self.env.timeout(self.params['time_cassette_to_belt']) 
            self.belts[0][0] = 1
                                                 
            #if (self.params['verbose']):
            #    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Put wafer from cassette on belt"
            #    self.output_text.sig.emit(string)
           
    def run_printer(self, num):        
        while True:
            if num > 0:
                input_check = False
            else:
                input_check = (self.input.container.level > 0)
            
            if (self.belts[num][-1] > 0):
                # if last belt position contains a wafer, start printing
            
                if self.first_run[num]:
                    self.start_time[num] = self.env.now
                    self.first_run[num] = False            
            
                # remove wafer from belt
                self.belts[num][-1] = 0

                # move belt and try to load new wafer
                self.belts[num].pop() #= np.roll(self.belts[num],1)                
                self.belts[num].insert(0,0)
                
                if input_check:
                    yield self.next_step.succeed()               
                    self.next_step = self.env.event()
                
                # perform print
                time_out = []
                time_out.append(self.params['time_print'])
                time_out.append(self.params['time_step'])
                yield self.env.timeout(max(time_out))
                
                #if (self.params['verbose']):
                #    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Printed a wafer on printer " + str(num)
                #    self.output_text.sig.emit(string)

                # place wafer in dryer after printing                    
                self.dryers[num][0] = 1

            elif input_check:
                # if cannot print but there are wafers available in input or on belt

                self.belts[num].pop() #= np.roll(self.belts[num],1)                
                self.belts[num].insert(0,0)
                
                yield self.next_step.succeed()
                self.next_step = self.env.event() # make new event

                time_out = []
                time_out.append(self.params['time_cassette_to_belt'])
                time_out.append(self.params['time_step'])
                yield self.env.timeout(max(time_out))                                                              

                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.params['time_step']               

            elif (sum(self.belts[num]) > 0):
                
                self.belts[num].pop() #= np.roll(self.belts[num],1)                
                self.belts[num].insert(0,0)
                
                yield self.env.timeout(self.params['time_step'])                                

                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.params['time_step']
                
            else:
                # if cannot print and no wafers available
                yield self.env.timeout(self.params['time_step'])
                
                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.params['time_step']

    def run_dryers(self):
        # Updates drying time for all wafers in dryers
        while True:
            for i in range(0,self.params['no_print_steps']):
                self.dryers[i].pop()               
                self.dryers[i].insert(0,0)
                
            yield self.env.timeout(1.0)              

    def run_dryer_load_out(self,num):
        # Places wafers into output when they have reached drying time
        while True:
            if self.dryers[num][-1] > 0:
                self.dryers[num][-1] = 0

                if (num < (self.params['no_print_steps']-1)):
                    #go to next printer
                    self.belts[num+1][0] = 1
                else:
                    # go to firing furnace
                    self.firing_lane[0] = 1 #[0][0] = 1

                    if self.first_run[num+1]:
                        self.start_time[num+1] = self.env.now
                        self.first_run[num+1] = False
                        
                #if (self.params['verbose']):
                #    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Dried a wafer on dryer " + str(num)
                #    self.output_text.sig.emit(string)                        

            yield self.env.timeout(1.0)

    def run_firing_lane(self):
        # Updates position for all wafers in firing lane
        while True:                    
            self.firing_lane.pop()                
            self.firing_lane.insert(0,0)            
            #self.firing_lane = np.roll(self.firing_lane,1)
            yield self.env.timeout(1.0)  

    def run_firing_load_out(self):
        # Places wafers into output when they have reached tool length
        while True:            
            if self.firing_lane[-1]: #[0][-1]:        
                self.firing_lane[-1] = 0 #[0][-1] = 0
                yield self.output.container.put(1)
                
                #if (self.params['verbose']):
                #    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Fired a wafer"
                #    self.output_text.sig.emit(string)   
            else:
                if not self.first_run[self.params['no_print_steps']]:
                    self.idle_times_internal[self.params['no_print_steps']] += 1.0
                
            yield self.env.timeout(1.0)       

    def nominal_throughput(self):
        return 3600/self.params['time_print']
            
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)