# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 09:01:54 2014

@author: rnaber
"""

from __future__ import division
from batchlocations.BatchContainer import BatchContainer

class WaferSource(object):

    def __init__(self, env, _params = {}):   
        
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['batch_size'] = 400
        self.params['time_limit'] = 0
        self.params['wait_time'] = 60
        self.params['verbose'] = False
        self.params.update(_params)
        
        self.batch_size = self.params['batch_size']
        self.process_counter = 0
       
        if (self.params['verbose']):
            print str(self.env.now) + " - [WaferSource][" + self.params['name'] + "] Added a wafer source"
        
        self.output = BatchContainer(self.env,"output",self.batch_size,1)
        self.env.process(self.run())

    def report(self,output):
        string = "[WaferSource][" + self.params['name'] + "] Units sourced: " + str(self.output.process_counter - self.output.container.level)
        output.sig.emit(string)
        
    def run(self):
        while True:
            
            if (self.params['time_limit'] > 0) & (self.env.now >= self.params['time_limit']):                
                print str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Time limit reached"
                break
            
            if (not self.output.container.level):
                yield self.output.container.put(self.params['batch_size'])
                self.output.process_counter += self.params['batch_size']
                
                if (self.params['verbose']):
                    print str(self.env.now) + " [WaferSource][" + self.params['name'] + "] Performed refill"
            
            yield self.env.timeout(self.params['wait_time'])        