# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from dialogs.AddBatchlocationDialog import AddBatchlocationDialog
from dialogs.BatchlocationSettingsDialog import BatchlocationSettingsDialog
from dialogs.LocationgroupSettingsDialog import LocationgroupSettingsDialog
from dialogs.LineDiagramDialog import LineDiagramDialog

class ToolsWidget(QtCore.QObject):
    def __init__(self, parent=None):
        super(ToolsWidget, self).__init__(parent)

        self.parent = parent
        
        self.view = self.parent.batchlocations_view        
        self.model = self.parent.batchlocations_model
        self.statusbar = self.parent.statusBar()

        self.batchlocations = [] #tool class name, dict with settings
        self.batchlocations.append(["WaferSource", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker", {'name' : '0'}])
        self.batchlocations.append(["BatchTex", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '0'}])
        self.batchlocations.append(["SingleSideEtch", {'name' : '0'}])
        self.batchlocations.append(["TubePECVD", {'name' : '0'}])
        self.batchlocations.append(["PrintLine", {'name' : '0'}])
                
        self.locationgroups = [] 
        self.batchconnections = []

        self.group_names = {}
        self.group_names['BatchClean'] = "Wet chemical clean"
        self.group_names['BatchTex'] = "Alkaline texture"
        self.group_names['Buffer'] = "Cassette buffer"
        self.group_names['InlinePECVD'] = "PECVD"
        self.group_names['IonImplanter'] = "Ion implantation"
        self.group_names['PlasmaEtcher'] = "Plasma edge isolation"
        self.group_names['PrintLine'] = "Printing/firing"
        self.group_names['SingleSideEtch'] = "Inline wet etch/texture"
        self.group_names['SpatialALD'] = "Atomic layer deposition"
        self.group_names['TubeFurnace'] = "Diffusion"
        self.group_names['TubePECVD'] = "PECVD"
        self.group_names['WaferBin'] = "Bin"
        self.group_names['WaferSource'] = "Source"
        self.group_names['WaferStacker'] = "Wafer stacking"
        self.group_names['WaferUnstacker'] = "Wafer unstacking"  

    def load_definition(self, default=True):

        if (default): # generate default locationgroup arrangement by batchlocation contents        
            self.generate_locationgroups()
            self.generate_batchconnections()
            
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Process flow'])           

        for i, value in enumerate(self.locationgroups):
            parent = QtGui.QStandardItem(self.group_names[self.batchlocations[self.locationgroups[i][0]][0]])

            for j in self.locationgroups[i]:
                child = QtGui.QStandardItem(self.batchlocations[j][0] + ' ' + self.batchlocations[j][1]['name'])
                parent.appendRow(child)
            self.model.appendRow(parent)
            #self.batchlocations_view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True)
            index = self.model.index(i, 0)
            self.view.setExpanded(index, True)

    def reindex_locationgroups(self):
        # change it so that all indexes are consecutive, which should always be the case
        num = 0
        for i, value0 in enumerate(self.locationgroups):
            for j, value1 in enumerate(self.locationgroups[i]):
                self.locationgroups[i][j] = num
                num += 1

    def line_diagram_view(self):
        if (len(self.batchlocations)) and (len(self.locationgroups)):
            self.show_diagram()
        else:
            self.parent.statusBar().showMessage(self.tr("Please complete production line definition"))

    def show_diagram(self):        
        # start dialog to generate and show line diagram
        connection_dialog = LineDiagramDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()

    def add_batchlocation_view(self):
        # start dialog to enable user to add batch location
        add_batchlocation_dialog = AddBatchlocationDialog(self.parent)
        add_batchlocation_dialog.setModal(True)
        add_batchlocation_dialog.show()

    def del_batchlocation_view(self):        
        reset_operators = self.parent.operators_widget.reset_operators
        reset_cassetteloops = self.parent.cassetteloops_widget.reset_cassetteloops        
        reset_technicians = self.parent.technicians_widget.reset_technicians    
        
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"),3000)
            return
        
        child_item = False
        
        if (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent item, remove all batchlocation children and row in locationgroups
        
            row = self.view.selectedIndexes()[0].row() # selected row in locationgroups
            reset_operators(self.locationgroups[row][0])            
            reset_cassetteloops(self.locationgroups[row][0])
            reset_technicians(self.locationgroups[row][0])
            
            start = self.locationgroups[row][0]
            finish = self.locationgroups[row][len(self.locationgroups[row])-1]+1                
            del self.batchlocations[start:finish]
            del self.locationgroups[row]            

        else: # if child item
            row = self.view.selectedIndexes()[0].parent().row() # selected row in locationgroups           
            
            if (len(self.locationgroups[row]) == 1):
                # if last child item, remove batchlocation and whole row in locationgroups
                
                reset_operators(self.locationgroups[row][0])            
                reset_cassetteloops(self.locationgroups[row][0])
                reset_technicians(self.locationgroups[row][0])
                
                del self.batchlocations[self.locationgroups[row][0]]
                del self.locationgroups[row]
            else:
                # if not last child item, remove batchlocation and element in locationgroup row
                index = self.view.selectedIndexes()[0].row()
                
                reset_operators(self.locationgroups[row][index])            
                reset_cassetteloops(self.locationgroups[row][index])
                reset_technicians(self.locationgroups[row][index])
                
                del self.batchlocations[self.locationgroups[row][index]]
                del self.locationgroups[row][index]
                child_item = True
          
        # do a bit of housekeeping now that batchlocations has changed
        self.reindex_locationgroups()
        self.load_definition(False)
        self.generate_batchconnections() # generate new connections list
        
        if child_item:
            index = self.model.index(row, 0)
            self.view.setExpanded(index, True)        
        
        self.statusbar.showMessage(self.tr("Batch location(s) removed"),3000)
    
    def edit_batchlocation_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"),3000)
            return
        
        if (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            row = self.view.selectedIndexes()[0].row()         
            
            # check if all the child elements are of the same class
            reference = self.batchlocations[self.locationgroups[row][0]][0]
            for i, value in enumerate(self.locationgroups[row]):
                to_be_tested = self.batchlocations[self.locationgroups[row][i]][0]        
                if not (reference == to_be_tested):
                    self.statusbar.showMessage(self.tr("Not all batch locations in this group are of the same kind"),3000)
                    return
                    
            locationgroup_dialog = LocationgroupSettingsDialog(self.parent)
            locationgroup_dialog.setModal(True)
            locationgroup_dialog.show()             
        else:            
            batchlocation_dialog = BatchlocationSettingsDialog(self.parent)
            batchlocation_dialog.setModal(True)
            batchlocation_dialog.show() 

    def trash_batchlocation_view(self):

        if not len(self.batchlocations):
            return          
        
        reset_operators = self.parent.operators_widget.reset_operators
        reset_cassetteloops = self.parent.cassetteloops_widget.reset_cassetteloops
        reset_technicians = self.parent.technicians_widget.reset_technicians

        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all tools. Continue?"))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtWidgets.QMessageBox.Ok):
            reset_operators(0)            
            reset_cassetteloops(0)
            reset_technicians(0)            
            self.batchlocations = []
            self.locationgroups = []
            self.batchconnections = []
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Process flow']) 
            self.statusbar.showMessage(self.tr("All tools were removed"),3000)

    def generate_locationgroups(self):
        # generate a default locationgroups list from batchlocations

        self.locationgroups = []
        num = 0
        for i, value in enumerate(self.batchlocations):
            # generate new locationgroups
            
            if (i == 0):
                self.locationgroups.insert(num,[0])
                num += 1
            elif (self.batchlocations[i][0] == self.batchlocations[i-1][0]):
                self.locationgroups[num-1].append(i)
            else:
                self.locationgroups.insert(num,[i])
                num += 1

    def generate_batchconnections(self):
        # generate a default batchconnections list from locationgroups        
        self.batchconnections = []

        transport_time = 60 # default duration for transport action
        time_per_unit = 10 # default additional duration for each unit
        min_units = 1 # default minimum number of units for transport
        max_units = 99 # default maximum number of units for transport

        for i in range(len(self.locationgroups)-1):
            for j, value in enumerate(self.locationgroups[i]):
                for k, value in enumerate(self.locationgroups[i+1]):
                    self.batchconnections.append([[i,j],[i+1,k],transport_time,time_per_unit,min_units,max_units])