# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from dialogs.AddTechnicianToolDialog import AddTechnicianToolDialog
from dialogs.TechnicianSettingsDialog import TechnicianSettingsDialog
from copy import deepcopy

class TechniciansWidget(QtCore.QObject):
    def __init__(self, parent=None):
        super(TechniciansWidget, self).__init__(parent)
        self.parent = parent
        self.technicians = []
        self.view = self.parent.technicians_view        
        self.model = self.parent.technicians_model
        self.statusbar = self.parent.statusBar()        

    def load_definition(self, default=True):

        if (default): # generate default technicians list based on batchlocationgroup
            self.generate_technicians()

        batchlocations = self.parent.batchlocations

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Technicians'])                       

        for i in range(len(self.technicians)):
            parent = QtGui.QStandardItem('Technician ' + self.technicians[i][1]['name'])

            for j, value in enumerate(self.technicians[i][0]):
                item = batchlocations[value][0] + " " + batchlocations[value][1]['name']
                child = QtGui.QStandardItem(item)
                parent.appendRow(child)
            self.model.appendRow(parent)

    def import_batchlocations_tech(self):
        self.load_definition() # default technicians list
        self.statusbar.showMessage(self.tr("Technicians automatically generated"))

    def generate_technicians(self):
        # generate a default technician list from batchlocations list

        self.technicians = []
        batchlocations = self.parent.batchlocations
        
        wet_chem_list = ['BatchClean','BatchTex','SingleSideEtch']
        backend_list = ['TubeFurnace','IonImplanter','WaferStacker','WaferUnstacker','PlasmaEtcher']
        frontend_list = ['TubePECVD','InlinePECVD','PrintLine','SpatialALD']
        
        # make three technicians by default
        self.technicians.append([[],{'name' : 'chem'}])
        self.technicians.append([[],{'name' : 'back'}])
        self.technicians.append([[],{'name' : 'front'}])
        
        for i, value in enumerate(batchlocations):
            
            if value[0] in wet_chem_list:
                self.technicians[0][0].append(i)

            if value[0] in backend_list:
                self.technicians[1][0].append(i)

            if value[0] in frontend_list:
                self.technicians[2][0].append(i)

    def add_technician_view(self):
        
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.add_technician(True)
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.add_technician()
        else: # if child row is selected
            self.add_technician_tool()  

    def add_technician(self, append_mode = False):

        batchlocations = self.parent.batchlocations
        
        tools_list = ['BatchClean','BatchTex','SingleSideEtch','TubeFurnace','IonImplanter',\
                      'WaferStacker','WaferUnstacker','PlasmaEtcher','TubePECVD','InlinePECVD','PrintLine','SpatialALD']        
        
        tool = -1 # find first suitable tool for new technician
        for i, value in enumerate(batchlocations):
            if value[0] in tools_list:
                tool = i
                break
            
        if tool == -1:
            self.statusbar.showMessage(self.tr("No tools available for new technician"))
            return            
        
        if (append_mode):
            
            self.technicians.append([[tool],{'name' : 'new'}])
       
            # reload definitions
            self.load_definition(False)
        
            index = self.model.index(len(self.technicians), 0)
            self.view.setCurrentIndex(index)

        else:                      
            # find out which operator was selected
            row = self.view.selectedIndexes()[0].row()
        
            # copy selected operator and give it name 'new'
            self.technicians.insert(row,deepcopy(self.technicians[row]))
            self.technicians[row][1].update({'name' : 'new'})
        
            # reload definitions
            self.load_definition(False)
        
            index = self.model.index(row, 0)
            self.view.setCurrentIndex(index)
        
        self.statusbar.showMessage(self.tr("Technician added"))

    def add_technician_tool(self):        
        # start dialog to enable user to add tools for technician        
        connection_dialog = AddTechnicianToolDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()

    def del_technician_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"))
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.del_technician()
        else: # if child row is selected
            self.del_technician_batchlocations()

    def del_technician(self):
        # find out which operator was selected
        row = self.view.selectedIndexes()[0].row()
        
        # remove selected operator
        del self.technicians[row]
        
        # reload definitions
        self.load_definition(False)        
        
        self.statusbar.showMessage(self.tr("Technician removed"))
            
    def del_technician_batchlocations(self):
        # find out which connection was selected
        row = self.view.selectedIndexes()[0].parent().row()
        index = self.view.selectedIndexes()[0].row()

        if (len(self.technicians[row][0]) == 1):
            # if last child item, remove the operator
            del self.technicians[row]
            
            # reload definition into view
            self.load_definition(False) 
            
            self.statusbar.showMessage("Last tool and technician removed")            
        else:
            del self.technicians[row][0][index]            
            
            # reload definition into view
            self.load_definition(False)

            # re-expand the operator parent item
            index = self.model.index(row, 0)
            self.view.setExpanded(index, True) 
            
            self.statusbar.showMessage("Technician tool removed")

    def edit_technician_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"))
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.edit_technician()
        else: # if child row is selected
            self.statusbar.showMessage(self.tr("No tool settings available"))

    def edit_technician(self):
        # start dialog to enable user to change settings        
        batchlocation_dialog = TechnicianSettingsDialog(self.parent)  
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show() 

    def trash_technician_view(self):
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all technicians. Continue?"))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtWidgets.QMessageBox.Ok):
            self.technicians = []
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Technicians']) 
            self.statusbar.showMessage(self.tr("All technicians were removed"))