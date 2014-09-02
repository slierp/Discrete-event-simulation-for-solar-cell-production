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
    # a copy of TubeFurnace mostly
    # different batch size and process_time only
    # more custom pecvd adjustments may be needed later

    def __init__(self, env, _params = {}):   
        
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['process_batch_size'] = 300
        self.params['process_time'] = 30*60        
        self.params['cool_time'] = 10*60
        self.params['no_of_processes'] = 4
        self.params['no_of_cooldowns'] = 3
        self.params['cassette_size'] = 100
        self.params['max_cassette_no'] = 5 # max number of cassettes in the input and output buffers
        self.params['no_of_boats'] = 6
        self.params['transfer_time'] = 90 # time needed to transfer boat between any two locations 
        self.params['load_time_per_cassette'] = 30 # time needed to transfer one cassette in or out of the boat (very critical for throughput)
        self.params['wait_time'] = 60
        self.params.update(_params)        

        self.transport_counter = 0
        self.batches_loaded = 0
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.load_in_out_end = self.env.event()
        
        print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Added a tube furnace"        
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.boat_load_unload = BatchContainer(self.env,"boat_load_unload",self.params['process_batch_size'],1)

        self.batchprocesses = {}
        self.coolprocesses = {}  
        for i in np.arange(self.params['no_of_processes']):
            process_name = "furnace" + str(i)
            self.batchprocesses[i] = BatchProcess(self.env,process_name,self.params['process_batch_size'],self.params['process_time'])
            
        for i in np.arange(self.params['no_of_cooldowns']):
            process_name = "cooldown" + str(i)
            self.coolprocesses[i] = BatchProcess(self.env,process_name,self.params['process_batch_size'],self.params['cool_time'])
               
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])        
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        print "[TubePECVD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        for i in self.batchprocesses:
            print "[TubePECVD][" + self.params['name'] + "][" + self.batchprocesses[i].name + "] Idle time: " + str(np.round(self.batchprocesses[i].idle_time(),1)) + " %" 

    def run_transport(self):
        
        batchconnections = {}
        j = 0
        for i in np.arange(self.params['no_of_processes']*self.params['no_of_cooldowns']):
            if (i%self.params['no_of_processes'] == 0) & (i > 0):
                j += 1
                
            batchconnections[i] = [self.batchprocesses[i%self.params['no_of_processes']],self.coolprocesses[j]]

        
        while True:
            for i in batchconnections:
                # first check if we can move any batch from tube to cool_down
                if (batchconnections[i][0].container.level > 0) & \
                        (batchconnections[i][1].container.level == 0) & \
                            batchconnections[i][0].process_finished:
                                        
                    with batchconnections[i][0].resource.request() as request_input, \
                        batchconnections[i][1].resource.request() as request_output: 
                        yield request_input                 
                        yield request_output

                        yield batchconnections[i][0].container.get(self.params['process_batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield batchconnections[i][1].container.put(self.params['process_batch_size'])

                        batchconnections[i][0].process_finished = 0
                        batchconnections[i][1].start_process()
                        #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Moved batch to cooldown"                    

            for i in self.coolprocesses:
                # check if we can unload a batch (should be followed by a re-load if possible)
                if (self.coolprocesses[i].container.level > 0) & \
                        (self.boat_load_unload.container.level == 0) & \
                            self.coolprocesses[i].process_finished:
                
                    with self.coolprocesses[i].resource.request() as request_input:
                        yield request_input

                        yield self.coolprocesses[i].container.get(self.params['process_batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield self.boat_load_unload.container.put(self.params['process_batch_size'])
                        #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Moved processed batch for load-out"
                    
                        self.coolprocesses[i].process_finished = 0                    
                    
                        yield self.load_out_start.succeed()
                        yield self.load_in_out_end
                        self.load_out_start = self.env.event()                    
            
            if (self.batches_loaded < self.params['no_of_boats']) & (self.input.container.level >= self.params['process_batch_size']) & \
                    (self.boat_load_unload.container.level == 0):
                # ask for more wafers if there is a boat and wafers available
                yield self.load_in_start.succeed()
                yield self.load_in_out_end
                self.load_in_start = self.env.event() # make new event                

            for i in self.batchprocesses:
                # check if we can load new wafers into a tube
                if (self.batchprocesses[i].container.level == 0) & \
                        (self.boat_load_unload.container.level == self.params['process_batch_size']):

                    with self.batchprocesses[i].resource.request() as request_output:                  
                        yield request_output
                        
                        yield self.boat_load_unload.container.get(self.params['process_batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield self.batchprocesses[i].container.put(self.params['process_batch_size'])

                        self.batchprocesses[i].start_process()
                        #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Started a process"
            
            yield self.env.timeout(self.params['wait_time'])                        
            
    def run_load_in(self):
        while True:
            yield self.load_in_start
            #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Loading trigger received"
            for i in np.arange(self.params['process_batch_size']/self.params['cassette_size']): # how to ensure it is an integer?
                yield self.env.timeout(self.params['load_time_per_cassette'])
                yield self.input.container.get(self.params['cassette_size'])            
                yield self.boat_load_unload.container.put(self.params['cassette_size'])
            self.batches_loaded += 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event
            #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Loaded batch"

    def run_load_out(self):
        while True:
            yield self.load_out_start
            #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Unloading trigger received"
            for i in np.arange(self.params['process_batch_size']/self.params['cassette_size']): # how to ensure it is an integer?
                yield self.env.timeout(self.params['load_time_per_cassette']) 
                yield self.boat_load_unload.container.get(self.params['cassette_size']) 
                yield self.output.container.put(self.params['cassette_size'])
                self.transport_counter += self.params['cassette_size']
            self.batches_loaded -= 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event            
            #print str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Unloaded batch"          