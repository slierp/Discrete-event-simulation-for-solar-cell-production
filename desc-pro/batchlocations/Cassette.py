# -*- coding: utf-8 -*-
import simpy
         
class Cassette(object):

    def __init__(self, env, cass_size=100):
        
        self.env = env
        self.cass_size = cass_size
        self.container = simpy.Container(self.env,self.cass_size,init=0)
            
    def space_available(self,added_units):
        if ((self.container.level + added_units) <= (self.cass_size)):
            return True
        else:
            return False       