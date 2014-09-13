# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 11:56:44 2014

@author: rnaber
"""

from __future__ import division
from BatchContainer import BatchContainer
#import simpyx as simpy
import simpy

class WaferBin(object):
        
    def __init__(self, env, _params = {}):   
        
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['batch_size'] = 100
        self.params['max_batch_no'] = 4
        self.params['wait_time'] = 60
        self.params['verbose'] = False
        self.params.update(_params)
        
        if (self.params['verbose']):
            print str(self.env.now) + " - [WaferBin][" + self.params['name'] + "] Added a wafer bin"
        
        self.input = BatchContainer(self.env,"input",self.params['batch_size'],self.params['max_batch_no'])
        self.output = InfiniteContainer(self.env,"output")
        
        self.env.process(self.run())

    def report(self,output):
        string = "[WaferBin][" + self.params['name'] + "] Current level: " + str(self.output.container.level)
        output.sig.emit(string)

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