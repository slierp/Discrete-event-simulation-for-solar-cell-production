# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

For measuring maximum throughput of single tools

"""

from __future__ import division
from RunSimulation import RunSimulation
import pickle, sys

if __name__ == "__main__":      
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Solar cell manufacturing simulation"
            print "Options:"
            print "--h, --help  : Help message"
            exit()

    batchlocations = {} #tool class name, no of tools, dict with settings
    batchlocations[0] = ["WaferSource", {'name' : '0','batch_size' : 100}]
    batchlocations[1] = ["WaferUnstacker", {'name' : '0', 'verbose' : True}]
    #batchlocations[1] = ["BatchTex", {'verbose' : True}]
    #batchlocations[1] = ["TubeFurnace", {'verbose' : True}]    
    #batchlocations[1] = ["SingleSideEtch", {'verbose' : True}]    
    #batchlocations[1] = ["TubePECVD", {'verbose' : True}]
    #batchlocations[1] = ["PrintLine", {'verbose' : True}]       
    batchlocations[2] = ["WaferBin", {'name' : '0'}]
    
    locationgroups = {}
    locationgroups[0] = [0]
    locationgroups[1] = [1]
    locationgroups[2] = [2]

    transport_time = 90 # time for actual transport of one or more units
    time_per_unit = 20 # added time per unit for loading/unloading on the machines (combined value for input and output stations)
    batchconnections = {} #[machine1,machine2,transport_time,time_per_unit]
    
    batchconnections = {}
    batchconnections[0] = [[0,0],[1,0],transport_time,time_per_unit]
    batchconnections[1] = [[1,0],[2,0],transport_time,time_per_unit]

    operators = {}
    operators[0] = [[0],{'name' : '0'}]
    operators[1] = [[1],{'name' : '1'}]    

    params = {}

    #params['time_limit'] = 1000
    params['time_limit'] = 60*60*24 # 1 day
    #params['time_limit'] = 60*60*24*7 # 1 week
    #params['time_limit'] = 60*60*24*30 # 1 month
    #params['time_limit'] = 60*60*24*365 # 1 year    

#    RunSimulation(batchlocations,locationgroups,batchconnections,operators,params)
    
    with open('Example1.desc', 'w') as f:
        pickle.dump([batchlocations,locationgroups,batchconnections,operators], f)