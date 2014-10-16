# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:56:30 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class BatchTransport(QtCore.QObject):
    # For simple one-way transports

    def __init__(self,  _env, _batchconnections, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.batchconnections = _batchconnections        
        self.output_text = _output
        self.idle_times = [] 

        self.params = {}
        self.params['name'] = ""
        self.params['batch_size'] = 1
        self.params['wait_time'] = 60 # simulation runs much faster with higher values!!! 
        self.params['verbose'] = False
        self.params.update(_params)

        self.name = self.params['name'] # for backward compatibility / to be removed
        self.transport_counter = 0     
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [BatchTransport][" + self.params['name'] + "] Added transporter"
            self.output_text.sig.emit(string)
            
        self.env.process(self.run())
    
    def run(self):
        while True:
            for i in range(len(self.batchconnections)):
                if isinstance(self.batchconnections[i][0],BatchContainer):
                    # load-in from BatchContainer to BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.params['batch_size']) & \
                            self.batchconnections[i][1].space_available(self.params['batch_size']):
                                                  
                        with self.batchconnections[i][1].resource.request() as request_output:
                            yield request_output
                        
                            yield self.batchconnections[i][0].container.get(self.params['batch_size'])
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.params['batch_size']
                            yield self.batchconnections[i][1].container.put(self.params['batch_size'])
                            self.batchconnections[i][1].start_process()
                            
                            if (self.params['verbose']):
                                string =  str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from "
                                string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"
                                self.output_text.sig.emit(string)                                    

                elif isinstance(self.batchconnections[i][1],BatchContainer):
                    # load-out into BatchContainer to BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.params['batch_size']) & \
                            self.batchconnections[i][1].space_available(self.params['batch_size']) & \
                            self.batchconnections[i][0].process_finished:

                        with self.batchconnections[i][0].resource.request() as request_input:
                            yield request_input
                        
                            yield self.batchconnections[i][0].container.get(self.params['batch_size'])
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.params['batch_size']
                            yield self.batchconnections[i][1].container.put(self.params['batch_size'])
                            self.batchconnections[i][0].process_finished = 0
                            
                            if (self.params['verbose']):
                                string = str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from "
                                string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"
                                self.output_text.sig.emit(string)                                     
                                
                elif (isinstance(self.batchconnections[i][0],BatchProcess)) & \
                        (isinstance(self.batchconnections[i][1],BatchProcess)):
                    # transport from BatchProcess to BatchProcess
                    # only call if you're sure in- and output are BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.params['batch_size']) & \
                            self.batchconnections[i][1].space_available(self.params['batch_size']) & \
                            self.batchconnections[i][0].process_finished:                           
                        #parentheses are crucial
                    
                        with self.batchconnections[i][0].resource.request() as request_input, \
                            self.batchconnections[i][1].resource.request() as request_output:
                            yield request_input                                    
                            yield request_output
                            
                            yield self.batchconnections[i][0].container.get(self.params['batch_size'])
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.params['batch_size']                            
                            yield self.batchconnections[i][1].container.put(self.params['batch_size'])                        

                            self.batchconnections[i][0].process_finished = 0                    
                            self.batchconnections[i][1].start_process()
                            
                            if (self.params['verbose']):
                                string = str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from "
                                string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"
                                self.output_text.sig.emit(string)                                    
                    
            yield self.env.timeout(self.params['wait_time'])
            
            