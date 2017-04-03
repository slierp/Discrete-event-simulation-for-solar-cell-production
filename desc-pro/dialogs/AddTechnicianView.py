# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from copy import deepcopy
from dialogs.AddTechnicianToolDialog import AddTechnicianToolDialog

class AddTechnicianView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (not len(self.parent.technicians_view.selectedIndexes())):
            # if nothing selected
            self.add_technician(True)
        elif (self.parent.technicians_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.add_technician()
        else: # if child row is selected
            self.add_technician_tool()
            
    def add_technician(self, append_mode = False):

        tools_list = ['BatchClean','BatchTex','SingleSideEtch','TubeFurnace','IonImplanter',\
                      'WaferStacker','WaferUnstacker','PlasmaEtcher','TubePECVD','InlinePECVD','PrintLine','SpatialALD']        
        
        tool = -1 # find first suitable tool for new technician
        for i, value in enumerate(self.parent.batchlocations):
            if value[0] in tools_list:
                tool = i
                break
            
        if tool == -1:
            self.parent.statusBar().showMessage(self.tr("No tools available for new technician"))
            return            
        
        if (append_mode):
            
            self.parent.technicians.append([[tool],{'name' : 'new'}])
       
            # reload definitions
            self.parent.load_definition_technicians(False)
        
            index = self.parent.technicians_model.index(len(self.parent.technicians), 0)
            self.parent.technicians_view.setCurrentIndex(index)

        else:                      
            # find out which operator was selected
            row = self.parent.technicians_view.selectedIndexes()[0].row()
        
            # copy selected operator and give it name 'new'
            self.parent.technicians.insert(row,deepcopy(self.parent.technicians[row]))
            self.parent.technicians[row][1].update({'name' : 'new'})
        
            # reload definitions
            self.parent.load_definition_technicians(False)
        
            index = self.parent.technicians_model.index(row, 0)
            self.parent.technicians_view.setCurrentIndex(index)
        
        self.parent.statusBar().showMessage(self.tr("Technician added"))

    def add_technician_tool(self):        
        # start dialog to enable user to tools for technician        
        connection_dialog = AddTechnicianToolDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()            