# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import collections

"""
TODO

Implement downtime
Implement cassette reload timeout

"""

class SpatialALD(QtCore.QObject):
        
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
                       B [label = "Main conveyor"];              
                       C [label = "Input buffer"];
                       D [label = "Heat-up"];
                       E [label = "Deposition"];
                       F [label = "Output buffer"];               
                       G [label = "Output"];                
                       A -> B -> C;
                       B -> G;
                       F -> B;
                       C -> D -> E -> F;
                       D -> E [folded];
                       group { C; D; E; F; color = "#CCCCCC";}
                       group { B; G; orientation = portrait; }
            
                       } """       
        
        self.params = {}
        self.params['specification'] = "SpatialALD consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Main conveyor\n"
        self.params['specification'] += "- Deposition units with small input and output buffers\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The machine accepts cassettes which are unloaded one wafer at a time. "
        self.params['specification'] += "Each wafer travels on the main conveyor to a number of depositions units. "
        self.params['specification'] += "After the process the wafers are placed back on the conveyor "
        self.params['specification'] += "and travel to the output.\n"
        
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
        self.params['time_preheat'] = 3.0
        self.params['time_preheat_desc'] = "Time to preheat one wafer before deposition (seconds)"        
        self.params['time_process'] = 5.0
        self.params['time_process_desc'] = "Time for one deposition process on one wafer (seconds)"
        
        self.params['no_deposition_units'] = 3
        self.params['no_deposition_units_desc'] = "Number of deposition units along the main conveyor"
        self.params['deposition_unit_length'] = 1.0
        self.params['deposition_unit_length_desc'] = "Distance between input and output position on main conveyor (meters)"    

        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers on belts (meters)"        
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
        self.time_step = self.params['time_step']
        
#        if (self.params['verbose']): #DEBUG     
#            string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "] Added a spatial ALD tool" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG

        ### Give warning for collisons ###
#        if (self.params['time_step'] > self.params['time_process']):
#            string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "]  <span style=\"color: red\">WARNING: Wafer collisions are likely with present settings</span>"
#            self.output_text.sig.emit(string)

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represent main conveyor ###
        # one empty position before and after the depositions units
        # zero denotes empty position; positive value indicates which deposition unit it is intended for (number 1 being the first)
        self.units_on_conveyor = 2+int(self.params['no_deposition_units']*self.params['deposition_unit_length']//self.params['unit_distance'])
        self.conveyor =  collections.deque([0 for rows in range(self.units_on_conveyor)])
        self.transport_counter = 0
        
        ### Calculate input/output positions for each deposition unit ###

        self.dep_input_positions = []
        self.dep_output_positions = []
        
        for i in range(self.params['no_deposition_units']):
            self.dep_input_positions.append(1 + i*int(self.params['deposition_unit_length']//self.params['unit_distance']))
            
        for i in self.dep_input_positions:
            self.dep_output_positions.append(-1 + i + int(self.params['deposition_unit_length']//self.params['unit_distance']))        
        
        ### Lists representing deposition unit buffers ###
        
        self.input_buffers = []
        self.output_buffers = []
        
        for i in range(self.params['no_deposition_units']):
            self.input_buffers.append(collections.deque([0 for rows in range(2)]))
            self.output_buffers.append(collections.deque([0 for rows in range(2)]))

        ### Lists representing preheater and deposition area within deposition units ###

        self.dep_unit = []
        
        for i in range(self.params['no_deposition_units']):
            self.dep_unit.append(collections.deque([0 for rows in range(2)]))
        
        ### Lists to keep track of wafers on belt ###
        
        self.wafers_sent = [0 for rows in range(self.params['no_deposition_units'])]
        
        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### List for calculating idle times ###
        self.start_time = []
        self.first_run = []
        self.idle_times_internal = []
        for i in range(self.params['no_deposition_units']):
            self.idle_times_internal.append(0)
            self.first_run.append(True)
            self.start_time.append(0)

        ### Start SimPy processes ###
        self.env.process(self.run_conveyor())      
        self.env.process(self.run_load_in())
        
        for i in range(self.params['no_deposition_units']):
            self.env.process(self.run_buffer_load_in_out(i))
            self.env.process(self.run_preheater(i))
            self.env.process(self.run_deposition_unit(i))

    def report(self):
        string = "[SpatialALD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)

        ### Report utilization ###        
        self.utilization.append("SpatialALD")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport_counter
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
            self.utilization.append(["du" + str(i),round(idle_time,1)])         

    def prod_volume(self):
        return self.transport_counter
    
    def run_load_in(self):

        wafer_ready = False
        no_deposition_units = self.params['no_deposition_units']
        priority_list = collections.deque([False for rows in range(no_deposition_units)])
        priority_list[-1] = True
        
        while True:                               
                
            if not wafer_ready:
                yield self.input.container.get(1)
                wafer_ready = True
            
            for i in range(no_deposition_units):

                p = next(j for j, x in enumerate(priority_list) if x) # find current priority in list
                
                if (self.input_buffers[p].count(0) > self.wafers_sent[p]):
                    self.conveyor[0] = p+1 # number indicates which DU it is intended for
                    wafer_ready = False # need new wafer
                    self.wafers_sent[p] += 1 # keep track of what is on the conveyor
                    
#                    if (self.params['verbose']): #DEBUG     
#                        string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "] Placed wafer on conveyor belt for DU " + str(p) #DEBUG
#                        self.output_text.sig.emit(string) #DEBUG                    
                    
                    break
                else:
                    priority_list.rotate(-1) # next deposition unit now has priority            
            
            yield self.env.timeout(self.time_step)
    
    def run_conveyor(self):
        
        while True:                
                    
            self.conveyor.rotate(1)

            if (self.conveyor[-1] > 0):
                # automatically performs load-out
                self.conveyor[-1] = 0
                yield self.output.container.put(1)
                self.transport_counter += 1
            
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
                self.wafers_sent[num] -= 1
                self.input_buffers[num][0] = num+1

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "][du" + str(num) + "] Received one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG

            if (self.output_buffers[num][-1] == 0):
                # move wafers forward towards main conveyor
                self.output_buffers[num].rotate(1)
            else:                            
                # put processed wafers back onto main conveyor
                if (self.conveyor[output_pos] == 0):
                    self.conveyor[output_pos] = num+1
                    self.output_buffers[num][-1] = 0
            
            yield self.env.timeout(self.time_step)        

    def run_preheater(self,num):

        time_preheat = self.params['time_preheat']

        while True:
            
            if (self.input_buffers[num][-1] > 0) & (self.dep_unit[num][0] == 0):                
                # preheat wafer if wafer and room available                
                
                self.input_buffers[num][-1] = 0
                yield self.env.timeout(self.time_step)                
                yield self.env.timeout(time_preheat)                    
                self.dep_unit[num][0] = num+1

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "][du" + str(num) + "] Preheated one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                
            else:
                yield self.env.timeout(self.time_step)

    def run_deposition_unit(self,num):

        time_process = self.params['time_process']
        
        while True:                

            if self.first_run[num]:
                self.start_time[num] = self.env.now
                self.first_run[num] = False  
            
            if (self.dep_unit[num][0] > 0) & (self.dep_unit[num][-1] == 0):                
                # perform deposition if wafer and room is available
            
                self.dep_unit[num].rotate(1)
                yield self.env.timeout(self.time_step)
                yield self.env.timeout(time_process)                    
                self.output_buffers[num][0] = num+1
                self.dep_unit[num][-1] = 0

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [SpatialALD][" + self.params['name'] + "][du" + str(num) + "] Processed one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                
            else:
                yield self.env.timeout(self.time_step)
                
                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.time_step                
    
    def nominal_throughput(self):

        return self.params['no_deposition_units']*3600/(self.params['time_process']+self.params['time_step'])