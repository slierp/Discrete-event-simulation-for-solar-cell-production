# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddBatchlocationDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.append_mode = False
        parent_type = None
        self.child_item = False
        
        if (not len(self.parent.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.append_mode = True            
        elif (self.parent.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.row = self.parent.batchlocations_view.selectedIndexes()[0].row()
            self.index = None
            parent_type = self.parent.batchlocations[self.parent.locationgroups[self.row][0]][0]
        else:
            self.row = self.parent.batchlocations_view.selectedIndexes()[0].parent().row()
            self.index = self.parent.batchlocations_view.selectedIndexes()[0].row()
            parent_type = self.parent.batchlocations[self.parent.locationgroups[self.row][self.index]][0]
            self.child_item = True
                
        self.setWindowTitle(self.tr("Add batch location"))

        vbox = QtWidgets.QVBoxLayout()
        hbox0 = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel(self.tr("Select type:"))
        hbox0.addWidget(label)

        batchlocation_types = []
        batchlocation_types.append("BatchClean")        
        batchlocation_types.append("BatchTex")
        batchlocation_types.append("Buffer")        
        batchlocation_types.append("InlinePECVD")
        batchlocation_types.append("IonImplanter")        
        batchlocation_types.append("PlasmaEtcher")
        batchlocation_types.append("PrintLine")         
        batchlocation_types.append("SingleSideEtch")    
        batchlocation_types.append("SpatialALD")
        batchlocation_types.append("TubeFurnace")
        batchlocation_types.append("TubePECVD")
        batchlocation_types.append("WaferBin")
        batchlocation_types.append("WaferSource")
        batchlocation_types.append("WaferStacker")        
        batchlocation_types.append("WaferUnstacker")               

        self.batchlocation_types_combo = QtWidgets.QComboBox(self)
        for i in batchlocation_types:
            self.batchlocation_types_combo.addItem(i)

        if (parent_type):
            for i, value in enumerate(batchlocation_types):
                if (parent_type == value):
                    self.batchlocation_types_combo.setCurrentIndex(i)
                    continue

        hbox0.addWidget(self.batchlocation_types_combo)
        vbox.addLayout(hbox0)

        hbox1 = QtWidgets.QHBoxLayout()
        
        label = QtWidgets.QLabel(self.tr("name"))
        hbox1.addWidget(label)

        self.name_edit = QtWidgets.QLineEdit("new")
        hbox1.addWidget(self.name_edit)        

        if (self.child_item):
            hbox2 = QtWidgets.QHBoxLayout()
        
            label = QtWidgets.QLabel(self.tr("create_copy"))
            hbox2.addWidget(label)

            self.copy_checkbox = QtWidgets.QCheckBox()
            self.copy_checkbox.setChecked(True)
            hbox2.addWidget(self.copy_checkbox)    

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft) 
        
        vbox.addLayout(hbox1)
        if (self.child_item): vbox.addLayout(hbox2)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)  

    def read(self):

        if (self.append_mode): # if nothing was selected
            self.selected_batchlocation_number = len(self.parent.batchlocations)
            self.parent.locationgroups.append([0])
            self.row = len(self.parent.locationgroups)-1
        elif (self.index == None): # if parent item was selected      
            self.selected_batchlocation_number = self.parent.locationgroups[self.row][0]
            self.parent.locationgroups.insert(self.row,[0])        
        else: # if child item was selected       
            self.selected_batchlocation_number = self.parent.locationgroups[self.row][self.index]
            self.parent.locationgroups[self.row].insert(self.index,0)        

        new_dict = {}
        if (self.child_item): # copy previously selected batchlocation
            if (self.copy_checkbox.isChecked()): # if user selected this option
                new_dict.update(self.parent.batchlocations[self.parent.locationgroups[self.row][self.index+1]][1])

        # insert new batch location with selected name
        input_string = str(self.name_edit.text()) 
        new_dict.update({'name' : input_string})
        self.parent.batchlocations.insert(self.selected_batchlocation_number,
                                          [self.batchlocation_types_combo.currentText(), new_dict])
        
        # do a bit of housekeeping, now that batchlocations has changed
        self.parent.reindex_locationgroups()
        self.parent.load_definition_batchlocations(False)
        self.parent.exec_locationgroups() # generate new connections list        
        self.reset_operators(self.row)

        # re-expand parent item in view       
        index = self.parent.batchlocations_model.index(self.row, 0)
        self.parent.batchlocations_view.setExpanded(index, True)
        
        if (self.child_item): # select newly created item in view
            parent = self.parent.batchlocations_model.index(self.row, 0)
            index = self.parent.batchlocations_model.index(self.index, 0, parent)
            self.parent.batchlocations_view.setCurrentIndex(index)
        
        self.parent.statusBar().showMessage(self.tr("Batch location added"))
        self.accept()
        
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