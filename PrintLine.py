# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

"""
from __future__ import division
from BatchContainer import BatchContainer
import simpy
import numpy as np

class PrintLine(object):
        
    def __init__(self, env, _params = {}):
          
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['cassette_size'] = 100
        self.params['max_cassette_no'] = 4
        self.params['units_on_belt_input'] = 8 # how many units fit on the belt between wafer source and printer
        self.params['time_step'] = 1 # number of seconds for one unit to progress one position
        self.params['time_new_cassette'] = 10 # number of seconds for new full cassette into position
        self.params['time_new_stack'] = 10 # number of seconds for putting a new stack in position
        self.params['time_cassette_to_belt'] = 1 # time to place a wafer onto the first belt
        self.params['time_print'] = 2 # time to print one wafer
        self.params['time_dry'] = 90 # time for one wafer to go from printer to dryer and to next input (printing or firing)
        self.params['no_print_steps'] = 3 # number of print and dry stations
        self.params.update(_params)
        
        print str(self.env.now) + " - [PrintLine][" + self.params['name'] + "] Added a print line"        

        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.output = InfiniteContainer(self.env,"output")

        self.next_step = {} # trigger events
        self.belts = {} # belts preceeding printers
        self.inputs = {} # cassette-like input before belts

        for i in np.arange(self.params['no_print_steps']):
            self.next_step[i] = env.event()
            self.belts[i] = BatchContainer(self.env,"belt_input",self.params['units_on_belt_input'],1)
            self.inputs[i] = BatchContainer(self.env,"input",self.params['cassette_size'],1) # buffer inside printer line            
            self.env.process(self.run_belt(i))
            self.env.process(self.run_printer(i))

    def report(self):
        print "[PrintLine][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)

    def run_belt(self, num):        
        while True:
            yield self.next_step[num]
            #print str(self.env.now) + " Trigger received"
            
            if (num):
                yield self.inputs[num].container.get(1)
            else:                
                yield self.input.container.get(1)
                
            yield self.env.timeout(self.params['time_cassette_to_belt']) 
            yield self.belts[num].container.put(1)
            #print str(self.env.now) + " Put wafer on belt"
            
    def run_printer(self, num):        
        while True:
            if (not num):
                input_check = (self.input.container.level > 0)
            else:
                input_check = (self.inputs[num].container.level > 0)
            
            if (self.belts[num].space_available(1)) & (input_check):                
                #print str(self.env.now) + " Triggering event"
                yield self.next_step[num].succeed()
                self.next_step[num] = self.env.event() # make new event

            if (not self.belts[num].space_available(1)) | (input_check & (self.belts[num].container.level > 0)):
                # if belt is fully loaded print one
                # else if input is empty but still wafers present on belt, continue printing until empty
                yield self.belts[num].container.get(1)
                yield self.env.timeout(self.params['time_print'])
                self.env.process(self.run_wafer_instance_drying(num))
            else:
                # if not printing, delay for time needed to load one wafer
                yield self.env.timeout(self.params['time_step'])

    def run_wafer_instance_drying(self, num):        
        yield self.env.timeout(self.params['time_dry'])
        
        if (num+1 < self.params['no_print_steps']):
            yield self.inputs[num+1].container.put(1)
        else:
            yield self.output.container.put(1)

class InfiniteContainer(object):
    
    def __init__(self, env, name=""):        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)