# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtGui

class AddOperatorConnectionDialog(QtGui.QDialog):
    def __init__(self, parent, _row, _index):
        super(QtGui.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.row = _row
        self.index = _index
        self.setWindowTitle(self.tr("Add operator connection"))
        vbox = QtGui.QVBoxLayout()

        title_label = QtGui.QLabel(self.tr("Available connections:"))
        vbox.addWidget(title_label)

        self.available_connections_combo = QtGui.QComboBox(self)
        for i, value in enumerate(self.parent.batchconnections):
            self.available_connections_combo.addItem(self.parent.print_batchconnection(i))

        vbox.addWidget(self.available_connections_combo)

        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def read(self):
        # Add connection to operator
        self.parent.operators[self.row][0].append(self.available_connections_combo.currentIndex())
        self.parent.operators[self.row][0].sort()
        
        self.parent.load_definition_operators(False)
        
        # re-expand the operator parent item
        index = self.parent.operators_model.index(self.row, 0)
        self.parent.operators_view.setExpanded(index, True) 
            
        self.parent.statusBar().showMessage("Operator connection added") 
        
        self.accept()