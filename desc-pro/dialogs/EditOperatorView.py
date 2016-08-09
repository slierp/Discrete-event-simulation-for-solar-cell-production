# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from OperatorSettingsDialog import OperatorSettingsDialog
from ConnectionSettingsDialog import ConnectionSettingsDialog

class EditOperatorView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (not len(self.parent.operators_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
        elif (self.parent.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.edit_operator()
        else: # if child row is selected
            self.edit_batchconnection()

    def edit_operator(self):
        # start dialog to enable user to change settings
        batchlocation_dialog = OperatorSettingsDialog(self.parent)
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()

    def edit_batchconnection(self):
        # find out which connection was selected
        row = self.parent.operators_view.selectedIndexes()[0].parent().row()
        index = self.parent.operators_view.selectedIndexes()[0].row()       
        batchconnection = self.parent.batchconnections[self.parent.operators[row][0][index]]

        # start dialog to enable user to change settings
        connection_dialog = ConnectionSettingsDialog(self.parent,batchconnection)
        connection_dialog.setModal(True)
        connection_dialog.show()            