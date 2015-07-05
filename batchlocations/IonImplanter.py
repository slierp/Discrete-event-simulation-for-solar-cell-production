# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.BatchProcess import BatchProcess
import collections


"""

    Input buffer - tuneable size but default 8 cassettes
    Loadlocks - tuneable capacity, default is 2 cassettes each
    Belts
    Output buffer - the same size as the input buffer
    One set of automation moves cassettes between the buffers and the loadlocks.
    Another set of automation puts and removes wafers from the belt (this probably doesn't exist in the real tool)

"""

class IonImplanter(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):    
        QtCore.QObject.__init__(self)
     
        self.env = _env
        self.output_text = _output
        self.utilization = []       
        
        self.params = {}
        self.params['specification'] = "IonImplanter consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- A number of loadlocks\n"
        self.params['specification'] += "- A number of process lanes\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "Cassettes are loaded into the loadlocks, which are "
        self.params['specification'] += "then held for a set time (for evacuation). Subsequently, the "
        self.params['specification'] += "wafers are processed on belts and enter into buffer cassettes. "
        self.params['specification'] += "When the buffer cassette is full, the wafers return on the same belt "
        self.params['specification'] += "to the loadlock. After a set time (for repressurization) the cassettes "
        self.params['specification'] += "are placed in the output buffer.\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There is a downtime procedure defined for the whole tool, during which "
        self.params['specification'] += "maintenance is performed."

        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual tool"
        self.params['loadlock_capacity'] = 2
        self.params['loadlock_capacity_desc'] = "Number of cassettes per loadlock"   
        self.params['no_of_loadlocks'] = 2
        self.params['no_of_loadlocks_desc'] = "Number of loadlocks"
        self.params['process_time'] = 20*60
        self.params['process_time_desc'] = "Process time including evacuation (seconds)"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 5
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"        
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)         
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.first_run = True
        self.process_counter = 0      
        
#        #if (self.params['verbose']): #DEBUG
#        #    string = str(self.env.now) + " [SingleSideEtch][" + self.params['name'] + "] Added a single side etch" #DEBUG
#        #    self.output_text.sig.emit(string) #DEBUG
        
        ### Input buffer ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ## Load locks ##
        self.batchprocesses = []
        for i in range(0,self.params['loadlock_capacity']):
            process_params = {}
            process_params['name'] = "i" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['process_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))       

        ### Array of zeroes represents lanes ###
        self.lanes = []
        for i in  range(self.params['no_of_lanes']):            
            self.lanes.append(collections.deque([False for rows in range(self.params['tool_length']//self.params['unit_distance'])]))        
        #self.lanes = [[0 for col in range(self.params['tool_length']//self.params['unit_distance'])] for row in range(self.params['no_of_lanes'])]

        ### Output buffer ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])
        
        self.idle_times_internal = {}
        
        for i in range(self.params['no_of_lanes']):
            self.env.process(self.run_lane_load_in(i))
            self.idle_times_internal[i] = 0

        self.env.process(self.run_lanes())
        self.env.process(self.run_lane_load_out())

    def report(self):
        #string = "[SingleSideEtch][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        #self.output_text.sig.emit(string)

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
            self.utilization.append(["l" + str(i),round(idle_time,1)])

    def run_loadlock(self, lane_number):
        return

    def run_lane_load_in(self, lane_number):
        # Loads wafers if available
        # Implementation optimized for minimal timeouts
        # All processes timeout with the same duration
    
        while True:
            if (self.params['downtime_volume'] > 0) & (self.process_counter >= self.params['downtime_volume']):
                yield self.env.timeout(self.params['downtime_duration'])
                for i in range(0,self.params['no_of_lanes']):
                    self.idle_times_internal[i] += self.params['downtime_duration']
                self.process_counter = 0
                
#                #if (self.params['verbose']): #DEBUG
#                #    string = str(self.env.now) + " [SingleSideEtch][" + self.params['name'] + "] End downtime" #DEBUG
#                #    self.output_text.sig.emit(string) #DEBUG

            if (self.input.container.level > lane_number):
                # all lanes are started simultaneously, so only continue if there are enough wafers for this particular lane
                if self.first_run:
                    self.start_time = self.env.now
                    self.first_run = False
                
                yield self.input.container.get(1)            
                #self.env.process(self.run_wafer_instance())
                self.lanes[lane_number][0] = 1
                self.process_counter += 1               
                
#                #if self.params['verbose']: #DEBUG
#                #    if ((self.process_counter % self.params['cassette_size']) == 0):   #DEBUG          
#                #        string = str(around(self.env.now,1)) + " [SingleSideEtch][" + self.params['name'] + "] " #DEBUG
#                #        string += "Loaded " + str(self.params['cassette_size']) + " units in lane " + str(lane_number) #DEBUG
#                #        self.output_text.sig.emit(string) #DEBUG
                        
            elif not self.first_run:
                # start counting down-time after first run
                self.idle_times_internal[lane_number] += 60*self.params['unit_distance']/self.params['belt_speed']
                        
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def run_lanes(self):
        while True:
            self.lanes.pop() #= np.roll(self.lanes,1)
            self.lanes.insert(0,0)
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def run_lane_load_out(self):
        while True:
            for i in range(0,self.params['no_of_lanes']):
                if self.lanes[i][-1] == 1:
                    self.lanes[i][-1] = 0
                    yield self.output.container.put(1)
                    self.transport_counter += 1
                    
            yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed'])

    def nominal_throughput(self):       
        return self.params['no_of_lanes']*60*self.params['belt_speed']/self.params['unit_distance']