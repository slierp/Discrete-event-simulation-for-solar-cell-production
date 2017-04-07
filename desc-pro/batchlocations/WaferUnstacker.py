# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
import collections, random

class WaferUnstacker(QtCore.QObject):
        
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
A WaferUnstacker is used to transfer wafer from stacks into cassettes.
It accepts a number of stacks, one of which is placed in an unloading position.
From that position the wafers are placed one by one onto a belt.
The belt then transfers the wafers into cassettes at the output.
When a cassette is full there is a time delay for loading a new cassette.\n
<h3>Description of the algorithm</h3>
There are two loops to simulate the tool, one for the wafer unstacking and one running the belt and the cassette loading.
The loop that performs the wafer unstacking consists of the following steps:
<ol>
<li>Pick up a wafer if not already available</li>
<li>If current wafer stack had been empty pause momentarily to simulate loading a new stack</li>
<li>If the first position on the belt is empty, load the wafer onto it</li>
<li>Wait for a set time period, to simulate the pick and place action</li>
</ol>
The second loop consists of the following steps:
<ol>
<li>If wafer available at end of belt and there is space in the cassette transfer it to cassette</li>
<li>If no wafer available at end of belt, move belt by one position</li>
<li>If cassette is full, pause momentarily to simulate cassette replacement</li>
</ol>
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "WaferUnstacker"
        self.params['stack_size'] = 500
        self.params['stack_size_desc'] = "Number of wafers in a single stack"
        self.params['stack_size_type'] = "configuration"
        self.params['max_stack_no'] = 4
        self.params['max_stack_no_desc'] = "Maximum number of stacks at the input side"
        self.params['max_stack_no_type'] = "configuration"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of output cassette positions"
        self.params['max_cassette_no_type'] = "configuration"
        self.params['units_on_belt'] = 5
        self.params['units_on_belt_desc'] = "Number of wafers that fit on the belt"
        self.params['units_on_belt_type'] = "configuration"
        
        self.params['time_step'] = 1/1
        self.params['time_step_desc'] = "Time for one wafer to progress one position on belt or into cassette (seconds) (0.1 sec minimum)"
        self.params['time_step_type'] = "automation"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a wafer loading position (seconds)"
        self.params['time_new_cassette_type'] = "automation"
        self.params['time_new_stack'] = 10
        self.params['time_new_stack_desc'] = "Time for putting a new stack into the wafer unloading position (seconds)"
        self.params['time_new_stack_type'] = "automation"
        self.params['time_pick_and_place'] = 1/1
        self.params['time_pick_and_place_desc'] = "Time for putting a single unit on the belt (seconds) (0.1 sec minimum)"
        self.params['time_pick_and_place_type'] = "automation"

        self.params['reject_percentage'] = 0
        self.params['reject_percentage_desc'] = "Percentage of randomly rejected wafers (%)"
        self.params['reject_percentage_type'] = "downtime"

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

        self.input = BatchContainer(self.env,"stack_in",self.params['stack_size'],self.params['max_stack_no'])
        self.belt = collections.deque([False] * (self.params['units_on_belt']+1))
        self.output = CassetteContainer(self.env,"output",self.params['max_cassette_no'])

        if self.params['reject_percentage'] > 0:
            random.seed(42)

        self.env.process(self.run_pick_and_place())
        self.env.process(self.run_cassette_loader())

    def report(self):
        return

    def prod_volume(self):
        return self.output.process_counter

    def run_pick_and_place(self):
        unit_counter = 0
        restart = True
        time_new_stack = self.params['time_new_stack']
        time_pick_and_place = self.params['time_pick_and_place']
        stack_size = self.params['stack_size']
        time_step = self.params['time_step']
        wafer_available = False
        
        while True:
            if (not wafer_available):
                # if pick and place robot does not already have a wafer try to get one
                yield self.input.container.get(1)
                wafer_available = True
            
            if (restart):
                #time delay for loading new stack if input had been completely empty
                yield self.env.timeout(time_new_stack)
                restart = False            
                
            if (not self.belt[0]):
                yield self.env.timeout(time_pick_and_place)
                self.belt[0] = True
                wafer_available = False
                unit_counter += 1
                                
#            string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Put wafer from stack onto belt" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG

            if (unit_counter == stack_size):
                # if current stack is empty and there are more stacks available, delay to load a new stack                
                unit_counter = 0            
                restart = True
                    
            yield self.env.timeout(time_step)                    
            
    def run_cassette_loader(self):
        current_load = 0
        time_new_cassette = self.params['time_new_cassette']
        time_step = self.params['time_step']
        cassette_size = self.params['cassette_size']
        reject_percentage = self.params['reject_percentage']
        
        cassette = yield self.output.input.get() # receive first empty cassette

        while True:     
            if (self.belt[-1]) & (current_load < cassette_size):
                # if wafer available and cassette is not full, load into cassette
                self.belt[-1] = False
                self.belt.rotate(1)
                yield self.env.timeout(time_step)                
                current_load += 1              

                # remove wafer again if it falls within random reject range
                if reject_percentage and (random.randint(0,100) <= reject_percentage):
                    current_load -= 1
                
#                string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Put wafer from belt into cassette" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG
                                          
            elif (not self.belt[-1]):
                # move belt if no wafer available
                self.belt.rotate(1)
                yield self.env.timeout(time_step)                
            
            if (current_load == cassette_size):            
                # if load is full, fill cassette and replace it for empty cassette
                yield self.output.output.put(cassette) # return full cassette
                self.output.process_counter += cassette_size
                cassette = yield self.output.input.get() # receive empty cassette
                
                current_load = 0
                yield self.env.timeout(time_new_cassette) # time for loading new cassette                