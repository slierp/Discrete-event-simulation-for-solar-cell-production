# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO
Should also contain a wafer inspector module?

"""
from __future__ import division
from BatchContainer import BatchContainer
import simpy

class WaferUnstacker(object):
    #WaferUnstacker accepts a number of stacks of wafers
    #pick and place machine puts wafers one by one on a belt; belt loads it into one of four cassettes
        
    def __init__(self, env, _params = {}):   
        
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['stack_size'] = 400
        self.params['max_stack_no'] = 3
        self.params['cassette_size'] = 100
        self.params['max_cassette_no'] = 4
        self.params['units_on_belt'] = 5 # how many units fit on the belt
        self.params['time_step'] = 1 # number of seconds for one unit to progress one position
        self.params['time_new_cassette'] = 10 # number of seconds for putting empty cassette into position
        self.params['time_new_stack'] = 10 # number of seconds for putting a new stack in position
        self.params.update(_params)
        
        self.next_step = env.event()
        print str(self.env.now) + " - [WaferUnstacker][" + self.params['name'] + "] Added a wafer unstacker"        

        self.input = BatchContainer(self.env,"input",self.params['stack_size'],self.params['max_cassette_no'])
        self.belt = BatchContainer(self.env,"belt",self.params['units_on_belt'],1)
        self.output = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        self.env.process(self.run_pick_and_place())
        self.env.process(self.run_cassette_loader())

    def report(self):
        print "[WaferUnstacker][" + self.params['name'] + "] Units processed: " + str(self.output.process_counter)

    def run_pick_and_place(self):
        unit_counter = 0
        
        while True:
            yield self.next_step
            #print str(self.env.now) +" Trigger received"
            
            if (self.input.container.level > 0):
                yield self.input.container.get(1)
                yield self.env.timeout(1) # time to pick and place a wafer
                yield self.belt.container.put(1)
                unit_counter += 1
                #print str(self.env.now) +" Put wafer on belt"

            if (unit_counter == self.params['stack_size']):                
                yield self.env.timeout(self.params['time_new_stack'])
                unit_counter = 0
                #print str(self.env.now) +" New stack loaded"
            
    def run_cassette_loader(self):
        current_load = 0
        
        while True:          
            if (current_load < self.params['cassette_size']) & (self.input.container.level > 0):    
                #print str(self.env.now) + " Triggering event"
                yield self.next_step.succeed()
                self.next_step = self.env.event() # make new event

            if (self.belt.container.level > 0):
                # belt may be empty because a new stack is being loaded, or because there are no new stacks
                yield self.belt.container.get(1)
                current_load += 1
            
            if (current_load == self.params['cassette_size']):                
                # whole machine is paused when the output container is full
                yield self.output.container.put(self.params['cassette_size'])
                self.output.process_counter += self.params['cassette_size']
                current_load = 0                
                yield self.env.timeout(self.params['time_new_cassette']) # load new cassette
                #print str(self.env.now) + " New output cassette"
            
            yield self.env.timeout(self.params['time_step']) 