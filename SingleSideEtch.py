# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 13:55:53 2014

@author: rnaber

TODO
Output put action should yield to two things: put and timer
If time_limit is reached because there is no output space available, destroy wafer?

"""

from __future__ import division
from BatchContainer import BatchContainer
import numpy as np

class SingleSideEtch(object):
    # unlike waferunstacker or printing line this machine runs continuously, independent of whether there is an output
    # position available or not, so the output automation cannot function as a master of the input
    # there are several of types of automation
    # assumed now is that each lane is fed separately with new cassettes, with no interruption between cassettes
    # (i.e. cassettes stacked on top of each other)

    def __init__(self, env, name="", no_of_lanes=5, tool_length=10, belt_speed = 1.8, unit_distance=0.2,
                 cassette_size=100, max_cassette_no=8):    
        
        self.env = env
        self.name = name
        self.no_of_lanes = no_of_lanes
        self.tool_length = tool_length # in meters
        self.belt_speed = belt_speed # in meters per second
        self.unit_distance = unit_distance # required distance from unit edge to unit edge in meters
        self.cassette_size = cassette_size
        self.max_cassette_no = max_cassette_no
        self.transport_counter = 0
        self.start_time = self.env.now
        print str(self.env.now) + " - [SingleSideEtch][" + self.name + "] Added a single side etch"        
                
        self.input = BatchContainer(self.env,"input",self.cassette_size,self.max_cassette_no)                  
        self.output = BatchContainer(self.env,"output",self.cassette_size,self.max_cassette_no)
        
        self.idle_times = {}
        for i in np.arange(self.no_of_lanes):
            self.env.process(self.run_one_lane(i))
            self.idle_times[i] = 0

    def report(self):
        print "[SingleSideEtch][" + self.name + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        for i in self.idle_times:
            idle_time = 100*self.idle_times[i]/(self.env.now-self.start_time)
            print "[SingleSideEtch][" + self.name + "][lane" + str(i) + "] Idle time: " + str(np.round(idle_time,1)) + " %"

    def run_one_lane(self, lane_number):       
        while True:
            if (self.input.container.level > 0):
                yield self.input.container.get(1)
                self.env.process(self.run_wafer_instance(lane_number))
                yield self.env.timeout(60*self.unit_distance/self.belt_speed) # same lane cannot except new unit until after x seconds
            else:                
                yield self.env.timeout(1)
                self.idle_times[lane_number] += 1
                
    def run_wafer_instance(self, lane_number):
        yield self.env.timeout(60*self.tool_length/self.belt_speed)
        yield self.output.container.put(1) 
        self.transport_counter += 1
        #print str(self.env.now) + " - [SingleSideEtch][Lane " + str(lane_number) + "] Processed one unit"