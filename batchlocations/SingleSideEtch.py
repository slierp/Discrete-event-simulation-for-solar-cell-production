# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import collections

class SingleSideEtch(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []       
        
        self.params = {}
        self.params['specification'] = "SingleSideEtch consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- A number of process lanes\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "Each lane runs independently and continuously, "
        self.params['specification'] += "but can only accept a new unit after a certain time interval. "
        self.params['specification'] += "Because it runs continuously "
        self.params['specification'] += "(independent of whether there is an output position available or not) "
        self.params['specification'] += "the output automation cannot function as a master of the input.\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There are several of types of automation. "
        self.params['specification'] += "Assumed now is that each lane is fed separately with new wafers, "
        self.params['specification'] += "with no interruption between cassettes (i.e. cassettes stacked on top of each other).\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There is a downtime procedure defined for the whole tool, during which the "
        self.params['specification'] += "etching solution is replaced."

        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['no_of_lanes'] = 5
        self.params['no_of_lanes_desc'] = "Number of process lanes"
        self.params['tool_length'] = 10
        self.params['tool_length_desc'] = "Distance between input and output (meters)"
        self.params['belt_speed'] = 1.8
        self.params['belt_speed_desc'] = "Speed at which all units travel (meters per minute)"
        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers (meters)"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        
        self.params['downtime_volume'] = 100000
        self.params['downtime_volume_desc'] = "Number of entered wafers before downtime"
        self.params['downtime_duration'] = 60*60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (seconds)"
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)         
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.first_run = True
        self.process_counter = 0      
        
#        if (self.params['verbose']): #DEBUG
#            string = str(int(self.env.now)) + " [SingleSideEtch][" + self.params['name'] + "] Added a single side etch" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represents lanes ###
        self.lanes = []
        for i in  range(self.params['no_of_lanes']):            
            self.lanes.append(collections.deque([False for rows in range(int(self.params['tool_length']//self.params['unit_distance']))]))            

        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])
        
        self.idle_times_internal = {}
        
        for i in range(self.params['no_of_lanes']):
            self.env.process(self.run_lane_load_in(i))
            self.idle_times_internal[i] = 0

        self.env.process(self.run_lanes())
        self.env.process(self.run_lane_load_out())

    def report(self):
        string = "[SingleSideEtch][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)

        self.utilization.append("SingleSideEtch")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport_counter - self.output.container.level
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            self.utilization.append(100*(production_volume/production_hours)/self.nominal_throughput())               
        else:
            self.utilization.append(0)            

        for i in range(len(self.idle_times_internal)):
            if self.first_run:
                idle_time = 100.0
            else:
                idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time)
            self.utilization.append(["l" + str(i),round(idle_time,1)])

    def prod_volume(self):
        return self.transport_counter

    def run_lane_load_in(self, lane_number):
        # Loads wafers if available
        # Implementation optimized for minimal timeouts
        # All processes timeout with the same duration
        downtime_volume = self.params['downtime_volume']
        downtime_duration = self.params['downtime_duration']
        no_of_lanes = self.params['no_of_lanes']
        time_step = 60*self.params['unit_distance']/self.params['belt_speed']
#        verbose = self.params['verbose'] #DEBUG
    
        while True:
            if (downtime_volume > 0) & (self.process_counter >= downtime_volume):
                yield self.env.timeout(downtime_duration)
                for i in range(0,no_of_lanes):
                    self.idle_times_internal[i] += downtime_duration
                self.process_counter = 0
                
#                if (verbose): #DEBUG
#                    string = str(int(self.env.now)) + " [SingleSideEtch][" + self.params['name'] + "][" + str(lane_number) + "] End downtime" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG

            if (self.input.container.level > lane_number):
                # all lanes are started simultaneously, so only continue if there are enough wafers for this particular lane
                if self.first_run:
                    self.start_time = self.env.now
                    self.first_run = False
                
                yield self.input.container.get(1)            
                #self.env.process(self.run_wafer_instance())
                self.lanes[lane_number][0] = True
                self.process_counter += 1               
                
#                #if (verbose): #DEBUG
#                #    if ((self.process_counter % self.params['cassette_size']) == 0): #DEBUG      
#                #        string = str(round(self.env.now,1)) + " [SingleSideEtch][" + self.params['name'] + "] " #DEBUG
#                #        string += "Loaded " + str(self.params['cassette_size']) + " units in lane " + str(lane_number) #DEBUG
#                #        self.output_text.sig.emit(string) #DEBUG
                        
            elif not self.first_run:
                # start counting down-time after first run
                self.idle_times_internal[lane_number] += time_step
                        
            yield self.env.timeout(time_step)

    def run_lanes(self):
        no_of_lanes = self.params['no_of_lanes']
        time_step = 60*self.params['unit_distance']/self.params['belt_speed']
        
        while True:
            for i in range(0,no_of_lanes):
                self.lanes[i].rotate(1)
            yield self.env.timeout(time_step)

    def run_lane_load_out(self):
        no_of_lanes = self.params['no_of_lanes']
        time_step = 60*self.params['unit_distance']/self.params['belt_speed']
        
        while True:
            for i in range(0,no_of_lanes):
                if self.lanes[i][-1]:
                    self.lanes[i][-1] = False
                    yield self.output.container.put(1)
                    self.transport_counter += 1
                    
            yield self.env.timeout(time_step)

    def nominal_throughput(self):       
        return self.params['no_of_lanes']*60*self.params['belt_speed']/self.params['unit_distance']