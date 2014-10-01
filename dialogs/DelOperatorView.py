# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtCore

class DelOperatorView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (not len(self.parent.operators_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
        elif (self.parent.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.del_operator()
        else: # if child row is selected
            self.del_operator_batchconnections()

    def del_operator(self):
        # find out which operator was selected
        row = self.parent.operators_view.selectedIndexes()[0].row()
        
        # remove selected operator
        del self.parent.operators[row]
        
        # reload definitions
        self.parent.load_definition_operators(False)        
        
        self.parent.statusBar().showMessage(self.tr("Operator removed"))
            
    def del_operator_batchconnections(self):
        # find out which connection was selected
        row = self.parent.operators_view.selectedIndexes()[0].parent().row()
        index = self.parent.operators_view.selectedIndexes()[0].row()

        if (len(self.parent.operators[row][0]) == 1):
            # if last child item, remove the operator
            del self.parent.operators[row]
            
            # reload definition into view
            self.parent.load_definition_operators(False) 
            
            self.parent.statusBar().showMessage("Last operator connection and operator removed")            
        else:
            del self.parent.operators[row][0][index]
            
            # reload definition into view
            self.parent.load_definition_operators(False)

            # re-expand the operator parent item
            index = self.parent.operators_model.index(row, 0)
            self.parent.operators_view.setExpanded(index, True) 
            
            self.parent.statusBar().showMessage("Operator connection removed")            