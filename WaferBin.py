# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 11:56:44 2014

@author: rnaber
"""

from __future__ import division
#from BatchTransport import BatchTransport
#from BatchProcess import BatchProcess
from BatchContainer import BatchContainer
import simpy

class WaferBin(object):

    def __init__(self, env, name="", batch_size=100, max_batch_no=4):    
        
        self.env = env
        self.name = name
        self.batch_size = batch_size
        self.max_batch_no = max_batch_no
        self.wait_time = 60
        print str(self.env.now) + " - [WaferBin][" + self.name + "] Added a wafer bin"        
        
        self.input = BatchContainer(self.env,"input",self.batch_size,self.max_batch_no)
        self.output = InfiniteContainer(self.env,"output")
        
        self.env.process(self.run())

    def report(self):
        print "[WaferBin][" + self.name + "] Current level: " + str(self.output.container.level)

    def run(self):
        while True:            
            if (self.input.container.level >= self.batch_size):
                yield self.input.container.get(self.batch_size)
                yield self.output.container.put(self.batch_size)
            yield self.env.timeout(self.wait_time)    
        
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):
        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)