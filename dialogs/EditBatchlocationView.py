# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore
from BatchlocationSettingsDialog import BatchlocationSettingsDialog
from LocationgroupSettingsDialog import LocationgroupSettingsDialog

class EditBatchlocationView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        if (not len(self.parent.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
            return
        
        if (self.parent.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            row = self.parent.batchlocations_view.selectedIndexes()[0].row()         
            
            # check if all the child elements are of the same class
            reference = self.parent.batchlocations[self.parent.locationgroups[row][0]][0]
            for i, value in enumerate(self.parent.locationgroups[row]):
                to_be_tested = self.parent.batchlocations[self.parent.locationgroups[row][i]][0]        
                if not (reference == to_be_tested):
                    self.parent.statusBar().showMessage(self.tr("Not all batch locations in this group are of the same kind"))
                    return
                    
            locationgroup_dialog = LocationgroupSettingsDialog(self.parent)
            locationgroup_dialog.setModal(True)
            locationgroup_dialog.show()             
        else:            
            batchlocation_dialog = BatchlocationSettingsDialog(self.parent)
            batchlocation_dialog.setModal(True)
            batchlocation_dialog.show()                                    