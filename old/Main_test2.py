# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

For testing a full line

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
    batchlocations.append(["WaferSource", {'name' : '0'}])
    batchlocations.append(["WaferUnstacker", {'name' : '0'}])
    batchlocations.append(["WaferUnstacker",{'name' : '1'}])
    batchlocations.append(["BatchTex", {'name' : '0'}])
    batchlocations.append(["TubeFurnace", {'name' : '0'}])
    batchlocations.append(["TubeFurnace", {'name' : '1'}])
    batchlocations.append(["SingleSideEtch", {'name' : '0'}])
    batchlocations.append(["TubePECVD", {'name' : '0'}])
    batchlocations.append(["TubePECVD", {'name' : '1'}])
    batchlocations.append(["PrintLine", {'name' : '0'}])
    batchlocations.append(["PrintLine", {'name' : '1'}])
    #batchlocations[11] = ["WaferBin", {'name' : '0'}]    

    locationgroups = []
    locationgroups.append([0])
    locationgroups.append([1, 2])
    locationgroups.append([3])
    locationgroups.append([4, 5])
    locationgroups.append([6])
    locationgroups.append([7, 8])
    locationgroups.append([9, 10])

    transport_time = 90 # time for actual transport of one or more units
    time_per_unit = 20 # added time per unit for loading/unloading on the machines (combined value for input and output stations)
    batchconnections = [] #[machine1,machine2,transport_time,time_per_unit]
    batchconnections.append([[0,0],[1,0],transport_time,time_per_unit])
    batchconnections.append([[0,0],[1,1],transport_time,time_per_unit])
    
    batchconnections.append([[1,0],[2,0],transport_time,time_per_unit])
    batchconnections.append([[1,1],[2,0],transport_time,time_per_unit])
    
    batchconnections.append([[2,0],[3,0],transport_time,time_per_unit])
    batchconnections.append([[2,0],[3,1],transport_time,time_per_unit])
    
    batchconnections.append([[3,0],[4,0],transport_time,time_per_unit])
    batchconnections.append([[3,1],[4,0],transport_time,time_per_unit])
    
    batchconnections.append([[4,0],[5,0],transport_time,time_per_unit])
    batchconnections.append([[4,0],[5,1],transport_time,time_per_unit])
    
    batchconnections.append([[5,0],[6,0],transport_time,time_per_unit])
    batchconnections.append([[5,0],[6,1],transport_time,time_per_unit])
    batchconnections.append([[5,1],[6,0],transport_time,time_per_unit])
    batchconnections.append([[5,1],[6,1],transport_time,time_per_unit])
    
    operators = []
    operators.append([[0,1],{'name' : '0'}])
    operators.append([[2,3],{'name' : '1'}])
    operators.append([[4,5],{'name' : '2'}])   
    operators.append([[6,7],{'name' : '3'}])
    operators.append([[8,9],{'name' : '4'}])
    operators.append([[10,11,12,13],{'name' : '5'}])

    params = {}

    #params['time_limit'] = 1000
    params['time_limit'] = 60*60*24 # 1 day
    #params['time_limit'] = 60*60*24*7 # 1 week
    #params['time_limit'] = 60*60*24*30 # 1 month
    #params['time_limit'] = 60*60*24*365 # 1 year    

    #RunSimulation(batchlocations,locationgroups,batchconnections,operators,params)

    with open('Example2.desc', 'w') as f:
        pickle.dump([batchlocations,locationgroups,batchconnections,operators], f)

    #with open('objs.pickle') as f:
    #    batchlocations1,locationgroups1,batchconnections1,operators1 = pickle.load(f)

    #print batchlocations1    
    #print operators1