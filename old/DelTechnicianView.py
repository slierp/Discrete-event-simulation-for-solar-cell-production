# -*- coding: utf-8 -*-
from PyQt5 import QtCore

class DelTechnicianView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (not len(self.parent.technicians_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
        elif (self.parent.technicians_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.del_technician()
        else: # if child row is selected
            self.del_technician_batchlocations()

    def del_technician(self):
        # find out which operator was selected
        row = self.parent.technicians_view.selectedIndexes()[0].row()
        
        # remove selected operator
        del self.parent.technicians[row]
        
        # reload definitions
        self.parent.load_definition_technicians(False)        
        
        self.parent.statusBar().showMessage(self.tr("Technician removed"))
            
    def del_technician_batchlocations(self):
        # find out which connection was selected
        row = self.parent.technicians_view.selectedIndexes()[0].parent().row()
        index = self.parent.technicians_view.selectedIndexes()[0].row()

        if (len(self.parent.technicians[row][0]) == 1):
            # if last child item, remove the operator
            del self.parent.technicians[row]
            
            # reload definition into view
            self.parent.load_definition_technicians(False) 
            
            self.parent.statusBar().showMessage("Last tool and technician removed")            
        else:
            del self.parent.technicians[row][0][index]            
            
            # reload definition into view
            self.parent.load_definition_technicians(False)

            # re-expand the operator parent item
            index = self.parent.technicians_model.index(row, 0)
            self.parent.technicians_view.setExpanded(index, True) 
            
            self.parent.statusBar().showMessage("Technician tool removed")            