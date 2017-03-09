# -*- coding: utf-8 -*-
import simpy
         
class CassetteContainer(object):
    # Idle container for cassettes, used for input and output tool buffers

    def __init__(self, env, name="", max_cass=1, loop=False):
        # if in/out max value is set to zero then that in- or output will not exist
        
        self.env = env
        self.name = name
        self.max_cass = max_cass
        self.loop = loop
        self.process_counter = 0 # for counting processed units
        self.oper_resource = simpy.Resource(self.env, 1) # resource to disentangle multiple operators       

        # stores cassette number references
        self.input = simpy.Store(self.env,self.max_cass)
        
        if not loop:
            self.output = simpy.Store(self.env,self.max_cass)
        else:
            self.output = self.input
                                           
    def space_available_input(self,added_units):
        if (len(self.input.items)+added_units) <= self.max_cass:
            return True
        else:
            return False       

    def space_available_output(self,added_units):
        if self.loop:
            return False
        
        if (len(self.output.items)+added_units) <= self.max_cass:
            return True
        else:
            return False