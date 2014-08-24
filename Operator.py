# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 08:38:24 2014

@author: rnaber

TODO

Implement in a more detailed way
Operator should have a particular location at any time
- time to walk to other location should be defined (with some randomness)
- time to perform work at each location should be defined
- have the time also increase with the number of units
- implement shift changes, breaks, factory shut-downs...

"""

from __future__ import division

class Operator(object):
    #Operator checks regularly whether he/she can perform a batch transfer action and then carries it out
        
    def __init__(self, env, batchconnections, name=""):
        self.env = env
        self.batchconnections = batchconnections
        self.name = name
        self.transport_counter = 0            
        self.wait_time = 60
        print str(self.env.now) + " - [Operator][" + self.name + "] Added an operator"
        self.env.process(self.run())        

    def run(self):
        while True:
            for i in self.batchconnections:
                units_needed = self.batchconnections[i][1].input.buffer_size - self.batchconnections[i][1].input.container.level
                units_available = self.batchconnections[i][0].output.container.level
                
                if (units_needed >= units_available):
                    units_for_transport = units_available
                else:
                    units_for_transport = units_needed
                
                if (units_for_transport > 0):                     
                    #print str(self.env.now) + " - [Operator][" + self.name + "] Moving " + str(units_for_transport) + " units"
                    yield self.batchconnections[i][0].output.container.get(units_for_transport)
                    yield self.env.timeout(self.batchconnections[i][2])
                    self.transport_counter += units_for_transport
                    #print str(self.env.now) + " - [Operator][" + self.name + "] End transport"
                    yield self.batchconnections[i][1].input.container.put(units_for_transport)
                    
            yield self.env.timeout(self.wait_time)

    def report(self):
        print "[Operator][" + self.name + "] Work done: " + str(self.transport_counter)            