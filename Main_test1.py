# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO

Implement a cart between machines - implement cart inside Operator class?
Add cassette to cassette transfer
How to implement screen-printing with plenty of down-time?

Implement STORES instead of more abstract CONTAINERS?
- make a 'cassette' class and put those in stores
- cassette can be full or empty, have different sizes
- make a 'wafer' class and store these in cassette class, among others
- wafers can be processed or not processed, have a tool feed-in and out time, idle_time etc.

Add a function to each tool to measure the maximum throughput? So with ever-present wafer supply and removal.

"""

from __future__ import division
from BatchTransport import BatchTransport
from BatchProcess import BatchProcess
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

    batchlocations = {}
    batchlocations[0] = WaferSource(env,{'batch_size' : 100}) # other machines need to to accept a multiple of this value
    #batchlocations[0] = WaferSource(env,{'batch_size' : 100, 'time_limit' : 1000})
    
    #batchlocations[1] = WaferUnstacker(env,{'verbose' : True})
    #batchlocations[1] = BatchTex(env,{'verbose' : True})
    #batchlocations[1] = TubeFurnace(env,{'verbose' : True})
    #batchlocations[1] = SingleSideEtch(env,{'verbose' : True})
    #batchlocations[1] = TubePECVD(env,{'verbose' : True})
    batchlocations[1] = PrintLine(env,{'verbose' : True})
    #batchlocations[2] = WaferBin(env)
    
    operators = {}    
    
    batchconnections = {} #[machine1,machine2,transfer_time]
    batchconnections[0] = [batchlocations[0],batchlocations[1],90]  
    operators[0] = Operator(env,batchconnections,"0")

    #batchconnections = {}
    #batchconnections[0] = [batchlocations[1],batchlocations[2],90]
    #operators[1] = Operator(env,batchconnections,"1")

    #time_limit = 10000
    time_limit = 60*60*24 # 1 day
    #time_limit = 60*60*24*7 # 1 week
    #time_limit = 60*60*24*7*30 # 1 month
    #time_limit = 60*60*24*365 # 1 year
    print "0% progress: 0 minutes (0 hours)"
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
        
    print "Production volume: " + str(batchlocations[len(batchlocations)-1].output.container.level)
    print "Average throughput (WPH): " + str(np.round(3600*batchlocations[len(batchlocations)-1].output.container.level/time_limit))
        