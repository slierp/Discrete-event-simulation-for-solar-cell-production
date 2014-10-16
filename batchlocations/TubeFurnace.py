# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 14:36:34 2014

@author: rnaber

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer
import numpy as np

class TubeFurnace(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        
        self.params = {}
        self.params['specification'] = self.tr("TubeFurnace consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- Boat-load-unload container\n")
        self.params['specification'] += self.tr("- Process tubes\n")
        self.params['specification'] += self.tr("- Cooldown locations\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There are two transporters:\n")
        self.params['specification'] += self.tr("transport1: from load-in to boat-load-unload and from boat-load-unload to output\n")
        self.params['specification'] += self.tr("transport2: from boat-load-unload to tube process to cool-down to boat-load-unload\n")
        self.params['specification'] += self.tr("transport2 triggers transport1 when to do something (load or unload)\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("The number of batches in the system is limited by the no_of_boats variable.\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("Unloading has priority as this enables you to start a new process (less idle time).")

        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['batch_size'] = 500
        self.params['batch_size_desc'] = self.tr("Number of units in a single process batch")
        self.params['process_time'] = 60*60
        self.params['process_time_desc'] = self.tr("Time for a single process (seconds)")
        self.params['cool_time'] = 10*60
        self.params['cool_time_desc'] = self.tr("Time for a single cooldown (seconds)")
        self.params['no_of_processes'] = 4
        self.params['no_of_processes_desc'] = self.tr("Number of process locations in the tool")
        self.params['no_of_cooldowns'] = 3
        self.params['no_of_cooldowns_desc'] = self.tr("Number of cooldown locations in the tool")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 5
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input and the same number at output")
        self.params['no_of_boats'] = 6
        self.params['no_of_boats_desc'] = self.tr("Number of boats available")
        self.params['transfer_time'] = 90
        self.params['transfer_time_desc'] = self.tr("Time for boat transfer between any two locations")
        self.params['load_time_per_cassette'] = 30
        self.params['load_time_per_cassette_desc'] = self.tr("Time to transfer one cassette in or out of the boat (very critical for throughput)")
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = self.tr("Wait period between boat transport attempts (seconds)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)        

        self.transport_counter = 0
        self.batches_loaded = 0
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.load_in_out_end = self.env.event()
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Added a tube furnace"
            self.output_text.sig.emit(string)
        
        ### Add input and boat load/unload location ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.boat_load_unload = BatchContainer(self.env,"boat_load_unload",self.params['batch_size'],1)

        ### Add batch processes ###
        self.batchprocesses = [] 
        for i in np.arange(self.params['no_of_processes']):
            process_params = {}
            process_params['name'] = "t" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['process_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Add cooldown processes ###
        self.coolprocesses = []            
        for i in np.arange(self.params['no_of_cooldowns']):
            process_params = {}
            process_params['name'] = "c" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['cool_time']
            process_params['verbose'] = self.params['verbose']
            self.coolprocesses.append(BatchProcess(self.env,self.output_text,process_params))            
            
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])        
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        string = "[TubeFurnace][" + self.params['name'] + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        self.output_text.sig.emit(string)        

        idle_item = []
        idle_item.append("TubeFurnace")
        idle_item.append(self.params['name'])
        for i in range(len(self.batchprocesses)):
            idle_item.append([self.batchprocesses[i].name,np.round(self.batchprocesses[i].idle_time(),1)])
        self.idle_times.append(idle_item)              

    def run_transport(self):
        
        batchconnections = []
        j = 0
        for i in np.arange(self.params['no_of_processes']*self.params['no_of_cooldowns']):
            if (i%self.params['no_of_processes'] == 0) & (i > 0):
                j += 1
                
            batchconnections.append([self.batchprocesses[i%self.params['no_of_processes']],self.coolprocesses[j]])
        
        while True:
            for i in range(len(batchconnections)):
                # first check if we can move any batch from tube to cool_down
                if (batchconnections[i][0].container.level > 0) & \
                        (batchconnections[i][1].container.level == 0) & \
                            batchconnections[i][0].process_finished:
                                        
                    with batchconnections[i][0].resource.request() as request_input, \
                        batchconnections[i][1].resource.request() as request_output: 
                        yield request_input                 
                        yield request_output

                        yield batchconnections[i][0].container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield batchconnections[i][1].container.put(self.params['batch_size'])

                        batchconnections[i][0].process_finished = 0
                        batchconnections[i][1].start_process()
                        
                        if (self.params['verbose']):
                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Moved batch to cooldown"
                            self.output_text.sig.emit(string)

            for i in range(len(self.coolprocesses)):
                # check if we can unload a batch (should be followed by a re-load if possible)
                if (self.coolprocesses[i].container.level > 0) & \
                        (self.boat_load_unload.container.level == 0) & \
                            self.coolprocesses[i].process_finished:
                
                    with self.coolprocesses[i].resource.request() as request_input:
                        yield request_input

                        yield self.coolprocesses[i].container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield self.boat_load_unload.container.put(self.params['batch_size'])
                        
                        if (self.params['verbose']):
                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Moved processed batch for load-out"
                            self.output_text.sig.emit(string)
                    
                        self.coolprocesses[i].process_finished = 0                    
                    
                        yield self.load_out_start.succeed()
                        yield self.load_in_out_end
                        self.load_out_start = self.env.event()                    
            
            if (self.batches_loaded < self.params['no_of_boats']) & (self.input.container.level >= self.params['batch_size']) & \
                    (self.boat_load_unload.container.level == 0):
                # ask for more wafers if there is a boat and wafers available
                yield self.load_in_start.succeed()
                yield self.load_in_out_end
                self.load_in_start = self.env.event() # make new event                

            for i in range(len(self.batchprocesses)):
                # check if we can load new wafers into a tube
                if (self.batchprocesses[i].container.level == 0) & \
                        (self.boat_load_unload.container.level == self.params['batch_size']):

                    with self.batchprocesses[i].resource.request() as request_output:                  
                        yield request_output
                        
                        yield self.boat_load_unload.container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer_time'])
                        yield self.batchprocesses[i].container.put(self.params['batch_size'])

                        self.batchprocesses[i].start_process()
                        
                        if (self.params['verbose']):
                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Started a process"
                            self.output_text.sig.emit(string)
            
            yield self.env.timeout(self.params['wait_time'])                        
            
    def run_load_in(self):
        while True:
            yield self.load_in_start
            for i in np.arange(self.params['batch_size']/self.params['cassette_size']): # how to ensure it is an integer?
                yield self.env.timeout(self.params['load_time_per_cassette'])
                yield self.input.container.get(self.params['cassette_size'])            
                yield self.boat_load_unload.container.put(self.params['cassette_size'])
            self.batches_loaded += 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event

            if (self.params['verbose']):
                string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Loaded batch"
                self.output_text.sig.emit(string)

    def run_load_out(self):
        while True:
            yield self.load_out_start
            for i in np.arange(self.params['batch_size']/self.params['cassette_size']): # how to ensure it is an integer?
                yield self.env.timeout(self.params['load_time_per_cassette']) 
                yield self.boat_load_unload.container.get(self.params['cassette_size']) 
                yield self.output.container.put(self.params['cassette_size'])
                self.transport_counter += self.params['cassette_size']
            self.batches_loaded -= 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event            

            if (self.params['verbose']):            
                string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Unloaded batch"
                self.output_text.sig.emit(string)