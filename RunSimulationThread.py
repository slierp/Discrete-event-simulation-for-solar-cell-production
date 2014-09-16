# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

"""

from __future__ import division
from batchlocations.WaferSource import WaferSource
from batchlocations.WaferUnstacker import WaferUnstacker
from batchlocations.Operator import Operator
from batchlocations.WaferBin import WaferBin
from batchlocations.BatchTex import BatchTex
from batchlocations.TubeFurnace import TubeFurnace
from batchlocations.SingleSideEtch import SingleSideEtch
from batchlocations.TubePECVD import TubePECVD
from batchlocations.PrintLine import PrintLine
#import simpyx as simpy
import simpy
import numpy as np
from PyQt4 import QtCore
#from PyQt4 import QtGui # only needed when not running simulation in separate thread

class SimulationSignal(QtCore.QObject):
        sig = QtCore.pyqtSignal(str)

class RunSimulationThread(QtCore.QThread):
#class RunSimulationThread(QtGui.QMainWindow): # interchange for QThread when not running simulation in separate thread

    def __init__(self, edit, parent = None):
        QtCore.QThread.__init__(self, parent)
        #super(QtGui.QMainWindow, self).__init__(parent) # interchange for QThread when not running simulation in separate thread
        self.stop_simulation = False
        self.edit = edit
        self.signal = SimulationSignal()        
        self.output = SimulationSignal()

    def make_unique(self,nonunique):
        unique = []
        for x in nonunique:
            if x not in unique:
                unique.append(x)
        unique.sort()
        return unique

    def run(self):
        
        self.env = simpy.Environment()    

        #import simpy.rt # if you are really patient
        #self.env = simpy.rt.RealtimeEnvironment(factor=0.1)
        #self.env = simpy.rt.RealtimeEnvironment(factor=1)
   
        for i, value in enumerate(self.batchlocations):
            # replace class names for real class instances in the same list
            if (self.batchlocations[i][0] == "WaferSource"):
                self.batchlocations[i] = WaferSource(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "WaferUnstacker"):
                self.batchlocations[i] = WaferUnstacker(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchTex"):
                self.batchlocations[i] = BatchTex(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "TubeFurnace"):
                self.batchlocations[i] = TubeFurnace(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "SingleSideEtch"):
                self.batchlocations[i] = SingleSideEtch(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "TubePECVD"):
                self.batchlocations[i] = TubePECVD(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "PrintLine"):
                self.batchlocations[i] = PrintLine(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "WaferBin"):
                self.batchlocations[i] = WaferBin(self.env,self.output,self.batchlocations[i][1])             

        for i, value in enumerate(self.locationgroups):
            # replace batchlocation number indicators for references to real class instances
            for j in np.arange(len(self.locationgroups[i])):
                self.locationgroups[i][j] = self.batchlocations[self.locationgroups[i][j]]
           
        for i, value in enumerate(self.batchconnections):
            # replace locationgroup number indicators for references to real class instances
            self.batchconnections[i][0] = self.locationgroups[self.batchconnections[i][0][0]][self.batchconnections[i][0][1]]
            self.batchconnections[i][1] = self.locationgroups[self.batchconnections[i][1][0]][self.batchconnections[i][1][1]]
    
        for i, value in enumerate(self.operators):
            # replace batchconnection number indicators for references to real class instances
            # also replace operator list elements for new class instances
            tmp_batchconnections = {}
        
            for j in np.arange(len(self.operators[i][0])):
                tmp_batchconnections[j] = self.batchconnections[self.operators[i][0][j]]

            self.operators[i] = Operator(self.env,tmp_batchconnections,self.output,self.operators[i][1])

        no_hourly_updates = self.params['time_limit'] // (60*60)
        hourly_updates = []
        for i in np.arange(0,no_hourly_updates):
            hourly_updates.append((i+1)*60*60)
        
        percentage_updates = []
        for i in np.arange(0,10):
            if (len(percentage_updates)):
                percentage_updates.append(percentage_updates[i-1] + (self.params['time_limit'] // 10))
            else:
                percentage_updates.append(self.params['time_limit'] // 10)    
                
        updates_list = hourly_updates + percentage_updates
        updates_list = self.make_unique(updates_list)

        self.output.sig.emit("0% progress: 0 hours / 0 produced")

        prev_production_volume_update = 0
        prev_percentage_time = self.env.now
        for i in updates_list:
            if(self.stop_simulation):
                string = "Stopped at "  + str(np.round(self.env.now/3600,1)) + " hours"
                self.output.sig.emit(string) 
                break

            self.env.run(until=i)
            
            if (i == self.params['time_limit']):                
                string = "Finished at "  + str(np.round(self.env.now/3600,1)) + " hours"
                self.output.sig.emit(string)                            
            elif (i % (self.params['time_limit'] // 10) == 0):
                
                l_loc = len(self.locationgroups)
                percentage_production_volume_update = 0
                for j in np.arange(len(self.locationgroups[l_loc-1])):
                    percentage_production_volume_update += self.locationgroups[l_loc-1][j].output.container.level
                    
                percentage_wph_update = (percentage_production_volume_update - prev_production_volume_update)
                percentage_wph_update = 3600 * percentage_wph_update / (self.env.now - prev_percentage_time)                
                
                string = str(np.round(100*i/self.params['time_limit']).astype(int)) + "% progress: " + str(np.round(i/3600,1)) + " hours / "
                string += str(percentage_production_volume_update) + " produced (" + str(np.round(percentage_wph_update).astype(int)) + " wph)"
                self.output.sig.emit(string)

                prev_percentage_time = self.env.now
                prev_production_volume_update = percentage_production_volume_update                

        for i, value in enumerate(self.batchlocations):
            self.batchlocations[i].report()

        for i, value in enumerate(self.operators):
            self.operators[i].report()

        prod_vol = 0
        l_loc = len(self.locationgroups)
        for i in np.arange(len(self.locationgroups[l_loc-1])):
            prod_vol += self.locationgroups[l_loc-1][i].output.container.level

        self.output.sig.emit("Production volume: " + str(prod_vol))
        self.output.sig.emit("Average throughput (WPH): " + str(np.round(3600*prod_vol/self.params['time_limit']).astype(int)))        
        
        self.signal.sig.emit('Simulation finished')