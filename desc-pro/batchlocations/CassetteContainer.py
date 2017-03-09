# -*- coding: utf-8 -*-
import simpy
         
class CassetteContainer(object):
    # Idle container for cassettes, used for input and output tool buffers

    def __init__(self, env, name="", max_cass_in=0, max_cass_out=0, buffer=False):
        # if in/out max value is set to zero then that in- or output will not exist
        
        self.env = env
        self.name = name
        self.max_cass_in = max_cass_in
        self.max_cass_out = max_cass_out
        self.process_counter = 0 # for counting processed units
        self.oper_resource = simpy.Resource(self.env, 1) # resource to disentangle multiple operators       

        if (max_cass_in): # stores cassette number references
            self.input = simpy.Store(self.env,self.max_cass_in)
        
        if (max_cass_out): # stores cassette number references
            self.output = simpy.Store(self.env,self.max_cass_out)
            
        if buffer:
            self.output = self.input
                                           
    def space_available_input(self,added_units):
        if (len(self.input.items)+added_units) <= self.max_cass_in:
            return True
        else:
            return False       

    def space_available_output(self,added_units):
        if (len(self.output.items)+added_units) <= self.max_cass_out:
            return True
        else:
            return False