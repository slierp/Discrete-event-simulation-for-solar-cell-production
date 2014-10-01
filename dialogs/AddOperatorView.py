# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore
from copy import deepcopy
from AddOperatorConnectionDialog import AddOperatorConnectionDialog

class AddOperatorView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (not len(self.parent.operators_view.selectedIndexes())):
            # if nothing selected
            self.add_operator(True)
        elif (self.parent.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.add_operator()
        else: # if child row is selected
            self.add_operator_batchconnections()
            
    def add_operator(self, append_mode = False):
        if (append_mode):
            if (len(self.parent.batchconnections) > 0):
                self.parent.operators.append([[0],{'name' : 'new'}])
       
                # reload definitions
                self.parent.load_definition_operators(False)
        
                index = self.parent.operators_model.index(len(self.parent.operators), 0)
                self.parent.operators_view.setCurrentIndex(index)
            else:
                self.parent.statusBar().showMessage(self.tr("No batch connections available for new operator"))
                return
        else:                      
            # find out which operator was selected
            row = self.parent.operators_view.selectedIndexes()[0].row()
        
            # copy selected operator and give it name 'new'
            self.parent.operators.insert(row,deepcopy(self.parent.operators[row]))
            self.parent.operators[row][1].update({'name' : 'new'})
        
            # reload definitions
            self.parent.load_definition_operators(False)
        
            index = self.parent.operators_model.index(row, 0)
            self.parent.operators_view.setCurrentIndex(index)
        
        self.parent.statusBar().showMessage(self.tr("Operator added"))

    def add_operator_batchconnections(self):        
        # start dialog to enable user to add operator
        connection_dialog = AddOperatorConnectionDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()            