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
    
    #batchlocations = {} #tool class name, no of tools, dict with settings
    #batchlocations[0] = ["WaferSource", {'name' : '0'}]
    #batchlocations[1] = ["WaferUnstacker", {'name' : '0'}]
    #batchlocations[2] = ["WaferUnstacker",{'name' : '1'}]
    #batchlocations[3] = ["BatchTex", {'name' : '0'}]
    #batchlocations[4] = ["TubeFurnace", {'name' : '0'}]
    #batchlocations[5] = ["TubeFurnace", {'name' : '1'}]
    #batchlocations[6] = ["SingleSideEtch", {'name' : '0'}]
    #batchlocations[7] = ["TubePECVD", {'name' : '0'}]
    #batchlocations[8] = ["TubePECVD", {'name' : '1'}]
    #batchlocations[9] = ["PrintLine", {'name' : '0'}]
    #batchlocations[10] = ["PrintLine", {'name' : '1'}]
    #batchlocations[11] = ["WaferBin", {'name' : '0'}]

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
    
    #locationgroups = {}
    #locationgroups[0] = [0]
    #locationgroups[1] = [1, 2]
    #locationgroups[2] = [3]
    #locationgroups[3] = [4, 5]
    #locationgroups[4] = [6]
    #locationgroups[5] = [7, 8]
    #locationgroups[6] = [9, 10]

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
    batchconnections = {} #[machine1,machine2,transport_time,time_per_unit]
    
    batchconnections = {}
    batchconnections[0] = [[0,0],[1,0],transport_time,time_per_unit]
    batchconnections[1] = [[0,0],[1,1],transport_time,time_per_unit]
    
    batchconnections[2] = [[1,0],[2,0],transport_time,time_per_unit]
    batchconnections[3] = [[1,1],[2,0],transport_time,time_per_unit]
    
    batchconnections[4] = [[2,0],[3,0],transport_time,time_per_unit]
    batchconnections[5] = [[2,0],[3,1],transport_time,time_per_unit]
    
    batchconnections[6] = [[3,0],[4,0],transport_time,time_per_unit]
    batchconnections[7] = [[3,1],[4,0],transport_time,time_per_unit]
    
    batchconnections[8] = [[4,0],[5,0],transport_time,time_per_unit]
    batchconnections[9] = [[4,0],[5,1],transport_time,time_per_unit]
    
    batchconnections[10] = [[5,0],[6,0],transport_time,time_per_unit]
    batchconnections[11] = [[5,0],[6,1],transport_time,time_per_unit]
    batchconnections[12] = [[5,1],[6,0],transport_time,time_per_unit]
    batchconnections[13] = [[5,1],[6,1],transport_time,time_per_unit]
    
    operators = {}
    operators[0] = [[0,1],{'name' : '0'}]
    operators[1] = [[2,3],{'name' : '1'}]    
    operators[2] = [[4,5],{'name' : '2'}]
    operators[3] = [[6,7],{'name' : '3'}]
    operators[4] = [[8,9],{'name' : '4'}]
    operators[5] = [[10,11,12,13],{'name' : '5'}]

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