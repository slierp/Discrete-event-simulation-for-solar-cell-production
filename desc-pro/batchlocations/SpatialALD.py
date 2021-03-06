# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
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
        
        self.params['specification'] = """
<h3>General description</h3>
A spatial ALD is used to deposit dielectric layers on wafers in order to improve the surface passivation.
The machine accepts cassettes which are unloaded one wafer at a time.
Each wafer travels on the main conveyor to a number of depositions units.
The deposition units consist of a pre-heating and a deposition chamber and each unit also has a small input and output conveyor next to it.
After the process the wafers travel via the output conveyor onto the main conveyor and then move to the output.
If there are not enough positions available at the output, the machine will pause the wafer to main conveyor automation.
\n
<h3>Description of the algorithm</h3>
There are five types of loops that define the tool operation:
<ol>
<li>Transport of wafers from the input onto the main conveyor</li>
<li>Movement of the main conveyor and tool load-out</li>
<li>Loops that run input and output conveyor of deposition units</li>
<li>Loops that run pre-heating chambers</li>
<li>Loops that run deposition chambers</li>
</ol>
In loop 1 there are two steps:
<ol>
<li>Pick up a wafer from input if not already available</li>
<li>If space available at the input of a deposition unit and at the tool output, place a wafer on the conveyor.
The wafer is marked so that it will be picked up by the intended unit.
To distribute wafers evenly, once a wafer has been placed and assigned to a unit, the next unit will receive priority to receive a wafer.</li>
</ol>
<p>Loop 2 contains only one step. The conveyor is moved forward one position and if the last position contains a wafer it is placed into the output.</p>
Loop 3 is performed for each deposition unit and consists of four steps:
<ol>
<li>If last position on the input conveyor is empty, move the conveyor forward by one position</li>
<li>If the input position on the main conveyor for this unit contains a wafer destined for this unit, place it on the input conveyor</li>
<li>If last position on the output conveyor is empty, move the conveyor forward by one position</li>
<li>If last position on the output conveyor is not empty, place the wafer onto the main conveyor</li>
</ol>
<p>Loop 4 consists of one step: If input conveyor contains a wafer and there is room available in the pre-heat chamber, take the wafer and keep it for a set time to simulate a pre-heating process.</p>
<p>Loop 5 is similar to loop 4 in that it checks whether a wafer is available in the pre-heat chamber and if so, takes it for set period to simulate a deposition process.
After the process the wafer is placed on the output conveyor of the deposition unit.</p>
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "SpatialALD"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and output"
        self.params['max_cassette_no_type'] = "configuration"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"
        self.params['time_new_cassette_type'] = "automation"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one unit distance on main conveyor (seconds)"
        self.params['time_step_type'] = "automation"
        self.params['time_preheat'] = 3.0
        self.params['time_preheat_desc'] = "Time to preheat one wafer before deposition (seconds)"        
        self.params['time_preheat_type'] = "process"
        self.params['time_process'] = 5.0
        self.params['time_process_desc'] = "Time for one deposition process on one wafer (seconds)"
        self.params['time_process_type'] = "process"
        
        self.params['no_deposition_units'] = 3
        self.params['no_deposition_units_desc'] = "Number of deposition units along the main conveyor"
        self.params['no_deposition_units_type'] = "configuration"
        self.params['deposition_unit_length'] = 1.0
        self.params['deposition_unit_length_desc'] = "Distance between input and output position on main conveyor (meters)"
        self.params['deposition_unit_length_type'] = "configuration"

        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers on belts (meters)"
        self.params['unit_distance_type'] = "configuration"
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)

        if self.params['cassette_size'] == -1:
            self.params['cassette_size'] = 100
        
        self.time_step = self.params['time_step']

        ### Give warning for collisons ###
#        if (not (self.output_text == None)) and (self.params['time_step'] > self.params['time_process']):
#           string = str(self.env.now) + " - [" + self.params['type'] + "][" + self.params['name'] + "]  <span style=\"color: red\">WARNING: Wafer collisions are likely with present settings</span>"
#           self.output_text.sig.emit(string)

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Array of zeroes represent main conveyor ###
        # one empty position before and after the depositions units
        # zero denotes empty position; positive value indicates which deposition unit it is intended for (number 1 being the first)
        self.units_on_conveyor = 2+int(self.params['no_deposition_units']*self.params['deposition_unit_length']//self.params['unit_distance'])
        self.conveyor =  collections.deque([0 for rows in range(self.units_on_conveyor)])
        self.transport_counter = 0
        
        ### Keep track of number of wafers in system ###
        self.wafers_in_system = 0        
        
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

        self.maintenance_needed = False

        ### Start SimPy processes ###
        self.env.process(self.run_conveyor())      
        self.env.process(self.run_load_in())
        
        for i in range(self.params['no_deposition_units']):
            self.env.process(self.run_buffer_load_in_out(i))
            self.env.process(self.run_preheater(i))
            self.env.process(self.run_deposition_unit(i))

    def report(self):     
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport_counter
        production_hours = (self.env.now - self.start_time[0])/3600
        
        if (self.nominal_throughput() > 0) and (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)            

        self.utilization.append(self.transport_counter)
        
        for i in range(len(self.idle_times_internal)):
            if self.first_run[i]:
                idle_time = 0
            elif ((self.env.now-self.start_time[i]) > 0):
                idle_time = 100-100*self.idle_times_internal[i]/(self.env.now-self.start_time[i])
            self.utilization.append(["Unit " + str(i),round(idle_time,1)])         

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
                
                if (self.input_buffers[p].count(0) > self.wafers_sent[p]) and (self.output.space_available(self.wafers_in_system+1)): # only insert wafer if there is room in the output
                    self.conveyor[0] = p+1 # number indicates which DU it is intended for
                    wafer_ready = False # need new wafer
                    self.wafers_sent[p] += 1 # keep track of what is on the conveyor
                    self.wafers_in_system += 1 # keep track of total wafer number in system
                    
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
                self.wafers_in_system -= 1 # keep track of total wafer number in system
            
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
            
            if (self.input_buffers[num][-1] > 0) and (self.dep_unit[num][0] == 0):                
                # preheat wafer if wafer and room available                
                
                self.input_buffers[num][-1] = 0
                yield self.env.timeout(self.time_step)                
                yield self.env.timeout(time_preheat)                    
                self.dep_unit[num][0] = num+1

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [" + self.params['type'] + "][" + self.params['name'] + "][du" + str(num) + "] Preheated one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                
            else:
                yield self.env.timeout(self.time_step)

    def run_deposition_unit(self,num):

        time_process = self.params['time_process']
        
        while True:                

            if self.first_run[num]:
                self.start_time[num] = self.env.now
                self.first_run[num] = False  
            
            if (self.dep_unit[num][0] > 0) and (self.dep_unit[num][-1] == 0):                
                # perform deposition if wafer and room is available
            
                self.dep_unit[num].rotate(1)
                yield self.env.timeout(self.time_step)
                yield self.env.timeout(time_process)                    
                self.output_buffers[num][0] = num+1
                self.dep_unit[num][-1] = 0

#                if (self.params['verbose']): #DEBUG     
#                    string = str(self.env.now) + " - [" + self.params['type'] + "][" + self.params['name'] + "][du" + str(num) + "] Processed one wafer" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                
            else:
                yield self.env.timeout(self.time_step)
                
                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.time_step                
    
    def nominal_throughput(self):

        return self.params['no_deposition_units']*3600/(self.params['time_process']+self.params['time_step'])