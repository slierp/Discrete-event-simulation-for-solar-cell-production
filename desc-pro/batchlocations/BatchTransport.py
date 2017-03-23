# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchProcess import BatchProcess
#from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer

class BatchTransport(QtCore.QObject):
    # For simple one-way transports

    def __init__(self,  _env, _batchconnections, _output=None, _params = {}):      
        QtCore.QObject.__init__(self)
        self.env = _env
        self.batchconnections = _batchconnections        
        self.output_text = _output     

        self.params = {}
        self.params['name'] = ""
        self.params['type'] = "BatchTransport"
        self.params['batch_size'] = 1
        self.params['cassette_size'] = 1
        self.params['wait_time'] = 60 # simulation runs much faster with higher values!!! 
        self.params.update(_params)

        self.name = self.params['name'] # for backward compatibility / to be removed
        self.transport_counter = 0     
            
        self.env.process(self.run())
    
    def run(self):
        batch_size = self.params['batch_size']
        cassette_size = self.params['cassette_size']
        wait_time = self.params['wait_time']
        continue_loop = False        
        
        while True:
            for i in range(len(self.batchconnections)):
                if isinstance(self.batchconnections[i][0],CassetteContainer):
                    # load-in from CassetteContainer to BatchProcess
                    if (len(self.batchconnections[i][0].output.items) >= batch_size) & \
                            self.batchconnections[i][1].space_available(batch_size) & \
                            self.batchconnections[i][1].status:                            
                            
                        with self.batchconnections[i][1].resource.request() as request_output:
                            yield request_output
                        
                            cassettes = []
                            for j in range(batch_size):
                                cassette = yield self.batchconnections[i][0].output.get()
                                cassettes.append(cassette)
                                
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size*cassette_size
                            
                            for k in cassettes:
                                yield self.batchconnections[i][1].store.put(k)
                                
                            self.batchconnections[i][1].start_process()
                            continue_loop = True
                            
                            string =  str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Transport from " #DEBUG
                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
                            #self.output_text.sig.emit(string) #DEBUG                                   

                elif isinstance(self.batchconnections[i][1],CassetteContainer):
                    # load-out from BatchProcess into CassetteContainer 
                    if (len(self.batchconnections[i][0].store.items) >= batch_size) & \
                            self.batchconnections[i][1].space_available_input(batch_size) & \
                            self.batchconnections[i][0].process_finished & \
                            self.batchconnections[i][0].status:

                        with self.batchconnections[i][0].resource.request() as request_input:
                            yield request_input

                            cassettes = []
                            for j in range(batch_size):
                                cassette = yield self.batchconnections[i][0].store.get()
                                cassettes.append(cassette)
                        
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size*cassette_size

                            for k in cassettes:
                                yield self.batchconnections[i][1].input.put(k)
                            
                            self.batchconnections[i][0].process_finished = 0
                            self.batchconnections[i][0].check_downtime()
                            continue_loop = True
                            
                            string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Transport from " #DEBUG
                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
                            #self.output_text.sig.emit(string) #DEBUG                                    
                                
                elif (isinstance(self.batchconnections[i][0],BatchProcess)) & \
                        (isinstance(self.batchconnections[i][1],BatchProcess)):
                    # transport from BatchProcess to BatchProcess
                    # only call if you're sure in- and output are BatchProcess
                    if (len(self.batchconnections[i][0].store.items) >= batch_size) & \
                            self.batchconnections[i][1].space_available(batch_size) & \
                            self.batchconnections[i][0].process_finished & \
                            self.batchconnections[i][0].status & self.batchconnections[i][1].status:
                        #parentheses are crucial
                    
                        with self.batchconnections[i][0].resource.request() as request_input, \
                            self.batchconnections[i][1].resource.request() as request_output:
                            yield request_input                                    
                            yield request_output

                            cassettes = []
                            for j in range(batch_size):
                                cassette = yield self.batchconnections[i][0].store.get()
                                cassettes.append(cassette)
                            
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += batch_size*cassette_size                         

                            for k in cassettes:
                                yield self.batchconnections[i][1].store.put(k)

                            self.batchconnections[i][0].process_finished = 0
                            self.batchconnections[i][0].check_downtime()
                            self.batchconnections[i][1].start_process()
                            continue_loop = True
                            
                            string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] Transport from " #DEBUG
                            string += self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended" #DEBUG
                            #self.output_text.sig.emit(string) #DEBUG                                   

            if (continue_loop): # restart loop without waiting if a transport action was performed
                continue_loop = False
                continue
                    
            yield self.env.timeout(wait_time)
            
            