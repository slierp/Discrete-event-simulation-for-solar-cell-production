# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore
from copy import deepcopy

class RunSimulation(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (len(self.parent.batchlocations) < 2) | (len(self.parent.locationgroups) < 2):
            self.parent.statusBar().showMessage(self.tr("Not enough batch locations found"))
            return
        
        for i, value in enumerate(self.parent.batchconnections):
            # check if all batchconnections exist inside locationgroups
            # no separate check whether all batchlocations inside locationgroups exist
            # since GUI should not allow for any errors to appear
            if (self.parent.batchconnections[i][0][0] > (len(self.parent.locationgroups)-1)) | \
                    (self.parent.batchconnections[i][1][0] > (len(self.parent.locationgroups)-1)):
                self.parent.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"))
                return
            elif (self.parent.batchconnections[i][0][1] > (len(self.parent.locationgroups[self.parent.batchconnections[i][0][0]])-1)) | \
                    (self.parent.batchconnections[i][1][1] > (len(self.parent.locationgroups[self.parent.batchconnections[i][1][0]])-1)):
                self.parent.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"))
                return

        for i, value in enumerate(self.parent.operators):
            # check if all batchconnection numbers inside self.operators exist inside self.batchconnections
            for j in self.parent.operators[i][0]:
                if (j > len(self.parent.batchconnections)):
                    self.parent.statusBar().showMessage(self.tr("Invalid batch connection found inside operator definitions"))
                    return
        
        time_limits = [60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]
        for i, value in enumerate(self.parent.sim_time_selection_list):
            if (value == self.parent.sim_time_combo.currentText()):
                self.parent.params['time_limit'] = time_limits[i]
        
        if not self.parent.simulation_thread.isRunning():
        #if True: # interchange for isRunning when not running simulation in separate thread
            self.parent.edit.clear()
            self.parent.simulation_thread.batchlocations = deepcopy(self.parent.batchlocations)
            self.parent.simulation_thread.locationgroups = deepcopy(self.parent.locationgroups)
            self.parent.simulation_thread.batchconnections = deepcopy(self.parent.batchconnections)
            self.parent.simulation_thread.operators = deepcopy(self.parent.operators)

            self.parent.simulation_thread.params = {}
            self.parent.simulation_thread.params['time_limit'] = 1000
            self.parent.simulation_thread.params.update(self.parent.params)
            
            self.parent.simulation_thread.stop_simulation = False
            self.parent.simulation_thread.start()
            #self.simulation_thread.run() # interchange for start when not running simulation in separate thread
            self.parent.run_sim_button.setEnabled(False)
            self.parent.stop_sim_button.setEnabled(True)
            
            self.parent.statusBar().showMessage(self.tr("Simulation started"))           