# -*- coding: utf-8 -*-
import simpy
import collections
         
class CassetteContainer(object):
    # Idle container for cassettes, used for input and output tool buffers

    def __init__(self, env, name="", max_cass_no=1):
        
        self.env = env
        self.name = name
        self.buffer_size = max_cass_no
        self.store = simpy.Store(self.env,max_cass_no)
        self.oper_resource = simpy.Resource(self.env, 1) # resource to disentangle multiple operators       
        self.input_belt = collections.deque([-1] * max_cass_no)
        self.load_unload = -1
        self.output_belt = collections.deque([-1] * max_cass_no)
                                           
    def space_available(self,added_units):
        if ((len(self.store.items) + added_units) <= (self.store.capacity)):
            return True
        else:
            return False       
        
    def put(self):
        pass
    
    def get(self):
        pass
    
    def empty_cassettes(self):
        pass
    
    def full_cassettes(self):
        pass