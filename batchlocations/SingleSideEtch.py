# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 13:55:53 2014

@author: rnaber

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import numpy as np

class SingleSideEtch(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []       
        
        self.params = {}
        self.params['specification'] = self.tr("SingleSideEtch consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- A number of process lanes\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("Each lane runs independently and continuously, ")
        self.params['specification'] += self.tr("but can only accept a new unit after a certain time interval. ")
        self.params['specification'] += self.tr("Because it runs continuously ")
        self.params['specification'] += self.tr("(independent of whether there is an output position available or not) ")
        self.params['specification'] += self.tr("the output automation cannot function as a master of the input.\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There are several of types of automation. ")
        self.params['specification'] += self.tr("Assumed now is that each lane is fed separately with new wafers, ")
        self.params['specification'] += self.tr("with no interruption between cassettes (i.e. cassettes stacked on top of each other).\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There is a downtime procedure defined for the whole tool, during which the ")         
        self.params['specification'] += self.tr("etching solution is replaced.")          

        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['no_of_lanes'] = 5
        self.params['no_of_lanes_desc'] = self.tr("Number of process lanes")
        self.params['tool_length'] = 10
        self.params['tool_length_desc'] = self.tr("Distance between input and output (meters)")
        self.params['belt_speed'] = 1.8
        self.params['belt_speed_desc'] = self.tr("Speed at which all units travel (meters per minute)")
        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = self.tr("Minimal distance between wafers (meters)")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input and the same number at output")
        
        self.params['downtime_volume'] = 100000
        self.params['downtime_volume_desc'] = self.tr("Number of entered wafers before downtime")
        self.params['downtime_duration'] = 60*60
        self.params['downtime_duration_desc'] = self.tr("Time for a single tool downtime cycle (seconds)")
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)         
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.first_run = True
        self.process_counter = 0      
        
        if (self.params['verbose']):
            string = str(self.env.now) + " [SingleSideEtch][" + self.params['name'] + "] Added a single side etch"
            self.output_text.sig.emit(string)
        
        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represents lanes ###
        self.lanes = np.zeros((self.params['no_of_lanes'],self.params['tool_length']//self.params['unit_distance']))

        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])
        
        self.idle_times_internal = {}
        
        for i in np.arange(self.params['no_of_lanes']):
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
        self.utilization.append(100*(production_volume/production_hours)/self.nominal_throughput())               

        for i in range(len(self.idle_times_internal)):
            if self.first_run:
                idle_time = 100.0
            else:
                idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time)
            self.utilization.append(["l" + str(i),np.round(idle_time,1)])

    def run_lane_load_in(self, lane_number):
        # Loads wafers if available
        # Implementation optimized for minimal timeouts
        # All processes timeout with the same duration
    
        while True:
            if (self.params['downtime_volume'] > 0) & (self.process_counter >= self.params['downtime_volume']):
                yield self.env.timeout(self.params['downtime_duration'])
                for i in self.params['no_of_lanes']:
                    self.idle_times_internal[i] += self.params['downtime_duration']
                self.process_counter = 0
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [SingleSideEtch][" + self.params['name'] + "] End downtime"
                    self.output_text.sig.emit(string)

            if (self.input.container.level > lane_number):
                # all lanes are started simultaneously, so only continue if there are enough wafers for this particular lane
                if self.first_run:
                    self.start_time = self.env.now
                    self.first_run = False
                
                yield self.input.container.get(1)            
                #self.env.process(self.run_wafer_instance())
                self.lanes[lane_number][0] = 1
                self.process_counter += 1               
                
                if self.params['verbose']:
                    if ((self.process_counter % self.params['cassette_size']) == 0):            
                        string = str(np.around(self.env.now,1)) + " [SingleSideEtch][" + self.params['name'] + "] "
                        string += "Loaded " + str(self.params['cassette_size']) + " units in lane " + str(lane_number)
                        self.output_text.sig.emit(string)
                        
            elif not self.first_run:
                # start counting down-time after first run
                self.idle_times_internal[lane_number] += 60*self.params['unit_distance']/self.params['belt_speed']
                        
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def run_lanes(self):
        while True:
            self.lanes = np.roll(self.lanes,1)
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def run_lane_load_out(self):
        while True:
            for i in np.arange(0,self.params['no_of_lanes']):
                if self.lanes[i][-1] == 1:
                    self.lanes[i][-1] = 0
                    yield self.output.container.put(1)
                    self.transport_counter += 1
                    
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def nominal_throughput(self):       
        return self.params['no_of_lanes']*60*self.params['belt_speed']/self.params['unit_distance']