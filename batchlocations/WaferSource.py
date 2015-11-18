# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer

class WaferSource(QtCore.QObject):

    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Source"];
                       B [label = "Output"];
                       A -> B;                    
                       } """       

        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
WaferSource is an imaginary machine that sources stacks of wafers.
The user can set a time period between sourcing attempts and a time limit after which the sourcing ends.\n
<h3>Description of the algorithm</h3>
There is one simple loop that consists of three steps:
<ol>
<li>Check if a time limit has been set and whether it has been reached. Send message and exit loop if the latter is true.</li>
<li>If the output container is empty insert a new wafer stack</li>
<li>Wait for a defined period of time</li>
</ol>
\n
        """        
        
        self.params['name'] = ""
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = "Number of units in a single stack"
        self.params['batch_size_type'] = "configuration"
        self.params['time_limit'] = 0
        self.params['time_limit_desc'] = "Time limit for sourcing batches (seconds) (0 to disable function)"
        self.params['time_limit_type'] = "automation"
        self.params['wait_time'] = 10
        self.params['wait_time_desc'] = "Wait period between wafer sourcing attempts (seconds) (1 sec minimum)"
        self.params['wait_time_type'] = "automation"
        self.params.update(_params)
        
        if (self.params['wait_time'] == 0): # enforce minimum waiting time
            self.params['wait_time'] = 1
        
        self.batch_size = self.params['batch_size']
        self.process_counter = 0

        self.output = BatchContainer(self.env,"output",self.batch_size,1)
        self.env.process(self.run())        

    def report(self):
        return

    def prod_volume(self):
        return self.output.process_counter
        
    def run(self):
        time_limit = self.params['time_limit']
        batch_size = self.params['batch_size']
        wait_time = self.params['wait_time']
        
        while True:
            
            if (time_limit > 0) and (self.env.now >= time_limit):   
                string = str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Time limit reached"
                self.output_text.sig.emit(string)
                break
            
            if (not self.output.container.level):
                yield self.output.container.put(batch_size)
                self.output.process_counter += batch_size
                
#                string = str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Performed refill" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG
                    
            yield self.env.timeout(wait_time)        