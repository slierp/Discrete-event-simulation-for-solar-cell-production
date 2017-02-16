# -*- coding: utf-8 -*-
from PyQt5 import QtCore

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
        start_time = self.start_time # local copy to reduce access events to global variable

        # Generate warning for batch size mismatch
        faulty_connections = 0        
        for i in self.batchconnections:
            if not (self.batchconnections[i][0].output.batch_size == self.batchconnections[i][1].input.batch_size):
                faulty_connections += 1
                
        if faulty_connections:
            string = "[Operator][" + self.params['name'] + "] WARNING: "
            string += str(faulty_connections) + " tool connections have dissimilar cassette or stack size at source and destination."
            string += "It may be impossible to fill the destination input, which could then prevent the destination tool from starting."
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

                    if (no_batches_for_transport < self.batchconnections[i][4]):
                        # abort transport if not enough batches available
                        continue
                    elif (no_batches_for_transport > self.batchconnections[i][5]):
                        # limit transport to size if higher than user set maximum
                        no_batches_for_transport = self.batchconnections[i][5]
                    
                    if self.batchconnections[i][0].output.oper_resource.count or self.batchconnections[i][1].input.oper_resource.count:
                        # if one or both resources are in use then abort
                        continue
                    
                    if start_time < 0:
                        self.start_time = self.env.now
                        start_time = self.start_time
                    
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

            if start_time >= 0:
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
            
        self.utilization.append(self.transport_counter)            