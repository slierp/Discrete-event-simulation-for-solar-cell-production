# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO
Should also contain a wafer inspector module?

"""
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer

class WaferUnstacker(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        
        self.params = {}
        self.params['specification'] = self.tr("WaferUnstacker accepts a number of stacks of wafers. A pick and place machine puts wafers one by one on a belt. The belt loads them into cassettes.")
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['stack_size'] = 400
        self.params['stack_size_desc'] = self.tr("Number of units in a single stack")
        self.params['max_stack_no'] = 3
        self.params['max_stack_no_desc'] = self.tr("Maximum number of stacks at the input side")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = self.tr("Number of output cassette positions")
        self.params['units_on_belt'] = 5
        self.params['units_on_belt_desc'] = self.tr("Number of units that fit on the belt")
        self.params['time_step'] = 1
        self.params['time_step_desc'] = self.tr("Time for one unit to progress one position (seconds)")
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = self.tr("Time for putting an empty cassette into a loading position (seconds)")
        self.params['time_new_stack'] = 10
        self.params['time_new_stack_desc'] = self.tr("Time for putting a new stack in unloading position (seconds)")
        self.params['time_pick_and_place'] = 1
        self.params['time_pick_and_place_desc'] = self.tr("Time for putting a single unit on the belt (seconds)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)
        
        self.next_step = self.env.event()
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [WaferUnstacker][" + self.params['name'] + "] Added a wafer unstacker"
            self.output_text.sig.emit(string)

        self.input = BatchContainer(self.env,"input",self.params['stack_size'],self.params['max_stack_no'])
        self.belt = BatchContainer(self.env,"belt",self.params['units_on_belt'],1)
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        self.env.process(self.run_pick_and_place())
        self.env.process(self.run_cassette_loader())

    def report(self):
        string = "[WaferUnstacker][" + self.params['name'] + "] Units processed: " + str(self.output.process_counter)
        self.output_text.sig.emit(string)

    def run_pick_and_place(self):
        unit_counter = 0
        restart = True
        
        while True:            
            yield self.next_step

            if (restart):
                # time delay for loading stack after being empty
                yield self.env.timeout(self.params['time_new_stack'])
                restart = False
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [WaferUnstacker][" + self.params['name'] + "] (Re-)starting unstacker"
                    self.output_text.sig.emit(string)
            
            yield self.input.container.get(1)
            yield self.env.timeout(self.params['time_pick_and_place'])
            yield self.belt.container.put(1)
            unit_counter += 1
            
            #if (self.params['verbose']):
            #    print str(self.env.now) + " [WaferUnstacker][" + self.params['name'] + "] Put wafer on belt"
            
            if (unit_counter == self.params['stack_size']):
                # if current stack is empty, delay to load a new stack                
                yield self.env.timeout(self.params['time_new_stack'])
                unit_counter = 0
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [WaferUnstacker][" + self.params['name'] + "] New input stack loaded"
                    self.output_text.sig.emit(string)
                    
            if (self.input.container.level == 0):
                restart = True
            
    def run_cassette_loader(self):
        current_load = 0
        
        while True:
            if (self.belt.space_available(1)) & (self.input.container.level > 0):
                # trigger new pick and place event if possible
                yield self.next_step.succeed()
                self.next_step = self.env.event() # make new event

            if (not self.belt.space_available(1)) & (self.output.space_available(1)):
                # if belt is full and there is space in the output, load one wafer into cassette
                yield self.belt.container.get(1)
                current_load += 1
            elif (self.input.container.level == 0) & (self.belt.container.level > 0) & (self.output.space_available(1)):
                # if the input is empty, but there are wafers on the belt and there is space in the output, continue loading
                yield self.belt.container.get(1)
                current_load += 1                
            
            if (current_load == self.params['cassette_size']):                
                # put one cassette into output at a time
                yield self.output.container.put(self.params['cassette_size'])
                self.output.process_counter += self.params['cassette_size']
                current_load = 0                
                yield self.env.timeout(self.params['time_new_cassette']) # load new cassette
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [WaferUnstacker][" + self.params['name'] + "] New output cassette"
                    self.output_text.sig.emit(string)
            
            yield self.env.timeout(self.params['time_step']) 