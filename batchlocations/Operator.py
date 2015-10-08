# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore

class Operator(QtCore.QObject):
    #Operator checks regularly whether he/she can perform a batch transfer action and then carries it out
        
    def __init__(self, _env, _batchconnections = None, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.batchconnections = _batchconnections

        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
An operator instance functions as a wafer transporter between tools.
It will regularly check whether a transport action is possible, considering the input and output status of the various tools that it was assigned to.
If no transport was possible then it will wait a set amount of time before trying again.\n
        """
        
        self.params['name'] = ""
        self.params['min_no_batches'] = 1
        self.params['min_no_batches_desc'] = "Minimum number of batches needed for transport action"
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between transport attempts (seconds)"
        self.params.update(_params)
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.idle_time = 0
            
        self.env.process(self.run())        

    def run(self):
        continue_loop = False
        min_no_batches = self.params['min_no_batches']
        wait_time = self.params['wait_time']
        
        for i in self.batchconnections:
            if self.batchconnections[i][0].output.batch_size > self.batchconnections[i][1].input.batch_size:
                string = "[Operator][" + self.params['name'] + "] <span style=\"color: red\">WARNING: "
                string += "Tool connection has larger cassette or stack size at source than at destination."
                string += "It may be impossible to fill the destination input, which then prevents the destination tool from starting.</span>"
                self.output_text.sig.emit(string)
        
        while True:
            for i in self.batchconnections:
                units_needed = self.batchconnections[i][1].input.buffer_size - self.batchconnections[i][1].input.container.level
                units_available = self.batchconnections[i][0].output.container.level
                
                if (units_needed >= units_available):
                    units_for_transport = units_available
                else:
                    units_for_transport = units_needed
                
                if (units_for_transport >= self.batchconnections[i][0].output.batch_size):
                    no_batches_for_transport = units_for_transport // self.batchconnections[i][0].output.batch_size

                    if (no_batches_for_transport < min_no_batches):
                        # abort transport if not enough batches available
                        continue
                    
                    request_time  = self.env.now
                    with self.batchconnections[i][0].output.oper_resource.request() as request_input, \
                        self.batchconnections[i][1].input.oper_resource.request() as request_output:
                        yield request_input
                        yield request_output
                        
                        if (self.env.now > request_time):
                            # if requests were not immediately granted, we cannot be sure if the source and destination
                            # have not changed, so abort
                            continue
                        
                        yield self.batchconnections[i][0].output.container.get(no_batches_for_transport*self.batchconnections[i][0].output.batch_size)                                          
                    
                        yield self.env.timeout(self.batchconnections[i][2] + self.batchconnections[i][3]*no_batches_for_transport)
                        self.transport_counter += no_batches_for_transport*self.batchconnections[i][0].output.batch_size                    
                        yield self.batchconnections[i][1].input.container.put(no_batches_for_transport*self.batchconnections[i][0].output.batch_size)
                    
                        continue_loop = True

#                        string = str(self.env.now) + " - [Operator][" + self.params['name'] + "] Batches transported: " #DEBUG
#                        string += str(no_batches_for_transport) #DEBUG
#                        self.output_text.sig.emit(string) #DEBUG                           

            if (continue_loop):
                continue_loop = False
                continue
            
            yield self.env.timeout(wait_time)
            self.idle_time += wait_time

    def report(self):        
        string = "[Operator][" + self.params['name'] + "] Units transported: " + str(self.transport_counter)
        self.output_text.sig.emit(string)
        
#        string = "[Operator][" + self.params['name'] + "] Transport time: " + str(round(100-100*self.idle_time/(self.env.now-self.start_time),1)) + " %" #DEBUG
#        self.output_text.sig.emit(string) #DEBUG