# -*- coding: utf-8 -*-
from __future__ import division
from batchlocations.BatchContainer import BatchContainer
import simpy

class WaferBin(object):
        
    def __init__(self, _env, _output=None, _params = {}):
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []        
        
        self.params = {}
        self.params['specification'] = "WaferBin is an imaginary machine that accepts cassettes and places them in an infinitely sized container."
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['batch_size'] = 100
        self.params['batch_size_desc'] = "Number of units in a single batch"
        self.params['max_batch_no'] = 4
        self.params['max_batch_no_desc'] = "Number of input batch positions"
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between wafer removal attempts (seconds)"
        self.params['verbose'] = False
        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool"
        self.params.update(_params)
        
        #if (self.params['verbose']):
        #    string = str(self.env.now) + " - [WaferBin][" + self.params['name'] + "] Added a wafer bin"
        #    self.output_text.sig.emit(string)
      
        self.input = BatchContainer(self.env,"input",self.params['batch_size'],self.params['max_batch_no'])
        self.output = InfiniteContainer(self.env,"output")
        
        self.env.process(self.run())

    #def report(self):
    #    string = "[WaferBin][" + self.params['name'] + "] Current level: " + str(self.output.container.level)
    #    self.output_text.sig.emit(string)

    def run(self):
        while True:
            if (self.input.container.level >= self.params['batch_size']):
                yield self.input.container.get(self.params['batch_size'])
                yield self.output.container.put(self.params['batch_size'])                
            yield self.env.timeout(self.params['wait_time'])    
        
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):
        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)