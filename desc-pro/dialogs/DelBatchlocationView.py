# -*- coding: utf-8 -*-
from PyQt5 import QtCore

class DelBatchlocationView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        if (not len(self.parent.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
            return
        
        child_item = False
        
        if (self.parent.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent item, remove all batchlocation children and row in locationgroups
        
            row = self.parent.batchlocations_view.selectedIndexes()[0].row() # selected row in locationgroups
            self.reset_operators(row)
            
            start = self.parent.locationgroups[row][0]
            finish = self.parent.locationgroups[row][len(self.parent.locationgroups[row])-1]+1                
            del self.parent.batchlocations[start:finish]
            del self.parent.locationgroups[row]            

        else: # if child item
            row = self.parent.batchlocations_view.selectedIndexes()[0].parent().row() # selected row in locationgroups           

            
            if (len(self.parent.locationgroups[row]) == 1):
                # if last child item, remove batchlocation and whole row in locationgroups
                del self.parent.batchlocations[self.parent.locationgroups[row][0]]
                del self.parent.locationgroups[row]
            else:
                # if not last child item, remove batchlocation and element in locationgroup row
                index = self.parent.batchlocations_view.selectedIndexes()[0].row()
                del self.parent.batchlocations[self.parent.locationgroups[row][index]]
                del self.parent.locationgroups[row][index]
                child_item = True
          
        # do a bit of housekeeping now that batchlocations has changed
        self.parent.reindex_locationgroups()
        self.parent.load_definition_batchlocations(False)
        self.parent.exec_locationgroups() # generate new connections list        
        
        if child_item:
            index = self.parent.batchlocations_model.index(row, 0)
            self.parent.batchlocations_view.setExpanded(index, True)        
        
        self.parent.statusBar().showMessage(self.tr("Batch location(s) removed"))
        
    def reset_operators(self, row):
        # reset connection list of operators whose connections have become invalid
    
        if (len(self.parent.batchlocations) == 0):
            return

        reset_list = []
        for i, value0 in enumerate(self.parent.operators):
            for j, value1 in enumerate(self.parent.operators[i][0]):
                if (self.parent.operators[i][0][j] < (len(self.parent.batchconnections)-1)):
                    num = self.parent.batchconnections[self.parent.operators[i][0][j]]
                    
                    if (num[0][0] >= row) | (num[1][0] >= row):
                        reset_list.append(i)
            
        for i in reset_list:
            dict_copy = self.parent.operators[i][1]
            del self.parent.operators[i]                        
            self.parent.operators.insert(i,[[],dict_copy])
            self.parent.operators[i][0].append(0)
            
        self.parent.load_definition_operators(False)