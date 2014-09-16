# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtGui

class AddBatchlocationDialog(QtGui.QDialog):
    def __init__(self, parent, _row, _index):
        super(QtGui.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.row = _row
        self.index = _index
        self.setWindowTitle(self.tr("Add batch location"))
        vbox = QtGui.QVBoxLayout()

        title_label = QtGui.QLabel(self.tr("Available types:"))
        vbox.addWidget(title_label)

        batchlocation_types = []
        batchlocation_types.append("WaferSource")
        batchlocation_types.append("WaferUnstacker")
        batchlocation_types.append("BatchTex")
        batchlocation_types.append("TubeFurnace")
        batchlocation_types.append("SingleSideEtch")
        batchlocation_types.append("TubePECVD")
        batchlocation_types.append("PrintLine")
        batchlocation_types.append("WaferBin")

        self.batchlocation_types_combo = QtGui.QComboBox(self)
        for i in batchlocation_types:
            self.batchlocation_types_combo.addItem(i)

        vbox.addWidget(self.batchlocation_types_combo)

        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def read(self):

        if (self.index == None): # if parent item        
            self.selected_batchlocation_number = self.parent.locationgroups[self.row][0]
            self.parent.locationgroups.insert(self.row,[0])
        else: # if child item       
            self.selected_batchlocation_number = self.parent.locationgroups[self.row][self.index]
            self.parent.locationgroups[self.row].insert(self.index,0)
        
        self.parent.batchlocations.insert(self.selected_batchlocation_number,
                                          [self.batchlocation_types_combo.currentText(), {'name' : 'new'}])
            
        
        self.parent.reindex_locationgroups()
        self.parent.load_definition_batchlocations(False)
        index = self.parent.batchlocations_model.index(self.row, 0)
        self.parent.batchlocations_view.setExpanded(index, True)
        
        self.parent.statusBar().showMessage(self.tr("Batch location added"))
        self.accept()