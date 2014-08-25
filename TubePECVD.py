# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 14:36:34 2014

@author: rnaber

"""

from __future__ import division
from BatchProcess import BatchProcess
from BatchContainer import BatchContainer
import numpy as np

class TubePECVD(object):
    def __init__(self, env, name="", process_batch_size=300, process_time=30*60, cool_time=10*60,
                 no_of_processes=4, cassette_size=100, max_cassette_no=5, no_of_boats=6, transfer_time = 10*60):
        
        self.env = env
        self.name = name
        self.process_batch_size = process_batch_size
        self.process_time = process_time
        self.cool_time = cool_time
        self.no_of_processes = no_of_processes
        self.cassette_size = cassette_size
        self.max_cassette_no = max_cassette_no
        self.no_of_boats = no_of_boats
        self.transfer_time = transfer_time = 10*60
        self.wait_time = 60
        self.transport_counter = 0
        self.batches_loaded = 0
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.load_in_out_end = self.env.event()
        
        print str(self.env.now) + " - [TubePECVD][" + self.name + "] Added a tube furnace"        
        
        self.input = BatchContainer(self.env,"input",self.cassette_size,self.max_cassette_no)
        self.boat_load_unload = BatchContainer(self.env,"boat_load_unload",self.process_batch_size,1)

        self.batchprocesses = {}
        self.coolprocesses = {}  
        for i in np.arange(self.no_of_processes):
            process_name = "pecvd" + str(i)
            self.batchprocesses[i] = BatchProcess(self.env,process_name,self.process_batch_size,self.process_time)

        for i in np.arange(self.no_of_processes-1): # always one cool-down location less than the number of tubes
            process_name = "cooldown" + str(i)
            self.coolprocesses[i] = BatchProcess(self.env,process_name,self.process_batch_size,self.cool_time)
               
        self.output = BatchContainer(self.env,"output",self.cassette_size,self.max_cassette_no)        
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        print "[TubePECVD][" + self.name + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        for i in self.batchprocesses:
            print "[TubePECVD][" + self.name + "][" + self.batchprocesses[i].name + "] Idle time: " + str(np.round(self.batchprocesses[i].idle_time(),1)) + " %" 

    def run_transport(self):
        
        batchconnections = {}
        j = 0
        for i in np.arange(self.no_of_processes*(self.no_of_processes-1)):
            # always one cool-down location less than the number of tubes
            if (i%self.no_of_processes == 0) & (i > 0):
                j += 1
                
            batchconnections[i] = [self.batchprocesses[i%self.no_of_processes],self.coolprocesses[j]]      
        
        while True:
            for i in batchconnections:
                # first check if we can move any batch from tube to cool_down
                if (batchconnections[i][0].container.level > 0) & \
                        (batchconnections[i][1].container.level == 0) & \
                            batchconnections[i][0].process_finished:
                                        
                    request_input = batchconnections[i][0].resource.request()
                    yield request_input
                    request_output = batchconnections[i][1].resource.request()                    
                    yield request_output

                    yield batchconnections[i][0].container.get(self.process_batch_size)
                    yield self.env.timeout(90)
                    yield batchconnections[i][1].container.put(self.process_batch_size)

                    yield batchconnections[i][0].resource.release(request_input)
                    batchconnections[i][0].process_finished = 0

                    yield batchconnections[i][1].resource.release(request_output)
                    batchconnections[i][1].start_process()
                    #print str(self.env.now) + " - [TubeFurnace][" + self.name + "] Moved batch to cooldown"                    

            for i in self.coolprocesses:
                # check if we can unload a batch (should be followed by a re-load if possible)
                if (self.coolprocesses[i].container.level > 0) & \
                        (self.boat_load_unload.container.level == 0) & \
                            self.coolprocesses[i].process_finished:
                
                    request_input = self.coolprocesses[i].resource.request()
                    yield request_input

                    yield self.coolprocesses[i].container.get(self.process_batch_size)
                    yield self.env.timeout(90)
                    yield self.boat_load_unload.container.put(self.process_batch_size)
                    
                    yield self.coolprocesses[i].resource.release(request_input)
                    self.coolprocesses[i].process_finished = 0                    
                    
                    yield self.load_out_start.succeed()
                    yield self.load_in_out_end
                    self.load_out_start = self.env.event()                    
            
            if (self.batches_loaded < self.no_of_boats) & (self.input.container.level >= self.process_batch_size) & \
                    (self.boat_load_unload.container.level == 0):
                # ask for more wafers if there is a boat and wafers available
                yield self.load_in_start.succeed()
                yield self.load_in_out_end
                self.load_in_start = self.env.event() # make new event                

            for i in self.batchprocesses:
                # check if we can load new wafers into a tube
                if (self.batchprocesses[i].container.level == 0) & \
                        (self.boat_load_unload.container.level == self.process_batch_size):

                    request_output = self.batchprocesses[i].resource.request()                    
                    yield request_output
                        
                    yield self.boat_load_unload.container.get(self.process_batch_size)
                    yield self.env.timeout(90)
                    yield self.batchprocesses[i].container.put(self.process_batch_size)

                    yield self.batchprocesses[i].resource.release(request_output)
                    self.batchprocesses[i].start_process()
                    #print str(self.env.now) + " - [TubePECVD][" + self.name + "] Started a process"
            
            yield self.env.timeout(self.wait_time)                        
            
    def run_load_in(self):
        while True:
            yield self.load_in_start
            #print str(self.env.now) + " - [TubePECVD][" + self.name + "] Loading trigger received"
            for i in np.arange(self.process_batch_size/self.cassette_size): # how to ensure it is an integer?
                yield self.env.timeout(30) # very critical for throughput
                yield self.input.container.get(self.cassette_size)            
                yield self.boat_load_unload.container.put(self.cassette_size)
            self.batches_loaded += 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event
            #print str(self.env.now) + " - [TubePECVD][" + self.name + "] Loaded batch"

    def run_load_out(self):
        while True:
            yield self.load_out_start
            #print str(self.env.now) + " - [TubePECVD][" + self.name + "] Unloading trigger received"
            for i in np.arange(self.process_batch_size/self.cassette_size): # how to ensure it is an integer?
                yield self.env.timeout(30) # very critical for throughput
                yield self.boat_load_unload.container.get(self.cassette_size) 
                yield self.output.container.put(self.cassette_size)
                self.transport_counter += self.cassette_size
            self.batches_loaded -= 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event            
            #print str(self.env.now) + " - [TubePECVD][" + self.name + "] Unloaded batch"          