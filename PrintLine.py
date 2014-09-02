# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO
Not yet implemented - copy of WaferUnstacker

"""
from __future__ import division
from BatchTransport import BatchTransport
from BatchProcess import BatchProcess
from BatchContainer import BatchContainer
import simpy

class PrintLine(object):

    def __init__(self, env, name="", stack_size=400, max_stack_no=3, cassette_size=100, max_cassette_no=4):    
        
        self.env = env
        self.name = name
        self.stack_size = stack_size
        self.max_stack_no = max_stack_no
        self.cassette_size = cassette_size
        self.max_cassette_no = max_cassette_no
        self.wait_time = 60
        self.units_on_belt = 5
        self.time_step = 1 # numer of seconds for one unit to progress one position
        self.next_step = env.event()
        print str(self.env.now) + " - [PrintLine][" + self.name + "] Added a print line"
        
        self.input = BatchContainer(self.env,"input",self.stack_size,self.max_stack_no)
        self.belt = BatchContainer(self.env,"belt",self.units_on_belt,1)
        self.output = BatchContainer(self.env,"input",self.cassette_size,max_cassette_no)

        self.env.process(self.run_pick_and_place())
        self.env.process(self.run_cassette_loader())

    def report(self):
        print "Not implemented yet"
        #print "[PrintLine][" + self.name + "] Units processed: " + str(self.output.process_counter)        

    def run_pick_and_place(self):
        #first_run = 1
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

            if (unit_counter == self.stack_size):                
                yield self.env.timeout(10)
                unit_counter = 0
                #print str(self.env.now) +" New stack loaded"
            
    def run_cassette_loader(self):
        current_load = 0
        
        while True:          
            if (current_load < self.cassette_size) & (self.input.container.level > 0):
                #print str(self.env.now) + " Triggering event"
                yield self.next_step.succeed()
                self.next_step = self.env.event() # make new event

            if (self.belt.container.level > 0):
                # belt may be empty because a new stack is being loaded, or because there are no new stacks
                yield self.belt.container.get(1)
                current_load += 1
            
            if (current_load == self.cassette_size):
                # whole machine is paused when the output container is full
                yield self.output.container.put(self.cassette_size)
                self.output.process_counter += self.cassette_size
                current_load = 0                
                yield self.env.timeout(10) # load new cassette
                #print str(self.env.now) + " New output cassette"
            
            yield self.env.timeout(self.time_step)