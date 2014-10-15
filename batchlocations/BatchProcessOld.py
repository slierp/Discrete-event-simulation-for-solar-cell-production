# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:55:31 2014

@author: rnaber
"""        

from __future__ import division
#import simpyx as simpy
import simpy
         
class BatchProcess(object):
    
    def __init__(self, env, name="", batch_size=1, process_time=1, verbose=False):
        
        self.env = env
        self.name = name
        self.batch_size = batch_size
        self.process_time = process_time
        self.verbose = verbose
        self.resource = simpy.Resource(self.env, 1)
        self.process_finished = 0
        self.start_time = self.env.now
        self.process_time_counter = 0
        self.start = env.event()
        self.first_run = True
        self.idle_times = []

        self.process_counter = 0            
        self.container = simpy.Container(self.env,capacity=self.batch_size,init=0)
        
        if (self.verbose):
            print str(self.env.now) + " - [BatchProcess][" + self.name + "] Added default batch process"
        self.env.process(self.run())                                

    def run(self):
        while True:
            yield self.start
            
            if self.first_run:
                self.start_time = self.env.now
                self.first_run = False
                
            if (self.container.level >= self.batch_size) & (not self.process_finished):
                with self.resource.request() as request:
                    yield request
                    yield self.env.timeout(self.process_time) 
                    self.process_finished = 1
                    self.process_time_counter += self.process_time
                    
                    if (self.verbose):
                        print str(self.env.now) + " - [BatchProcess][" + self.name + "] End process "
            
    def space_available(self,_batch_size):
        if ((self.container.level+_batch_size) <= (self.batch_size)):
            return True
        else:
            return False

    def start_process(self):
        self.start.succeed()
        self.start = self.env.event() # make new event
        
    def idle_time(self):
        return 100-(100*self.process_time_counter/(self.env.now-self.start_time))