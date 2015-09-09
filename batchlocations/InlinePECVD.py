# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import collections

"""

No separate versions implemented for different applications
Single ARC / double-sided nitride / AlOx plus double-sided nitride can be simulated using a longer process chamber length
However, AlOx strictly speaking requires an additional loadlock for gas separation

TODO
Finish utilization implementation > how to define idle time?

"""

class InlinePECVD(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []         
        self.diagram = """blockdiag {      
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';
                       default_group_color = none               
                       A [label = "Input"];
                       B [label = "Output"];               
                       C [label = "Tray load-in"];
                       D [label = "Tray load-out"];
                       E [label = "Evacuation"];                       
                       F [label = "Process"];
                       G [label = "Venting"];
                       A -> C -> E -> F -> G -> D -> B;
                       F -> G [folded];                       
                       } """
        
        self.params = {}
        self.params['specification'] = "InlinePECVD consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Load-in conveyor\n"
        self.params['specification'] += "- Tray load/unload position\n"
        self.params['specification'] += "- Evacuation chamber\n"
        self.params['specification'] += "- Process chamber (including heat-up/cool-down sections)\n"
        self.params['specification'] += "- Venting chamber\n"       
        self.params['specification'] += "- Load-out conveyor\n"        
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The machine accepts cassettes which are unloaded one wafer at a time onto a belt. "
        self.params['specification'] += "The trays are loaded one belt row at a time and subsequently go through the machine. "
        self.params['specification'] += "After the deposition(s) the trays are returned to the original position. "
        self.params['specification'] += "Wafers are unloaded one row at a time onto the load-out conveyor and then "
        self.params['specification'] += "placed back into cassettes.\n"
        self.params['specification'] += "There is a downtime procedure defined for the whole tool, which is for the "
        self.params['specification'] += "required deposition chamber cleaning procedure.\n"
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and output"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"

        self.params['no_trays'] = 8
        self.params['no_trays_desc'] = "Number of trays that cycle through the system"
        self.params['no_tray_rows'] = 6
        self.params['no_tray_rows_desc'] = "Number of rows in the tray (equal to number of units on conveyors)"
        self.params['no_tray_columns'] = 4
        self.params['no_tray_columns_desc'] = "Number of columns in the tray"
        self.params['tray_load_unload_time'] = 5
        self.params['tray_load_unload_time_desc'] = "Time for loading/unloading one tray row (seconds)"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one unit distance on input/output conveyor (seconds)"
  
        self.params['process_chamber_length'] = 6.0
        self.params['process_chamber_length_desc'] = "Tray transport distance in the process chamber (meters)" 
        self.params['process_chamber_speed'] = 5.0
        self.params['process_chamber_speed_desc'] = "Tray speed in process chamber (meters per minute)" 
        
        self.params['time_loadlock'] = 30
        self.params['time_loadlock_desc'] = "Time for load-in/out and evacuation/venting procedures in both load-locks (seconds)"           

        self.params['tray_return_speed'] = 10.0
        self.params['tray_return_speed_desc'] = "Tray speed during transport back to load-in position (meters per minute)"
        self.params['tray_return_distance'] = 8.0
        self.params['tray_return_distance_desc'] = "Tray transport distance for return to load-in position (meters)"

        self.params['downtime_interval'] = 160
        self.params['downtime_interval_desc'] = "Number of hours before downtime"
        self.params['downtime_duration'] = 8
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (hours)"                
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
        self.start_time = 0
        self.first_run = True        
        self.transport_counter = 0
        
#        if (self.params['verbose']): #DEBUG     
#            string = str(self.env.now) + " - [InlinePECVD][" + self.params['name'] + "] Added an inline PECVD tool" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ### Conveyors ###
        self.input_conveyor = collections.deque([False for rows in range(self.params['no_tray_rows'])])
        self.output_conveyor = collections.deque([False for rows in range(self.params['no_tray_rows'])])
        
        ### Trays ###
        self.tray = []
        self.tray_state = [] # 0 is ready for load-in; 1 is ready for pre-heat; 2 is ready for process; 3 is ready for cool-down; 4 is ready for load-out; 5 is ready for return
        for i in range(self.params['no_trays']):
            self.tray.append(BatchContainer(self.env,"tray" + str(i),self.params['no_tray_rows']*self.params['no_tray_columns'],1))
            self.tray_state.append(0)
        
        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Start processes ###
        self.env.process(self.run_load_in_conveyor())
        self.env.process(self.run_load_out_conveyor())        
        self.env.process(self.run_tray_load_in())
        self.env.process(self.run_tray_load_out())        
        self.env.process(self.run_evacuate_chamber())
        self.env.process(self.run_process_chamber())        
        self.env.process(self.run_venting_chamber())
        self.env.process(self.run_tray_return())

    def report(self):
        string = "[InlinePECVD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)

        self.utilization.append("InlinePECVD")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport_counter
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)            
        
        #if self.first_run:
        #    idle_time = 100.0
        #elif ((self.env.now-self.start_time) > 0):
        #    idle_time = 100.0*self.idle_time_internal/(self.env.now-self.start_time[i])
        #self.utilization.append(["p",round(idle_time,1)])           

    def prod_volume(self):
        return self.transport_counter
        
    def run_load_in_conveyor(self):
        wafer_counter = 0
        restart = True # start with new cassette
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        time_step = self.params['time_step']
        wafer_available = False
        downtime_interval = 3600*self.params['downtime_interval']
        downtime_duration = 3600*self.params['downtime_duration']
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            
            if (not wafer_available): # if we don't already have a wafer in position try to get one
                yield self.input.container.get(1)
                wafer_available = True
                
            if self.first_run:
                self.start_time = self.env.now
                last_downtime = self.env.now
                self.first_run = False

            if (restart):
                #time delay for loading new cassette if input had been completely empty
                yield self.env.timeout(time_new_cassette - time_step)
                restart = False            
            
            if (not self.input_conveyor[0]):                 
                self.input_conveyor[0] = True
                wafer_available = False
                wafer_counter += 1

                if(not self.input_conveyor[-1]):
                    self.input_conveyor.rotate(1)                                
                
#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Put wafer from cassette on load-in conveyor" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                    
            if (wafer_counter == cassette_size):
                # if current cassette is empty then delay to load a new cassette                                   
                wafer_counter = 0                
                restart = True
                
                if ((self.env.now - last_downtime) >= downtime_interval): # stop load-in during downtime
                    yield self.env.timeout(downtime_duration)
                    last_downtime = self.env.now

#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] End downtime" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG                    
                
            yield self.env.timeout(time_step)                

    def run_tray_load_in(self):
        current_tray = 0
        no_trays = self.params['no_trays']       
        no_tray_rows = self.params['no_tray_rows']
        no_tray_columns = self.params['no_tray_columns']
        tray_load_unload_time = self.params['tray_load_unload_time']

        while True:

            if self.tray_state[current_tray]: # wait until tray is ready for load-in (state 0)
                yield self.env.timeout(1)
                continue

            with self.tray[current_tray].oper_resource.request() as request:
                yield request
                
                for i in range(no_tray_columns):                    
                    while True:
                        if(self.input_conveyor[-1]): # if input belt is full
                            for i in range(no_tray_rows):
                                self.input_conveyor[i] = False
                                
                            yield self.env.timeout(tray_load_unload_time)
                            yield self.tray[current_tray].container.put(no_tray_rows)
                            break
                        else:
                            yield self.env.timeout(1)

#            if self.params['verbose']: #DEBUG
#                string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Tray " + str(current_tray) + " fully loaded with " + str(self.trays[current_tray].container.level) + " wafers" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

            self.tray_state[current_tray] += 1
            
            current_tray += 1
            
            if (current_tray == no_trays):
                current_tray = 0
                
    def run_evacuate_chamber(self):
        current_tray = 0
        no_trays = self.params['no_trays']
        time_loadlock = self.params['time_loadlock']

        while True:
            
            if not self.tray_state[current_tray] == 1: # wait until tray is ready for evacuation (state 1)
                yield self.env.timeout(1)
                continue            

            with self.tray[current_tray].oper_resource.request() as request:
                yield request
                yield self.env.timeout(time_loadlock)
            
            self.tray_state[current_tray] += 1
            
            current_tray += 1
            
            if (current_tray == no_trays):
                current_tray = 0            

    def run_process_chamber(self):
        current_tray = 0
        no_trays = self.params['no_trays']
        time_process = 60*self.params['process_chamber_length']/self.params['process_chamber_speed']

        while True:        
            if not self.tray_state[current_tray] == 2: # wait until tray is ready for process (state 2)
                yield self.env.timeout(1)
                continue            

            self.env.process(self.run_process(current_tray,time_process)) # use separate process to enable multiple trays
            
            current_tray += 1
            
            if (current_tray == no_trays):
                current_tray = 0 

    def run_process(self,current_tray,time_process):
        
        with self.tray[current_tray].oper_resource.request() as request:            
            yield request
            yield self.env.timeout(time_process)
        
        self.tray_state[current_tray] += 1
        
    def run_venting_chamber(self):
        current_tray = 0
        no_trays = self.params['no_trays']
        time_loadlock = self.params['time_loadlock']

        while True:        
            if not self.tray_state[current_tray] == 3: # wait until tray is ready for venting (state 3)
                yield self.env.timeout(1)
                continue            

            with self.tray[current_tray].oper_resource.request() as request:
                yield request
                yield self.env.timeout(time_loadlock)
            
            self.tray_state[current_tray] += 1         
            
            current_tray += 1
            
            if (current_tray == no_trays):
                current_tray = 0

    def run_tray_load_out(self):
        current_tray = 0
        no_trays = self.params['no_trays']                
        no_tray_rows = self.params['no_tray_rows']
        no_tray_columns = self.params['no_tray_columns']
        tray_load_unload_time = self.params['tray_load_unload_time']        

        while True:
            
            if not self.tray_state[current_tray] == 4: # wait until tray is ready for unloading (state 4)
                yield self.env.timeout(1)
                continue

            with self.tray[current_tray].oper_resource.request() as request:
                yield request
                
                for i in range(no_tray_columns):
                    
                    yield self.tray[current_tray].container.get(no_tray_rows)
                    yield self.env.timeout(tray_load_unload_time)
                    
                    while True:
                        if(not self.output_conveyor.count(True)): # if output belt is empty place wafers
                            for i in range(no_tray_rows):
                                self.output_conveyor[i] = True
                            break
                        else:
                            yield self.env.timeout(1)

#            if self.params['verbose']: #DEBUG
#                string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Tray " + str(current_tray) + " fully unloaded" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

            self.tray_state[current_tray] += 1        
                
            current_tray += 1

            if (current_tray == no_trays):
                current_tray = 0            

    def run_tray_return(self):

        current_tray = 0
        no_trays = self.params['no_trays']
        time_return = 60*self.params['tray_return_distance']/self.params['tray_return_speed']

        while True:        
            if not self.tray_state[current_tray] == 5: # wait until tray is ready for return (state 5)
                yield self.env.timeout(1)
                continue            

            self.env.process(self.run_return(current_tray,time_return)) # use separate process to enable multiple trays
            
            current_tray += 1
            
            if (current_tray == no_trays):
                current_tray = 0           

    def run_return(self,current_tray,time_return):
        
        with self.tray[current_tray].oper_resource.request() as request:            
            yield request
            yield self.env.timeout(time_return)
        
        self.tray_state[current_tray] = 0
            
    def run_load_out_conveyor(self):
        wafer_counter = 0
        restart = True # start with new cassette
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        time_step = self.params['time_step']
        
        while True:            

            if (restart):
                # time delay for loading new cassette if output cassette had been full
                yield self.env.timeout(time_new_cassette - time_step)
                restart = False 
            
            if (self.output_conveyor[0]): 
                self.output_conveyor[0] = False               
                yield self.output.container.put(1)
                self.output_conveyor.rotate(-1)
                                
                wafer_counter += 1

#                if self.params['verbose']: #DEBUG
#                    string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Put wafer from load-out conveyor into cassette" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG                
                
            else:               
                self.output_conveyor.rotate(-1)                                              
                    
            if (wafer_counter == cassette_size):
                # if current cassette is full then delay to load a new cassette
                self.transport_counter += cassette_size
                wafer_counter = 0                
                restart = True                            

            yield self.env.timeout(time_step)
            
    def nominal_throughput(self):
        tray_content = self.params['no_tray_rows']*self.params['no_tray_columns']      
        process_time = 60*self.params['process_chamber_length']/(self.params['no_trays']*self.params['process_chamber_speed'])

        throughputs = []        
        throughputs.append(tray_content*3600/process_time)
        throughputs.append(tray_content*3600/self.params['time_loadlock'])
        return min(throughputs)        