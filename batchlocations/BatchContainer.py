# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:55:31 2014

@author: rnaber
"""        

from __future__ import division
#import simpyx as simpy
import simpy
         
class BatchContainer(object):
    # Generic idle container, mainly for input and output buffers that do not require a resource lock,
    # a process time or a process_finished tag

    def __init__(self, env, name="", batch_size=1, max_batch_no=1):
        
        self.env = env
        self.name = name
        self.batch_size = batch_size
        self.buffer_size = batch_size*max_batch_no        
        self.process_counter = 0 # for counting processed units
        self.container = simpy.Container(self.env,self.batch_size*max_batch_no,init=0)
        self.oper_resource = simpy.Resource(self.env, 1) # resource to disentangle multiple operators       
            
    def space_available(self,added_units):
        if ((self.container.level + added_units) <= (self.buffer_size)):
            return True
        else:
            return False       