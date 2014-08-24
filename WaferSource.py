# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 09:01:54 2014

@author: rnaber
"""

from __future__ import division
from BatchContainer import BatchContainer
import simpy

class WaferSource(object):

    def __init__(self, env, name="", batch_size=400, time_limit=0):    
        
        self.env = env
        self.name = name
        self.batch_size = batch_size
        self.time_limit = time_limit
        self.process_counter = 0
        self.wait_time = 60
        print str(self.env.now) + " - [WaferSource][" + self.name + "] Added a wafer source"        
        
        self.output = BatchContainer(self.env,"output",self.batch_size,1)
        self.env.process(self.run())

    def report(self):
        print "[WaferSource][" + self.name + "] Units sourced: " + str(self.output.process_counter - self.output.container.level)
        
    def run(self):
        while True:
            
            if (self.time_limit > 0) & (self.env.now >= self.time_limit):
                print str(self.env.now) + " - [WaferSource][" + self.name + "] Time limit reached"
                break
            
            if (not self.output.container.level):
                #print str(self.env.now) + " - [BatchProcess][" + self.name + "] Start refill"
                yield self.output.container.put(self.batch_size)
                #print str(self.env.now) + " - [BatchProcess][" + self.name + "] End refill"
                self.output.process_counter += self.batch_size
            yield self.env.timeout(self.wait_time)        