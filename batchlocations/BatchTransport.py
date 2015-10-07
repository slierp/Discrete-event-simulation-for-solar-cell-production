# -*- coding: utf-8 -*-
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

        self.params = {}
        self.params['name'] = ""
        self.params['batch_size'] = 1
        self.params['wait_time'] = 60 # simulation runs much faster with higher values!!! 
        self.params.update(_params)

        self.name = self.params['name'] # for backward compatibility / to be removed
        self.transport_counter = 0     
            
        self.env.process(self.run())
    
    def run(self):
        batch_size = self.params['batch_size']
        wait_time = self.params['wait_time']
        
        while True:
            for i in range(len(self.batchconnections)):
                if isinstance(self.batchconnections[i][0],BatchContainer):
                    # load-in from BatchContainer to BatchProcess
                    if (self.batchconnections[i][0].container.level >= batch_size) & \
                            self.batchconnections[i][1].space_available(batch_size) & \
                            self.batchconnections[i][1].status:                            
                            
                        with self.batchconnections[i][1].resource.request() as request_output:
                            yield request_output
                        
                            yield self.batchconnections[i][0].container.get(batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size
                            yield self.batchconnections[i][1].container.put(batch_size)
                            self.batchconnections[i][1].start_process()
                            
#                            string =  str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from " #DEBUG
#                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG                                   

                elif isinstance(self.batchconnections[i][1],BatchContainer):
                    # load-out from BatchProcess into BatchContainer 
                    if (self.batchconnections[i][0].container.level >= batch_size) & \
                            self.batchconnections[i][1].space_available(batch_size) & \
                            self.batchconnections[i][0].process_finished & \
                            self.batchconnections[i][0].status:

                        with self.batchconnections[i][0].resource.request() as request_input:
                            yield request_input
                        
                            yield self.batchconnections[i][0].container.get(batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size
                            yield self.batchconnections[i][1].container.put(batch_size)
                            self.batchconnections[i][0].process_finished = 0
                            self.batchconnections[i][0].check_downtime()
                            
#                            string = str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from " #DEBUG
#                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG                                    
                                
                elif (isinstance(self.batchconnections[i][0],BatchProcess)) & \
                        (isinstance(self.batchconnections[i][1],BatchProcess)):
                    # transport from BatchProcess to BatchProcess
                    # only call if you're sure in- and output are BatchProcess
                    if (self.batchconnections[i][0].container.level >= batch_size) & \
                            self.batchconnections[i][1].space_available(batch_size) & \
                            self.batchconnections[i][0].process_finished & \
                            self.batchconnections[i][0].status & self.batchconnections[i][1].status:
                        #parentheses are crucial
                    
                        with self.batchconnections[i][0].resource.request() as request_input, \
                            self.batchconnections[i][1].resource.request() as request_output:
                            yield request_input                                    
                            yield request_output
                            
                            yield self.batchconnections[i][0].container.get(batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size                            
                            yield self.batchconnections[i][1].container.put(batch_size)                        

                            self.batchconnections[i][0].process_finished = 0
                            self.batchconnections[i][0].check_downtime()
                            self.batchconnections[i][1].start_process()
                            
#                            string = str(self.env.now) + " [BatchTransport][" + self.params['name'] + "] Transport from " #DEBUG
#                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG                                   
                    
            yield self.env.timeout(wait_time)
            
            