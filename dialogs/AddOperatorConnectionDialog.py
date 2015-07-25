# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui
from sys import platform as _platform

class AddOperatorConnectionDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(QtGui.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent

        # find out which connection was selected
        self.row = self.parent.operators_view.selectedIndexes()[0].parent().row()
        self.index = self.parent.operators_view.selectedIndexes()[0].row()        
        
        self.setWindowTitle(self.tr("Add operator connection"))
        vbox = QtGui.QVBoxLayout()

        title_label = QtGui.QLabel(self.tr("Available connections:"))
        vbox.addWidget(title_label)

        self.available_connections_combo = QtGui.QComboBox(self)
        for i, value in enumerate(self.parent.batchconnections):
            self.available_connections_combo.addItem(self.parent.print_batchconnection(i))

        vbox.addWidget(self.available_connections_combo)

        ### Buttonbox for ok or cancel ###
        hbox = QtGui.QHBoxLayout()
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtGui.QBoxLayout.RightToLeft)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

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