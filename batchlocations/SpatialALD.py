# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import collections

"""
TODO

Fix lockup problem with more than few tens of wafers
Implement downtime
Implement cassette reload timeout

"""

class SpatialALD(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []
        
        self.params = {}
        self.params['specification'] = "DO NOT USE\n"
        self.params['specification'] += "SpatialALD consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Main conveyor\n"
        self.params['specification'] += "- Deposition units with small input and output buffers\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The machine accepts cassettes which are unloaded one wafer at a time. "
        self.params['specification'] += "Each wafer travels on the main conveyor to a number of depositions units. "
        self.params['specification'] += "After the process the wafers are placed back on the conveyor "
        self.params['specification'] += "and travel to the output."
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and output"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one unit distance on main conveyor (seconds)"
        self.params['time_process'] = 5.0
        self.params['time_process_desc'] = "Time to process one wafer including pre-heating (seconds)"
        
        self.params['no_deposition_units'] = 3
        self.params['no_deposition_units_desc'] = "Number of deposition units along the main conveyor"
        self.params['deposition_unit_length'] = 1.0
        self.params['deposition_unit_length_desc'] = "Distance between input and output position on main conveyor (meters)"        
        self.params['deposition_buffer_size'] = 3
        self.params['deposition_buffer_size_desc'] = "Number of units in each deposition unit input buffer"    

        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers on belts (meters)"        
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
        self.time_step = self.params['time_step']
        
#        if (self.params['verbose']): #DEBUG     
#            string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "] Added a spatial ALD tool" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represent main conveyor ###
        # one empty position before and after the depositions units
        # zero denotes empty position; positive value indicates which deposition unit it is intended for (number 1 being the first)
        self.units_on_conveyor = 2+int(self.params['no_deposition_units']*self.params['deposition_unit_length']//self.params['unit_distance'])
        self.conveyor =  collections.deque([0 for rows in range(self.units_on_conveyor)])
        
        ### Calculate input/output positions for each deposition unit ###

        self.dep_input_positions = []
        self.dep_output_positions = []
        
        for i in range(self.params['no_deposition_units']):
            self.dep_input_positions.append(1 + i*int(self.params['deposition_unit_length']//self.params['unit_distance']))
            
        for i in self.dep_input_positions:
            self.dep_output_positions.append(1 + i + int(self.params['deposition_unit_length']//self.params['unit_distance']))        
        
        ### Lists for keeping check of wafers in depostion unit buffers ###
        
        self.input_buffers = []
        self.output_buffers = []
        
        for i in range(self.params['no_deposition_units']):
            self.input_buffers.append(collections.deque([0 for rows in range(self.params['deposition_buffer_size'])]))
            self.output_buffers.append(collections.deque([0 for rows in range(self.params['deposition_buffer_size'])]))
        
        ### Request list for wafers by deposition units ###
        
        self.request_list = [False for rows in range(self.params['no_deposition_units'])]
        
        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        self.env.process(self.run_conveyor())      
        self.env.process(self.run_load_in())
        
        for i in range(self.params['no_deposition_units']):
            self.env.process(self.run_buffer_load_in_out(i))
            self.env.process(self.run_deposition_unit(i)) # count starts at 1 in this case

    def report(self):
        string = "[SpatialALD][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)
        self.output_text.sig.emit(string)        

    def prod_volume(self):
        return self.output.container.level
    
    def run_load_in(self):
        no_deposition_units = self.params['no_deposition_units']
        preference_list = collections.deque([False for rows in range(self.params['no_deposition_units'])])
        preference_list[0] = True
        
        while True:                       
            
            if (not self.conveyor[0]):

                yield self.input.container.get(1)
               
                while True:
                    preferred = 0
                    for i in range(len(preference_list)):
                        if preference_list[i]:
                            preferred = i
                    
                    # spread wafers evenly over the deposition units
                    if self.request_list[preferred]:
                        self.conveyor[0] = preferred+1 # number indicates which DU it is intended for
                        self.request_list[preferred] = False # request granted so need to place new request
                        preference_list.rotate(1) # following DU will preferably get next wafer

#                        if (self.params['verbose']): #DEBUG     
#                            string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "] Placed wafer on conveyor belt" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG                        
                        
                        break
                    else:
                        preference_list.rotate(1)
                        
            yield self.env.timeout(self.time_step)
    
    def run_conveyor(self):
        
        while True:                
                    
            self.conveyor.rotate(1)

            if (self.conveyor[-1] > 0):
                # automatically performs load-out
                self.conveyor[-1] = 0
                yield self.output.container.put(1)
            
            yield self.env.timeout(self.time_step)

    def run_buffer_load_in_out(self,num):
        
        input_pos = self.dep_input_positions[num]
        output_pos = self.dep_output_positions[num]
        
        while True:
            
            if (self.input_buffers[num][-1] == 0):
                # move wafers forward towards deposition unit
                self.input_buffers[num].rotate(1)

            if (self.conveyor[input_pos] == (num+1)):
                # get wafers intended for this deposition unit
                self.conveyor[input_pos] = 0
                self.input_buffers[num][0] = num+1

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "][du" + str(num) + "] Received one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG                
                
            elif (self.input_buffers[num][0] == 0):
                self.request_list[num] = True

            if (self.output_buffers[num][-1] == 0):
                self.output_buffers[num].rotate(1)
            else:                            
                # put processed wafers back onto main conveyor
                if (self.conveyor[output_pos] == 0):
                    self.conveyor[output_pos] = num+1
                    self.output_buffers[num][-1] = 0
            
            yield self.env.timeout(self.time_step)        

    def run_deposition_unit(self,num):

        time_process = self.params['time_process']
        
        while True:
            
            if (self.input_buffers[num][-1] > 0):
                # process wafer if available                
                self.input_buffers[num][-1] = 0
                yield self.env.timeout(time_process)
                self.output_buffers[num][0] = num+1

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "][du" + str(num) + "] Processed one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                
            else:
                yield self.env.timeout(self.time_step)
    
    def nominal_throughput(self):

        return self.params['no_deposition_units']*3600/self.params['time_process']