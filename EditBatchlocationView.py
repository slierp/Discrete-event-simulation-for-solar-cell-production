# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore
from BatchlocationSettingsDialog import BatchlocationSettingsDialog

class EditBatchlocationView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        if (not len(self.parent.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
            return
        elif (self.parent.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            # TO BE IMPLEMENTED: change all children, provided that they are of the same class
            self.parent.statusBar().showMessage("Not yet implemented")            
            return

        # start dialog to enable user to change settings
        batchlocation_dialog = BatchlocationSettingsDialog(self.parent)
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()                 