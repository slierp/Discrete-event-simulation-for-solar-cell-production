# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchTransport import BatchTransport
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
import collections, simpy

class IonImplanter(QtCore.QObject):
        
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
                       C [label = "Loadlock0"];
                       D [label = "Loadlock1"];
                       E [label = "Process belt0"];                       
                       F [label = "Process belt1"];
                       G [label = "Buffer0"];
                       H [label = "Buffer1"];
                       A -> C;
                       B <- D;
                       C <-> E;
                       E <-> G;
                       F <-> H;
                       group { A; B; }
                       group { C; D; color = "#CCCCCC"}
                       group { E; F; G; H; color = "#CCCCCC"}
                       
                       } """      
        
        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
An ion implanter is used for applying dopant into wafers using an ion beam.
Cassettes are loaded into the loadlocks, which are then held for a set time for evacuation.
Subsequently, the wafers are transported on belts to be exposed to beam and then enter into buffer cassettes.
When the buffer cassette is full, the wafers return on the same belt to the loadlock.
After repressurization the cassettes are placed in the output buffer.
There is a downtime procedure available during to simulate a maintenance procedure.
During this time the wafer load-in is paused.\n
        """

        self.params['name'] = ""
        self.params['type'] = "IonImplanter"        
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        self.params['max_cassette_no_type'] = "configuration"
        
        self.params['transfer0_time'] = 30
        self.params['transfer0_time_desc'] = "Time for single batch transfer from input to loadlock (seconds)"
        self.params['transfer0_time_type'] = "automation"
        self.params['transfer1_time'] = 30
        self.params['transfer1_time_desc'] = "Time for single batch transfer from loadlock to output (seconds)"
        self.params['transfer1_time_type'] = "automation"

        self.params['evacuation_time'] = 240
        self.params['evacuation_time_desc'] = "Time for single loadlock evacuation (seconds)"
        self.params['evacuation_time_type'] = "process"
        self.params['repressurization_time'] = 90
        self.params['repressurization_time_desc'] = "Time for single loadlock repressurization (seconds)"
        self.params['repressurization_time_type'] = "process"

        self.params['implant_belt_speed'] = 10.0
        self.params['implant_belt_speed_desc'] = "Speed at which all units travel (meters per minute)"
        self.params['implant_belt_speed_type'] = "process"
        self.params['implant_belt_length'] = 2.0
        self.params['implant_belt_length_desc'] = "Distance between loadlock and buffer cassette (meters)"
        self.params['implant_belt_length_type'] = "configuration"
        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers (meters)"
        self.params['unit_distance_type'] = "configuration"
        
        self.params['downtime_interval'] = 100
        self.params['downtime_interval_desc'] = "Interval between downtime cycles (hours)"
        self.params['downtime_interval_type'] = "downtime"
        self.params['downtime_duration'] = 60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (minutes)"
        self.params['downtime_duration_type'] = "downtime"

        self.params['mtbf'] = 1000
        self.params['mtbf_desc'] = "Mean time between failures (hours) (0 to disable function)"
        self.params['mtbf_type'] = "downtime"
        self.params['mttr'] = 60
        self.params['mttr_desc'] = "Mean time to repair (minutes) (0 to disable function)"
        self.params['mttr_type'] = "downtime"
        self.params['random_seed'] = 42   
        self.params['random_seed_type'] = "immutable"

        self.params['batch_size'] = 2
        self.params['batch_size_type'] = "immutable"
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)

        if self.params['cassette_size'] == -1:
            self.params['cassette_size'] = 100
        
        ### Input buffer ###
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'],True)
        
        ### Implant lanes ###            
        self.implant_lanes_resource = simpy.Resource(self.env, 1) 
        
        ## Load locks ##
        self.batchprocesses = []
        for i in range(0,2):
            process_params = self.params.copy()
            process_params['name'] = "ll" + str(i)
            self.batchprocesses.append(loadlock(self.env,self.output_text,process_params,self.implant_lanes_resource))

        ### Output buffer ###
        self.output = CassetteContainer(self.env,"output",self.params['max_cassette_no'],True)

        ### Load-in transport ###
        batchconnections = []

        for i in range(0,2):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])

        transport_params = self.params.copy()
        transport_params['name'] = "ii0"
        transport_params['mtbf'] = self.params['mtbf']
        transport_params['mttr'] = self.params['mttr']
        transport_params['random_seed'] = self.params['random_seed']
        self.downtime_finished = None
        self.technician_resource = None
        self.downtime_duration = 0
        self.maintenance_needed = False                          
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params,self)        

        ### Load-out transport ###
        # separate transporter so we can easily count processed wafers
        batchconnections = []
        
        for i in range(0,2):
            batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer1_time']])
        
        transport_params = self.params.copy()
        transport_params['name'] = "ii1"      
        self.transport1 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

    def report(self):
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport1.transport_counter
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
        util = round(100*(production_volume/production_hours)/self.nominal_throughput(),1)
        self.utilization.append(util)
        self.utilization.append(self.transport1.transport_counter)

#        for i in range(0,2):
#            if self.batchprocesses[0].first_run:
#                idle_time = 0
#            else:
#                idle_time = 100-100*self.implant_lanes[i].idle_time/(self.env.now-self.batchprocesses[0].start_time)
#            self.utilization.append(["Lane " + str(i),round(idle_time,1)])

    def prod_volume(self):
        return self.transport1.transport_counter

    def nominal_throughput(self):       
        return int(60*self.params['implant_belt_speed']/self.params['unit_distance'])
        
class loadlock(QtCore.QObject):
    
    def __init__(self,  _env, _output=None, _params = {}, _implant_lanes_resource=None):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output   
        self.params = _params
        self.implant_lanes_resource = _implant_lanes_resource

        self.name = self.params['name'] # needed for BatchTransport
        self.resource = simpy.Resource(self.env, 1) # needed for BatchTransport
        self.process_finished = 0 # needed for BatchTransport
        self.status = 1 # needed for BatchTransport        
        self.start = self.env.event()
        self.implant_process_finished0 = self.env.event()
        self.implant_process_finished1 = self.env.event()
        self.store = simpy.Store(self.env,2)        
        self.first_run = True
        self.start_time = 0
        self.last_downtime = 0

        self.loadlock_container = simpy.Container(self.env,capacity=self.params['cassette_size'],init=self.params['cassette_size'])

        ### Array of zeroes represents lane ###
        no_positions = int(self.params['implant_belt_length']//self.params['unit_distance'])        
        self.lane = collections.deque([False for rows in range(no_positions)])            

        ### Buffer cassette ###
        self.buffer = BatchContainer(self.env,"buffer",self.params['cassette_size'],1)
        
        #string = str(self.env.now) + " - [Loadlock][" + self.params['name'] + "] Added loadlock"
        #self.output_text.sig.emit(string)
            
        self.env.process(self.run())        

    def run(self):
        evacuation_time = int(self.params['evacuation_time'])
        repressurization_time = int(self.params['repressurization_time'])
        time_step = 60*self.params['unit_distance']/self.params['implant_belt_speed']
        
        while True:
            yield self.start            

            if (self.first_run):
                self.start_time = self.env.now
                self.first_run = False
            
            if not self.process_finished:
                with self.resource.request() as request: # reserve access to loadlock
                    yield request

                    #string = str(round(self.env.now,1)) + " [Loadlock][" + self.name + "] Starting new batch "
                    #self.output_text.sig.emit(string)
                                      
                    yield self.env.timeout(evacuation_time)
                    
                    with self.implant_lanes_resource.request() as request_lanes: # reserve access to process lanes
                        yield request_lanes

                        #string = str(round(self.env.now,1)) + " [Loadlock][" + self.name + "] Start implant process "
                        #self.output_text.sig.emit(string)
                        
#                        if (self.first_run):
#                            self.first_run = False
#                        else:
#                            self.idle_time += (self.env.now-self.prev_time)

                        while True: # load wafers on belt and run belt until loadlock and belt is empty
                            if (self.loadlock_container.level > 0) & (not self.lane[0]):
                                self.loadlock_container.get(1)
                                self.lane[0] = True
                            
                            if (self.lane[-1]):
                                self.lane[-1] = False
                                self.buffer.container.put(1)
                            
                            if (self.loadlock_container.level == 0) & (not self.lane.count(True)):
                                break                
                            
                            self.lane.rotate(1)    
                            yield self.env.timeout(time_step)                
                
                        while True: # load wafers on belt and run belt until buffer and lane is empty
                            if (self.buffer.container.level > 0) & (not self.lane[-1]):
                                self.buffer.container.get(1)
                                self.lane[-1] = True
                            
                            if (self.lane[0]):
                                self.lane[0] = False
                                self.loadlock_container.put(1)
            
                            if (self.buffer.container.level == 0) & (not self.lane.count(True)):
                                break  
                            
                            self.lane.rotate(-1)    
                            yield self.env.timeout(time_step)

                        #string = str(round(self.env.now,1)) + " [Loadlock][" + self.name + "] End implant process "
                        #self.output_text.sig.emit(string)
                    
                    yield self.env.timeout(repressurization_time)
                    self.process_finished = 1

                    #string = str(round(self.env.now,1)) + " [Loadlock][" + self.name + "] Finished batch "
                    #self.output_text.sig.emit(string)

    def start_process(self):
        self.start.succeed()
        self.start = self.env.event() # make new event
        
    def space_available(self,_batch_size):
        # see if space is available for the specified _batch_size
        if ((len(self.store.items)+_batch_size) <= self.params['batch_size']):            
            return True
        else:
            return False
            
    def check_downtime(self): # needed for BatchTransport
        return