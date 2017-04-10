# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddBatchlocationDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.view = self.parent.batchlocations_view        
        self.model = self.parent.batchlocations_model
        self.batchlocations = self.parent.tools_widget.batchlocations
        self.locationgroups = self.parent.tools_widget.locationgroups
        self.statusbar = self.parent.statusBar()        
        
        self.append_mode = False
        parent_type = None
        self.child_item = False
        self.row = False
        
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.append_mode = True            
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.row = self.view.selectedIndexes()[0].row()
            self.index = None
            parent_type = self.batchlocations[self.locationgroups[self.row][0]][0]
        else:
            self.row = self.view.selectedIndexes()[0].parent().row()
            self.index = self.view.selectedIndexes()[0].row()
            parent_type = self.batchlocations[self.locationgroups[self.row][self.index]][0]
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
        #batchlocation_types.append("InlinePECVD")
        #batchlocation_types.append("IonImplanter")        
        batchlocation_types.append("PlasmaEtcher")
        batchlocation_types.append("PrintLine")         
        batchlocation_types.append("SingleSideEtch")    
        #batchlocation_types.append("SpatialALD")
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
        
        reindex_locationgroups = self.parent.tools_widget.reindex_locationgroups
        load_definition = self.parent.tools_widget.load_definition
        generate_locationgroups = self.parent.tools_widget.generate_locationgroups
        generate_batchconnections = self.parent.tools_widget.generate_batchconnections
        reset_cassetteloops = self.parent.cassetteloops_widget.reset_cassetteloops
        reset_operators = self.parent.operators_widget.reset_operators
        reset_technicians = self.parent.technicians_widget.reset_technicians

        if (self.append_mode): # if nothing was selected
            self.selected_batchlocation_number = len(self.batchlocations)
            reset_cassetteloops(self.selected_batchlocation_number)
            reset_operators(self.selected_batchlocation_number)
            reset_technicians(self.selected_batchlocation_number)            
            self.locationgroups.append([0])
            self.row = len(self.locationgroups)-1
        elif (self.index == None): # if parent item was selected      
            self.selected_batchlocation_number = self.locationgroups[self.row][0]
            reset_cassetteloops(self.selected_batchlocation_number)
            reset_operators(self.selected_batchlocation_number)
            reset_technicians(self.selected_batchlocation_number)            
            self.locationgroups.insert(self.row,[0])        
        else: # if child item was selected       
            self.selected_batchlocation_number = self.locationgroups[self.row][self.index]
            reset_cassetteloops(self.selected_batchlocation_number)
            reset_operators(self.selected_batchlocation_number)
            reset_technicians(self.selected_batchlocation_number)            
            self.locationgroups[self.row].insert(self.index,0)        

        new_dict = {}
        if (self.child_item): # copy previously selected batchlocation
            if (self.copy_checkbox.isChecked()): # if user selected this option
                new_dict.update(self.batchlocations[self.locationgroups[self.row][self.index+1]][1])

        # insert new batch location with selected name
        input_string = str(self.name_edit.text()) 
        new_dict.update({'name' : input_string})
        self.batchlocations.insert(self.selected_batchlocation_number,
                                          [self.batchlocation_types_combo.currentText(), new_dict])
        
        # do a bit of housekeeping, now that batchlocations has changed
        reindex_locationgroups()
        load_definition(False)
        generate_locationgroups() # generate new locationgroups list
        generate_batchconnections() # generate new connections list

        # re-expand parent item in view       
        index = self.model.index(self.row, 0)
        self.view.setExpanded(index, True)
        
        if (self.child_item): # select newly created item in view
            parent = self.model.index(self.row, 0)
            index = self.model.index(self.index, 0, parent)
            self.view.setCurrentIndex(index)
        
        self.statusbar.showMessage(self.tr("Batch location added"),3000)
        self.accept()