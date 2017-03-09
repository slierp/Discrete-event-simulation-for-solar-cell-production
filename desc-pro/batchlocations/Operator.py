# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.CassetteContainer import CassetteContainer

class Operator(QtCore.QObject):
    #Operator checks regularly whether he/she can perform a batch transfer action and then carries it out
        
    def __init__(self, _env, _batchconnections = None, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.batchconnections = _batchconnections
        self.utilization = []

        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
An operator instance functions as a wafer transporter between tools.
It will regularly check whether a transport action is possible, considering the input and output status of the various tools that it was assigned to.
If no transport was possible then it will wait a set amount of time before trying again.\n
<h3>Description of the algorithm</h3>
There is one loop that describes the functionality of the operator.
The first step in this loop is to go over all the tool connections assigned to this operator and do the following:
<ol>
<li>For each connection check if wafers are available at the source and space available at destination</li>
<li>Continue if it is possible to transport more than one cassette, or the user defined minimum of wafers for that connection</li>
<li>Request a lock on the intended input and output to prevent other operators from performing actions on them</li>
<li>If the lock was not provided immediately then another operator may have done something, so discontinue the transport</li>
<li>Transport the wafers with a certain time delay according to the settings for this connection</li>
</ol>
If none of the tool connections allowed for a transport event, then the operator will wait for a set amount of time before restarting the loop.
\n
        """
        
        self.params['name'] = ""
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between transport attempts (seconds)"
        self.params.update(_params)
        
        self.transport_counter = 0
        self.start_time = -1
        self.idle_time = 0
            
        self.env.process(self.run())        

    def run(self):

        continue_loop = False
        wait_time = self.params['wait_time']
        start_time_set = False

        # Generate warning for batch size mismatch
#        faulty_connections = 0        
#        for i in self.batchconnections:
#            if not (self.batchconnections[i][0].output.batch_size == self.batchconnections[i][1].input.batch_size):
#                faulty_connections += 1
#                
#        if faulty_connections:
#            string = "[Operator][" + self.params['name'] + "] WARNING: "
#            string += str(faulty_connections) + " tool connections have dissimilar cassette or stack size at source and destination."
#            string += "It may be impossible to fill the destination input, which could then prevent the destination tool from starting."
#            self.output_text.sig.emit(string)
        
        while True:
            for i in self.batchconnections:
                transport_time = self.batchconnections[i][2]
                time_per_unit = self.batchconnections[i][3]
                min_units = self.batchconnections[i][4]
                max_units = self.batchconnections[i][5]

                if len(self.batchconnections[i]) == 6: # forward transport of cassette or stack 
                    origin = self.batchconnections[i][0].output
                    destination = self.batchconnections[i][1].input                
                    
                    if isinstance(origin,CassetteContainer):
                        cassette_transport = True # cassette transport
                    else:
                        cassette_transport = False # stack transport
                    
                else: # return transport of cassette
                    cassette_transport = True
                    origin = self.batchconnections[i][0].input
                    destination = self.batchconnections[i][1].output
                
                if cassette_transport:
                    buffer = destination.max_cass_in
                    level = len(destination.input.items)
                    units_for_transport = min(buffer - level,len(origin.output.items))                  
                else:
                    buffer = destination.buffer_size
                    level = destination.container.level
                    units_for_transport = min(buffer - level,origin.container.level)
                
#                if (units_needed >= units_available):
#                    units_for_transport = units_available
#                else:
#                    units_for_transport = units_needed
               
                continue_action = False

                if cassette_transport:
                    if units_for_transport > 0:
                        no_batches_for_transport = units_for_transport
                        continue_action = True
                elif (units_for_transport >= origin.batch_size):
                    no_batches_for_transport = units_for_transport // origin.batch_size
                    continue_action = True
                else:
                    continue_action = False
                    
#                if (units_for_transport >= self.batchconnections[i][0].output.batch_size):
#                    no_batches_for_transport = units_for_transport // self.batchconnections[i][0].output.batch_size

                if continue_action:
                    continue_action = False
                                                                                            
                    if (no_batches_for_transport < min_units):
                        # abort transport if not enough batches available
                        continue
                    elif (no_batches_for_transport > max_units):
                        # limit transport to size if higher than user set maximum
                        no_batches_for_transport = max_units
                    
                    if origin.oper_resource.count or destination.oper_resource.count:
                        # if one or both resources are in use then abort
                        continue
                    
                    if not start_time_set:
                        self.start_time = self.env.now
                        start_time_set = True
                    
                    request_time  = self.env.now
                    with origin.oper_resource.request() as request_input, \
                        destination.oper_resource.request() as request_output:
                        yield request_input
                        yield request_output
                        
                        if (self.env.now > request_time):
                            # if requests were not immediately granted, we cannot be sure if the source and destination
                            # have not changed, so abort
                            continue
                        
                        if cassette_transport:
                            cassettes = []

                            for j in range(no_batches_for_transport):
                                cassette = yield origin.output.get()
                                cassettes.append(cassette)
                            
                            yield self.env.timeout(transport_time + time_per_unit*no_batches_for_transport)
                            #self.transport_counter += no_batches_for_transport

                            for k in cassettes:
                                yield destination.input.put(k)                            
                        else:
                            batch_size = origin.batch_size
                            yield origin.container.get(no_batches_for_transport*batch_size)                                          
                    
                            yield self.env.timeout(transport_time + time_per_unit*no_batches_for_transport)
                            #self.transport_counter += no_batches_for_transport*self.batchconnections[i][0].output.batch_size                    
                            yield destination.container.put(no_batches_for_transport*batch_size)
                    
                        continue_loop = True

#                        string = str(self.env.now) + " - [Operator][" + self.params['name'] + "] Batches transported: " #DEBUG
#                        string += str(no_batches_for_transport) #DEBUG
#                        self.output_text.sig.emit(string) #DEBUG                           

            if (continue_loop):
                continue_loop = False
                continue

            if start_time_set:
                self.idle_time += wait_time            
                
            yield self.env.timeout(wait_time)
        

    def report(self):        
        self.utilization.append("Operator")
        self.utilization.append(self.params['name'])
        self.utilization.append("n/a")
        
        if self.start_time >= 0:
            util = 100-(100*self.idle_time/(self.env.now-self.start_time))
            self.utilization.append(round(util,1))
        else:
            self.utilization.append(0)
            
#        self.utilization.append(self.transport_counter)            
        self.utilization.append("n/a")