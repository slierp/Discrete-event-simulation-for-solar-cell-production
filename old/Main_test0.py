# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

For checking whether single units are processed correctly

"""

from __future__ import division
#from RunSimulation import RunSimulation
import pickle, sys

if __name__ == "__main__":      
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Solar cell manufacturing simulation"
            print "Options:"
            print "--h, --help  : Help message"
            exit()

    batchlocations = [] #tool class name, no of tools, dict with settings
    batchlocations.append(["WaferSource", {'batch_size' : 2, 'time_limit' : 1, 'name' : '0'}])
    batchlocations.append(["WaferUnstacker", {'cassette_size' : 1, 'verbose' : True, 'name' : '0'}])
    #batchlocations[1] = ["BatchTex", {'batch_size' : 1, 'cassette_size' : 1, 'verbose' : True}]
    #batchlocations[1] = ["TubeFurnace", {'batch_size' : 1, 'cassette_size' : 1, 'verbose' : True}]    
    #batchlocations[1] = ["SingleSideEtch", {'cassette_size' : 1, 'verbose' : True}]    
    #batchlocations[1] = ["TubePECVD", {'batch_size' : 1, 'cassette_size' : 1, 'verbose' : True}]
    #batchlocations[1] = ["PrintLine", {'cassette_size' : 1, 'verbose' : True}]       
    batchlocations.append(["WaferBin", {'batch_size' : 1, 'name' : '0'}])
    
    locationgroups = []
    locationgroups.append([0])
    locationgroups.append([1])
    locationgroups.append([2])

    transport_time = 90 # time for actual transport of one or more units
    time_per_unit = 20 # added time per unit for loading/unloading on the machines (combined value for input and output stations)
    batchconnections = [] #[machine1,machine2,transport_time,time_per_unit]
    batchconnections.append([[0,0],[1,0],transport_time,time_per_unit])
    batchconnections.append([[1,0],[2,0],transport_time,time_per_unit])

    operators = []
    operators.append([[0],{'name' : '0'}])
    operators.append([[1],{'name' : '1'}]) 

    params = {}

    params['time_limit'] = 10000  

#    RunSimulation(batchlocations,locationgroups,batchconnections,operators,params)

    with open('Example0.desc', 'w') as f:
        pickle.dump([batchlocations,locationgroups,batchconnections,operators], f)