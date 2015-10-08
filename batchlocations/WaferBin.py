# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import simpy

class WaferBin(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Bin"];
                       A -> B;                    
                       } """      
        
        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
WaferBin is an imaginary machine that accepts cassettes and places them in an infinitely sized container.\n
        """         
        
        self.params['name'] = ""
        self.params['batch_size'] = 100
        self.params['batch_size_desc'] = "Number of units in a single cassette"
        self.params['batch_size_type'] = "configuration"
        self.params['max_batch_no'] = 4
        self.params['max_batch_no_desc'] = "Number of input cassette positions"
        self.params['max_batch_no_type'] = "configuration"
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between wafer removal attempts (seconds)"
        self.params['wait_time_type'] = "automation"
        self.params.update(_params)
        
#        string = str(self.env.now) + " - [WaferBin][" + self.params['name'] + "] Added a wafer bin" #DEBUG
#        self.output_text.sig.emit(string) #DEBUG
      
        self.input = BatchContainer(self.env,"input",self.params['batch_size'],self.params['max_batch_no'])
        self.output = InfiniteContainer(self.env,"output")
        
        self.env.process(self.run())

    def report(self):
        string = "[WaferBin][" + self.params['name'] + "] Current level: " + str(self.output.container.level)
        self.output_text.sig.emit(string)

    def prod_volume(self):
        return self.output.container.level
        
    def run(self):
        batch_size = self.params['batch_size']
        wait_time = self.params['wait_time']
        
        while True:
            if (self.input.container.level >= batch_size):
                yield self.input.container.get(batch_size)
                yield self.output.container.put(batch_size)                
            yield self.env.timeout(wait_time)    
        
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):
        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)