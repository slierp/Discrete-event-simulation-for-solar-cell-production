# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 09:01:54 2014

@author: rnaber
"""

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

        self.params = {}
        self.params['specification'] = self.tr("WaferSource is an imaginary machine that sources stacks of wafers.")
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = self.tr("Number of units in a single batch")
        self.params['time_limit'] = 0
        self.params['time_limit_desc'] = self.tr("Time limit for sourcing batches (seconds)")
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = self.tr("Wait period between wafer sourcing attempts (seconds)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)
        
        self.batch_size = self.params['batch_size']
        self.process_counter = 0        
       
        if (self.params['verbose']):
            string = str(self.env.now) + " - [WaferSource][" + self.params['name'] + "] Added a wafer source"
            self.output_text.sig.emit(string)
        
        self.output = BatchContainer(self.env,"output",self.batch_size,1)
        self.env.process(self.run())        

    def report(self):
        string = "[WaferSource][" + self.params['name'] + "] Units sourced: " + str(self.output.process_counter - self.output.container.level)
        self.output_text.sig.emit(string)
        
    def run(self):
        while True:
            
            if (self.params['time_limit'] > 0) & (self.env.now >= self.params['time_limit']):                
                string = str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Time limit reached"
                self.output_text.sig.emit(string)
                break
            
            if (not self.output.container.level):
                yield self.output.container.put(self.params['batch_size'])
                self.output.process_counter += self.params['batch_size']
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Performed refill"
                    self.output_text.sig.emit(string)
                    
            yield self.env.timeout(self.params['wait_time'])        