# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.CassetteContainer import CassetteContainer
import collections, random, simpy

class SingleSideEtch(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = [] 
        self.diagram = """blockdiag {    
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Process lanes", stacked];
                       C [label = "Output"];
                       A -> B -> C;                        
                       } """        
        
        self.params = {}
        
        self.params['specification'] = """
<h3>General description</h3>
A single side etch is used for etching, polishing or texturing wafers.
Each lane runs independently and continuously, but can only accept a new unit after a certain time interval to avoid wafer collisions.
Each lane is fed separately with new wafers with no interruption for exchanging cassettes.
There is a downtime procedure available where the whole tool goes down for a certain period after running a set number of wafers.
Such downtimes are required for exchanging the etching solution.\n
<h3>Description of the algorithm</h3>
There are three types of program loops to run the tool:
<ol>
<li>An independent loop for wafer load-in to each lane.
There is currently no delay for exchanging empty cassettes for full ones.</li>
<li>Wafer transport consists of single process that progresses wafers along all lanes with fixed time increments.
The time increment is determined by the belt speed and unit distance.</li>
<li>Wafer load-out is done with the same time increment and for all lanes at the same time.</li>
</ol>
<p>The downtime procedure pauses the wafer load-in process for a set duration.</p>
\n
        """

        self.params['name'] = ""
        self.params['type'] = "SingleSideEtch"        
        self.params['no_of_lanes'] = 5
        self.params['no_of_lanes_desc'] = "Number of process lanes"
        self.params['no_of_lanes_type'] = "configuration"
        self.params['tool_length'] = 8
        self.params['tool_length_desc'] = "Travel distance for wafers between input and output (meters)"
        self.params['tool_length_type'] = "configuration"
        self.params['belt_speed'] = 1.8
        self.params['belt_speed_desc'] = "Speed at which all units travel (meters per minute)"
        self.params['belt_speed_type'] = "process"
        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = "Minimal distance between wafers (meters)"
        self.params['unit_distance_type'] = "configuration"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        self.params['max_cassette_no_type'] = "configuration"
        
        self.params['downtime_volume'] = 100
        self.params['downtime_volume_desc'] = "Number of entered wafers before downtime (x1000) (0 to disable function)"
        self.params['downtime_volume_type'] = "downtime"
        self.params['downtime_duration'] = 60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (minutes)"
        self.params['downtime_duration_type'] = "downtime"

        self.params['mtbf'] = 1000
        self.params['mtbf_desc'] = "Mean time between failures (hours) (0 to disable function)"
        self.params['mtbf_type'] = "downtime"
        self.params['mttr'] = 60
        self.params['mttr_desc'] = "Mean time to repair (minutes) (0 to disable function)"
        self.params['mttr_type'] = "downtime"
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)

        if self.params['cassette_size'] == -1:
            self.params['cassette_size'] = 100
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.first_run = True
        self.process_counter = 0
        self.time_step = 60*self.params['unit_distance']/self.params['belt_speed']
        
        ### Input ###
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'])

        ### Array of zeroes represents lanes ###
        self.lanes = []
        for i in  range(self.params['no_of_lanes']):
            no_positions = int(self.params['tool_length']//self.params['unit_distance'])
            self.lanes.append(collections.deque([False for rows in range(no_positions)]))            

        ### Output ###
        self.output = CassetteContainer(self.env,"output",self.params['max_cassette_no'])
        self.wafer_out = simpy.Container(self.env)

        self.idle_time = 0
                                     
        self.downtime_finished = None
        self.technician_resource = simpy.Resource(self.env,1)
        self.downtime_duration =  0
        self.maintenance_needed = False
        
        random.seed(42)
        self.mtbf_enable = False
        if (self.params['mtbf'] > 0) and (self.params['mttr'] > 0):
            self.next_failure = random.expovariate(1/(3600*self.params['mtbf']))
            self.mtbf_enable = True       
        
        self.env.process(self.run_cassette_load_out())
        self.env.process(self.run_lane_load_out())
        self.env.process(self.run_lanes())
        self.env.process(self.run_cassette_load_in())

    def report(self):
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport_counter
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            util = 100*(production_volume/production_hours)/self.nominal_throughput()
            self.utilization.append(round(util,1))
        else:
            self.utilization.append(0)            

        self.utilization.append(self.transport_counter)

        if not self.first_run:
            idle_time = 100-100*self.idle_time/(self.env.now-self.start_time)
            self.utilization.append(["Lanes ",round(idle_time,1)])
        else:
            self.utilization.append(["Lanes ",0])

    def prod_volume(self):
        return self.transport_counter

    def run_cassette_load_in(self):
        cassette_size = self.params['cassette_size']
        time_step = self.time_step
        no_of_lanes = self.params['no_of_lanes']
        max_cassette_no = self.params['max_cassette_no']
        max_volume = self.params['no_of_lanes']*self.params['tool_length']/self.params['unit_distance']
        min_output_cass = 1+max_volume/self.params['cassette_size']
        min_output_cass = min(max_cassette_no,min_output_cass)
        downtime_volume = 1000*self.params['downtime_volume']
        downtime_duration = 60*self.params['downtime_duration']
        
        cassette = yield self.input.input.get() # receive first full cassette        
        wafer_counter = cassette_size

        mtbf_enable = self.mtbf_enable
        if mtbf_enable:
            mtbf = 1/(3600*self.params['mtbf'])
            mttr = 1/(60*self.params['mttr'])

        while True:

            if mtbf_enable and self.env.now >= self.next_failure:
                self.downtime_duration = random.expovariate(mttr)
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF set failure - maintenance needed for " + str(round(self.downtime_duration/60)) + " minutes")
                self.downtime_finished = self.env.event()
                self.maintenance_needed = True                    
                yield self.downtime_finished
                self.next_failure = self.env.now + random.expovariate(mtbf)
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF maintenance finished - next maintenance in " + str(round((self.next_failure - self.env.now)/3600)) + " hours")            
            
            if wafer_counter < cassette_size:
                # if not enough wafers available get new full cassette
                yield self.input.output.put(cassette) # return empty cassette
                cassette = yield self.input.input.get() # receive full cassette
                wafer_counter += cassette_size

            if (downtime_volume > 0) & (self.process_counter >= downtime_volume):
                yield self.env.timeout(downtime_duration)
                self.idle_time += downtime_duration
                self.process_counter = 0

            # skip load-in if empty cassette buffer too low, full cassette buffer too full or not enough wafers
            space_input = len(self.output.input.items)
            space_output = (max_cassette_no - len(self.output.output.items))
            if (space_input < min_output_cass) or (space_output < min_output_cass) or (wafer_counter < no_of_lanes):
                if not self.first_run:
                    self.idle_time += time_step
                yield self.env.timeout(time_step)
                continue
            
            if self.first_run:
                self.start_time = self.env.now
                self.first_run = False
            
            wafer_counter -= no_of_lanes
                
            for i in range(no_of_lanes):
                self.lanes[i][0] = True

#                if ((self.process_counter % self.params['cassette_size']) == 0): #DEBUG      
#                    string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] " #DEBUG
#                    string += "Loaded " + str(self.params['cassette_size']) + " units in lane " + str(lane_number) #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
            
            self.process_counter += no_of_lanes              
            
            yield self.env.timeout(time_step)

    def run_lanes(self):
        no_of_lanes = self.params['no_of_lanes']
        time_step = self.time_step
        
        while True:
            for i in range(0,no_of_lanes):
                self.lanes[i].rotate(1)
            yield self.env.timeout(time_step)

    def run_lane_load_out(self):
        no_of_lanes = self.params['no_of_lanes']
        time_step = self.time_step
        cassette_size = self.params['cassette_size']
        signal_not_sent0 = True
        signal_not_sent1 = True
        
        while True:
            count = 0
            for i in range(0,no_of_lanes):
                if self.lanes[i][-1]:
                    self.lanes[i][-1] = False
                    count += 1

            if count:
                yield self.wafer_out.put(count)
    
            if signal_not_sent0 and (self.wafer_out.level > 2*cassette_size):
                string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
                string += "Overload in load-out section (> 1 cassette)"
                self.output_text.sig.emit(string)
                signal_not_sent0 = False

            if signal_not_sent1 and (self.wafer_out.level > 11*cassette_size):
                string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
                string += "Major overload in load-out section (>10 cassettes)"
                self.output_text.sig.emit(string)
                signal_not_sent1 = False
                    
            yield self.env.timeout(time_step)

    def run_cassette_load_out(self):
        cassette_size = self.params['cassette_size']
        cassette = yield self.output.input.get() # receive empty cassette

        while True:
            if self.wafer_out.level >= cassette_size:
                # if load is full, fill cassette and replace it for empty cassette
                yield self.wafer_out.get(cassette_size)
                yield self.output.output.put(cassette) # return full cassette
                self.transport_counter += cassette_size
                cassette = yield self.output.input.get() # receive empty cassette
            
            yield self.env.timeout(1)

    def nominal_throughput(self):       
        return self.params['no_of_lanes']*60*self.params['belt_speed']/self.params['unit_distance']