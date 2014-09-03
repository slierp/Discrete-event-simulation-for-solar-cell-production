# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO

Add a function to calculate the number of wafers in the line at certain intervals
- wafer.bin - wafer.source after a certain time has passed for stabilization
- report an average value + calculate the investment of product in the line at any given time
- Calculate average pass-through by checking how long it takes for that amount of wafers to pass

Add a function to generate functioning lines in an easier way
- make a dict with all the types of machines
- define the line in another dict (order, number of tools, transfer time between tools)
- define operators in another dict, or automatically connect operators

Tools/locations to be added
- cassette to cassette transfer
- buffers
- printing line
- pecvd (to be implemented)
- wafer inspection tool? Perhaps combined with waferunstacker

Implement STORES instead of more abstract CONTAINERS?
- make a 'cassette' class and put those in stores
- cassette can be full or empty, have different sizes
- make a 'wafer' class and store these in cassette class, among others
- wafers can be processed or not processed, have a tool feed-in and out time, idle_time etc.

The end program should have a function to measure the maximum throughput of each tool
So with ever-present wafer supply and removal.

"""

from __future__ import division
from WaferSource import WaferSource
from WaferUnstacker import WaferUnstacker
from Operator import Operator
from WaferBin import WaferBin
from BatchTex import BatchTex
from TubeFurnace import TubeFurnace
from SingleSideEtch import SingleSideEtch
from TubePECVD import TubePECVD
from PrintLine import PrintLine
import simpy
import numpy as np

if __name__ == "__main__":      
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Solar cell manufacturing simulation"
            print "Options:"
            print "--h, --help  : Help message"
            exit()
        
    env = simpy.Environment()

    #import simpy.rt # if you are really patient
    #env = simpy.rt.RealtimeEnvironment(factor=0.1)
    #env = simpy.rt.RealtimeEnvironment(factor=1)
    
    batchlocations = {}
    batchlocations[0] = WaferSource(env,{'name' : '0'}) #, 'time_limit' : 10000})
    batchlocations[1] = WaferUnstacker(env,{'name' : '0'})
    batchlocations[2] = WaferUnstacker(env,{'name' : '1'})
    batchlocations[3] = BatchTex(env,{'name' : '0'})
    batchlocations[4] = TubeFurnace(env,{'name' : '0'})
    batchlocations[5] = TubeFurnace(env,{'name' : '1'})
    batchlocations[6] = SingleSideEtch(env,{'name' : '0'})
    batchlocations[7] = TubePECVD(env,{'name' : '0'})
    batchlocations[8] = TubePECVD(env,{'name' : '1'})
    batchlocations[9] = PrintLine(env,{'name' : '0'})
    batchlocations[10] = PrintLine(env,{'name' : '1'})
    #batchlocations[11] = WaferBin(env,{'name' : '0'})
    
    operators = {}    
    
    transport_time = 90
    batchconnections = {} #[machine1,machine2,transfer_time]
    batchconnections[0] = [batchlocations[0],batchlocations[1],transport_time]
    batchconnections[1] = [batchlocations[0],batchlocations[2],transport_time]   
    operators[0] = Operator(env,batchconnections,"operator0")

    batchconnections = {}
    batchconnections[0] = [batchlocations[1],batchlocations[3],transport_time]
    batchconnections[1] = [batchlocations[2],batchlocations[3],transport_time]
    operators[1] = Operator(env,batchconnections,"operator1")

    batchconnections = {}
    batchconnections[0] = [batchlocations[3],batchlocations[4],transport_time]
    batchconnections[1] = [batchlocations[3],batchlocations[5],transport_time]
    operators[2] = Operator(env,batchconnections,"operator2")

    batchconnections = {}
    batchconnections[0] = [batchlocations[4],batchlocations[6],transport_time]
    batchconnections[1] = [batchlocations[5],batchlocations[6],transport_time]
    operators[3] = Operator(env,batchconnections,"operator3")

    batchconnections = {}
    batchconnections[0] = [batchlocations[6],batchlocations[7],transport_time]
    batchconnections[1] = [batchlocations[6],batchlocations[8],transport_time]
    operators[4] = Operator(env,batchconnections,"operator4")

    batchconnections = {}
    batchconnections[0] = [batchlocations[7],batchlocations[9],transport_time]
    batchconnections[1] = [batchlocations[7],batchlocations[10],transport_time]
    batchconnections[2] = [batchlocations[8],batchlocations[9],transport_time]
    batchconnections[3] = [batchlocations[8],batchlocations[10],transport_time]
    operators[5] = Operator(env,batchconnections,"operator5")

    #time_limit = 10000
    time_limit = 60*60*24 # 1 day
    #time_limit = 60*60*24*7 # 1 week
    #time_limit = 60*60*24*30 # 1 month
    #time_limit = 60*60*24*365 # 1 year
    print "0% progress: 0 hours"
    for i in np.arange(1,11):        
        env.run(until=time_limit*i/10) # or perhaps do daily updates?
        if (i < 10):            
            print str(i*10) + "% progress: " + str(np.round(time_limit*i/36000,1)) + " hours"
        else:
            print "Finished at "  + str(np.round(env.now/3600,1)) + " hours"

    for i in batchlocations:
        batchlocations[i].report()

    for i in operators:
        operators[i].report()

    #print "Production volume: " + str(batchlocations[len(batchlocations)-1].output.container.level)
    #print "Average throughput (WPH): " + str(np.round(3600*batchlocations[len(batchlocations)-1].output.container.level/time_limit))
    
    print "Production volume: " + str(batchlocations[len(batchlocations)-1].output.container.level + batchlocations[len(batchlocations)-2].output.container.level)
    print "Average throughput (WPH): " + str(np.round(3600*(batchlocations[len(batchlocations)-1].output.container.level + batchlocations[len(batchlocations)-2].output.container.level)/time_limit))
        