# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

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

class RunSimulation(object):

    def __init__(self, batchlocations,locationgroups,batchconnections,operators,_params = {}):    

        self.batchlocations = batchlocations
        self.locationgroups = locationgroups
        self.batchconnections = batchconnections
        self.operators = operators

        self.params = {}
        self.params['time_limit'] = 1000
        self.params.update(_params)
    
        self.env = simpy.Environment()    

        #import simpy.rt # if you are really patient
        #self.env = simpy.rt.RealtimeEnvironment(factor=0.1)
        #self.env = simpy.rt.RealtimeEnvironment(factor=1)
    
        for i in batchlocations:
            # replace class names for real class instances in the same list
            if (batchlocations[i][0] == "WaferSource"):
                batchlocations[i] = WaferSource(self.env,batchlocations[i][1])
            elif (batchlocations[i][0] == "WaferUnstacker"):
                batchlocations[i] = WaferUnstacker(self.env,batchlocations[i][1])
            elif (batchlocations[i][0] == "BatchTex"):
                batchlocations[i] = BatchTex(self.env,batchlocations[i][1])
            elif (batchlocations[i][0] == "TubeFurnace"):
                batchlocations[i] = TubeFurnace(self.env,batchlocations[i][1])
            elif (batchlocations[i][0] == "SingleSideEtch"):
                batchlocations[i] = SingleSideEtch(self.env,batchlocations[i][1]) 
            elif (batchlocations[i][0] == "TubePECVD"):
                batchlocations[i] = TubePECVD(self.env,batchlocations[i][1]) 
            elif (batchlocations[i][0] == "PrintLine"):
                batchlocations[i] = PrintLine(self.env,batchlocations[i][1]) 
            elif (batchlocations[i][0] == "WaferBin"):
                batchlocations[i] = WaferBin(self.env,batchlocations[i][1])             

        for i in locationgroups:
            # replace batchlocation number indicators for references to real class instances
            for j in np.arange(len(locationgroups[i])):
                locationgroups[i][j] = batchlocations[locationgroups[i][j]]
           
        for i in batchconnections:
            # replace locationgroup number indicators for references to real class instances
            batchconnections[i][0] = locationgroups[batchconnections[i][0][0]][batchconnections[i][0][1]]
            batchconnections[i][1] = locationgroups[batchconnections[i][1][0]][batchconnections[i][1][1]]
    
        for i in operators:
            # replace batchconnection number indicators for references to real class instances
            # also replace operator list elements for new class instances
            _batchconnections = {}
        
            for j in np.arange(len(operators[i][0])):
                _batchconnections[j] = batchconnections[operators[i][0][j]]

            operators[i] = Operator(self.env,_batchconnections,operators[i][1])         

        print "0% progress: 0 hours"
        for i in np.arange(1,11):        
            self.env.run(until=self.params['time_limit']*i/10) # or perhaps do daily updates?
            if (i < 10):            
                print str(i*10) + "% progress: " + str(np.round(self.params['time_limit']*i/36000,1)) + " hours"
            else:
                print "Finished at "  + str(np.round(self.env.now/3600,1)) + " hours"

        for i in batchlocations:
            batchlocations[i].report()

        for i in operators:
            operators[i].report()

        prod_vol = 0
        l_loc = len(locationgroups)
        for i in np.arange(len(locationgroups[l_loc-1])):
            prod_vol += locationgroups[l_loc-1][i].output.container.level

        print "Production volume: " + str(prod_vol)
        print "Average throughput (WPH): " + str(np.round(3600*prod_vol/self.params['time_limit']).astype(int))