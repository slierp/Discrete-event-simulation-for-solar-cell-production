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
from PyQt4 import QtCore #, QtGui

class SimulationSignal(QtCore.QObject):
    sig = QtCore.Signal(str)

class RunSimulationThread(QtCore.QThread):

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.stop_simulation = False
        self.signal = SimulationSignal()

    def run(self):
        print "Started running"        

        self.env = simpy.Environment()    

        #import simpy.rt # if you are really patient
        #self.env = simpy.rt.RealtimeEnvironment(factor=0.1)
        #self.env = simpy.rt.RealtimeEnvironment(factor=1)
    
        for i in self.batchlocations:
            # replace class names for real class instances in the same list
            if (self.batchlocations[i][0] == "WaferSource"):
                self.batchlocations[i] = WaferSource(self.env,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "WaferUnstacker"):
                self.batchlocations[i] = WaferUnstacker(self.env,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchTex"):
                self.batchlocations[i] = BatchTex(self.env,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "TubeFurnace"):
                self.batchlocations[i] = TubeFurnace(self.env,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "SingleSideEtch"):
                self.batchlocations[i] = SingleSideEtch(self.env,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "TubePECVD"):
                self.batchlocations[i] = TubePECVD(self.env,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "PrintLine"):
                self.batchlocations[i] = PrintLine(self.env,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "WaferBin"):
                self.batchlocations[i] = WaferBin(self.env,self.batchlocations[i][1])             

        for i in self.locationgroups:
            # replace batchlocation number indicators for references to real class instances
            for j in np.arange(len(self.locationgroups[i])):
                self.locationgroups[i][j] = self.batchlocations[self.locationgroups[i][j]]
           
        for i in self.batchconnections:
            # replace locationgroup number indicators for references to real class instances
            self.batchconnections[i][0] = self.locationgroups[self.batchconnections[i][0][0]][self.batchconnections[i][0][1]]
            self.batchconnections[i][1] = self.locationgroups[self.batchconnections[i][1][0]][self.batchconnections[i][1][1]]
    
        for i in self.operators:
            # replace batchconnection number indicators for references to real class instances
            # also replace operator list elements for new class instances
            tmp_batchconnections = {}
        
            for j in np.arange(len(self.operators[i][0])):
                tmp_batchconnections[j] = self.batchconnections[self.operators[i][0][j]]

            self.operators[i] = Operator(self.env,tmp_batchconnections,self.operators[i][1])         

        print "0% progress: 0 hours"
        for i in np.arange(1,11):
            if(self.stop_simulation):
                break
            
            self.env.run(until=self.params['time_limit']*i/10) # or perhaps do daily updates?
            if (i < 10):            
                print str(i*10) + "% progress: " + str(np.round(self.params['time_limit']*i/36000,1)) + " hours"
            else:
                print "Finished at "  + str(np.round(self.env.now/3600,1)) + " hours"

        for i in self.batchlocations:
            self.batchlocations[i].report()

        for i in self.operators:
            self.operators[i].report()

        prod_vol = 0
        l_loc = len(self.locationgroups)
        for i in np.arange(len(self.locationgroups[l_loc-1])):
            prod_vol += self.locationgroups[l_loc-1][i].output.container.level

        print "Production volume: " + str(prod_vol)
        print "Average throughput (WPH): " + str(np.round(3600*prod_vol/self.params['time_limit']).astype(int))
        
        self.signal.sig.emit('Simulation finished')