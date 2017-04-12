# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
import collections, random, simpy

class WaferStacker(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):  
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []        
        self.next_step = self.env.event()
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Belt"];
                       C [label = "Output"];
                       A -> B -> C;                    
                       } """        
        
        self.params = {}
        self.params['specification'] = """
<h3>General description</h3>
A WaferStacker is used to transfer wafer from cassettes to stacks.
It accepts a number of cassettes, one of which is placed in an unloading position.
From that position the wafers are placed one by one onto a belt.
The belt then transfers the wafers to a pick-up robot that stacks the wafers at the output.
When a cassette is empty there is a time delay for loading a new cassette.\n
<h3>Description of the algorithm</h3>
There are two loops to simulate the tool, one for the wafer unloading from cassetttes and one running the belt and the wafer stacking.
The loop that performs the wafer unloading consists of the following steps:
<ol>
<li>Pick up a wafer if not already available</li>
<li>If current cassette had been empty pause momentarily to simulate loading a cassette</li>
<li>If the first position on the belt is empty, load the wafer onto it</li>
<li>Wait for a set time period, to simulate the wafer placement action</li>
</ol>
The second loop consists of the following steps:
<ol>
<li>If current wafer stack holder had been full pause momentarily to simulate loading a new stack holder</li>
<li>Try to pick up wafer from end position on belt and perform a delay to simulate the action</li>
<li>If wafer available load it into output</li>
<li>Move belt forward by one position and perform a delay to simulate the belt movement time</li>
</ol>
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "WaferStacker"        
        self.params['stack_size'] = 500
        self.params['stack_size_desc'] = "Number of wafers in a single stack"
        self.params['stack_size_type'] = "configuration"
        self.params['max_stack_no'] = 4
        self.params['max_stack_no_desc'] = "Maximum number of stacks at the output side"
        self.params['max_stack_no_type'] = "configuration"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of input cassette positions"
        self.params['max_cassette_no_type'] = "configuration"
        self.params['units_on_belt'] = 5
        self.params['units_on_belt_desc'] = "Number of wafers that fit on the belt"
        self.params['units_on_belt_type'] = "configuration"
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one position on belt (seconds) (0.1 sec minimum)"
        self.params['time_step_type'] = "automation"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a wafer unloading position (seconds)"
        self.params['time_new_cassette_type'] = "automation"
        self.params['time_new_stack'] = 10
        self.params['time_new_stack_desc'] = "Time for putting a new stack into the wafer loading position (seconds)"
        self.params['time_new_stack_type'] = "automation"
        self.params['time_pick_and_place'] = 1.0
        self.params['time_pick_and_place_desc'] = "Time for putting a single wafer on a stack (seconds) (0.1 sec minimum)"
        self.params['time_pick_and_place_type'] = "automation"

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

        if (self.params['time_step'] < 1/10): # enforce minimum time step
            self.params['time_step'] = 1/10

        if (self.params['time_pick_and_place'] < 1/10): # enforce minimum time step
            self.params['time_pick_and_place'] = 1/10

        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'])        
        self.belt = collections.deque([False] * (self.params['units_on_belt']+1))
        self.output = BatchContainer(self.env,"output",self.params['stack_size'],self.params['max_stack_no'])

        self.start_time = -1
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

        self.env.process(self.run_load_in_conveyor())
        self.env.process(self.run_pick_and_place())

    def report(self):
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.output.process_counter
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            util = 100*(production_volume/production_hours)/self.nominal_throughput()
            self.utilization.append(round(util,1))
        else:
            self.utilization.append(0)            

        self.utilization.append(self.output.process_counter)

        if not self.start_time == -1:
            idle_time = 100-100*self.idle_time/(self.env.now-self.start_time)
            self.utilization.append(["Lane ",round(idle_time,1)])
        else:
            self.utilization.append(["Lane ",0])

    def prod_volume(self):
        return self.output.process_counter

    def run_load_in_conveyor(self):
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        time_step = self.params['time_step']
        
        cassette = yield self.input.input.get() # receive first cassette
        wafer_counter = cassette_size
        self.start_time = self.env.now

        mtbf_enable = self.mtbf_enable
        if mtbf_enable:
            mtbf = 1/(3600*self.params['mtbf'])
            mttr = 1/(60*self.params['mttr'])
        
        while True:

            if mtbf_enable and self.env.now >= self.next_failure:
                self.downtime_duration = random.expovariate(mttr)
                start = self.env.now
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF set failure - maintenance needed for " + str(round(self.downtime_duration/60)) + " minutes")
                self.downtime_finished = self.env.event()
                self.maintenance_needed = True                    
                yield self.downtime_finished
                self.idle_time += self.env.now - start
                self.next_failure = self.env.now + random.expovariate(mtbf)
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF maintenance finished - next maintenance in " + str(round((self.next_failure - self.env.now)/3600)) + " hours")  
            
            if (not self.belt[0]):                 
                self.belt[0] = True
                wafer_counter -= 1
            else:
                self.idle_time += time_step
                
#                string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Put wafer from cassette onto conveyor" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

            if not wafer_counter:
                start = self.env.now
                yield self.input.output.put(cassette) # return empty cassette
                cassette = yield self.input.input.get() # receive new cassette
                self.idle_time += self.env.now - start                
                wafer_counter = cassette_size
                yield self.env.timeout(time_new_cassette)
                continue
                
            yield self.env.timeout(time_step)

    def run_pick_and_place(self):
        unit_counter = 0
        restart = True
        time_new_stack = self.params['time_new_stack']
        time_pick_and_place = self.params['time_pick_and_place']
        stack_size = self.params['stack_size']
        time_step = self.params['time_step']
        wafer_available = False
        
        while True:
            if (restart):
                #time delay for loading new stack if input had been completely empty
                yield self.env.timeout(time_new_stack)
                restart = False

            if (self.belt[-1]) and (not wafer_available): # try to get wafer
                yield self.env.timeout(time_pick_and_place)
                self.belt[-1] = False                
                wafer_available = True
                unit_counter += 1
                
            if (wafer_available):
                # if pick and place robot has a wafer then put it on stack
                yield self.output.container.put(1)
                wafer_available = False
                    
#                string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Put wafer from belt onto stack" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

            if (unit_counter == stack_size):
                # if current stack is empty and there are more stacks available, delay to load a new stack                
                unit_counter = 0            
                restart = True
                self.output.process_counter += stack_size

            self.belt.rotate(1)                    
            yield self.env.timeout(time_step)
            
    def nominal_throughput(self):
        return 3600/(self.params['time_pick_and_place'] + self.params['time_step'])       