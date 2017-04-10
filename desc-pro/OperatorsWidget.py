# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from copy import deepcopy
from dialogs.AddOperatorConnectionDialog import AddOperatorConnectionDialog
from dialogs.OperatorSettingsDialog import OperatorSettingsDialog
from dialogs.ConnectionSettingsDialog import ConnectionSettingsDialog

class OperatorsWidget(QtCore.QObject):
    def __init__(self, parent=None):
        super(OperatorsWidget, self).__init__(parent)

        self.parent = parent
        self.operators = []
        self.view = self.parent.operators_view        
        self.model = self.parent.operators_model
        self.statusbar = self.parent.statusBar()
        
    def load_definition(self, default=True):

        if (default): # generate default operator list based on locationgroup            
            self.generate_operators()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Operators'])                       

        for i in range(len(self.operators)):
            parent = QtGui.QStandardItem('Operator ' + self.operators[i][1]['name'])

            for j in range(len(self.operators[i][0])): 
                child = QtGui.QStandardItem(self.print_batchconnection(self.operators[i][0][j]))
                parent.appendRow(child)
            self.model.appendRow(parent)
            #self.view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True) 
            index = self.model.index(i, 0)
            self.view.setExpanded(index, True)            

    def import_batchlocations(self):
        self.load_definition() # default operators list
        self.statusbar.showMessage(self.tr("Operators automatically generated"))

    def print_batchlocation(self, num):
        
        batchlocations = self.parent.tools_widget.batchlocations
        
        if (num >= len(batchlocations)):
            return "Error"
            
        return batchlocations[num][0] + " " + batchlocations[num][1]['name']

    def print_batchconnection(self, num):

        locationgroups = self.parent.tools_widget.locationgroups
        batchconnections = self.parent.tools_widget.batchconnections        
        
        if (num >= len(batchconnections)):
            return "Error"
            
        value1 = locationgroups[batchconnections[num][0][0]][batchconnections[num][0][1]]
        value2 = locationgroups[batchconnections[num][1][0]][batchconnections[num][1][1]]

        return self.print_batchlocation(value1) + " -> " + self.print_batchlocation(value2)           

    def generate_operators(self):
        # generate a default operators list from batchconnections list

        locationgroups = self.parent.tools_widget.locationgroups
        batchconnections = self.parent.tools_widget.batchconnections
        
        self.operators = []    
        for i in range(len(locationgroups)-1):
            # make as many operators as there are locationgroups minus one
            self.operators.append([[],{'name' : str(i)}])
            
        num = 0
        curr_locationgroup = 0
        for i, value in enumerate(batchconnections):
            if (batchconnections[i][0][0] == curr_locationgroup):
                self.operators[num][0].append(i)
            else:
                curr_locationgroup = batchconnections[i][0][0]
                num += 1
                self.operators[num][0].append(i)
        
    def add_operator_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.add_operator(True)
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.add_operator()
        else: # if child row is selected
            self.add_operator_batchconnections()
            
    def add_operator(self, append_mode = False):
        batchconnections = self.parent.tools_widget.batchconnections
        
        if (append_mode):
            if (len(batchconnections) > 0):
                self.operators.append([[0],{'name' : 'new'}])
       
                # reload definitions
                self.load_definition(False)
        
                index = self.model.index(len(self.operators), 0)
                self.view.setCurrentIndex(index)
            else:
                self.statusbar.showMessage(self.tr("No batch connections available for new operator"))
                return
        else:                      
            # find out which operator was selected
            row = self.view.selectedIndexes()[0].row()
        
            # copy selected operator and give it name 'new'
            self.operators.insert(row,deepcopy(self.operators[row]))
            self.operators[row][1].update({'name' : 'new'})
        
            # reload definitions
            self.load_definition(False)
        
            index = self.model.index(row, 0)
            self.view.setCurrentIndex(index)
        
        self.statusbar.showMessage(self.tr("Operator added"))

    def add_operator_batchconnections(self):        
        # start dialog to enable user to add operator
        connection_dialog = AddOperatorConnectionDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()   

    def del_operator_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"))
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.del_operator()
        else: # if child row is selected
            self.del_operator_batchconnections()

    def del_operator(self):
        # find out which operator was selected
        row = self.view.selectedIndexes()[0].row()
        
        # remove selected operator
        del self.operators[row]
        
        # reload definitions
        self.parent.load_definition_operators(False)        
        
        self.statusbar.showMessage(self.tr("Operator removed"))
            
    def del_operator_batchconnections(self):
        # find out which connection was selected
        row = self.view.selectedIndexes()[0].parent().row()
        index = self.view.selectedIndexes()[0].row()

        if (len(self.operators[row][0]) == 1):
            # if last child item, remove the operator
            del self.operators[row]
            
            # reload definition into view
            self.load_definition(False) 
            
            self.statusbar.showMessage("Last operator connection and operator removed")            
        else:
            del self.operators[row][0][index]
            
            # reload definition into view
            self.load_definition(False)

            # re-expand the operator parent item
            index = self.model.index(row, 0)
            self.view.setExpanded(index, True) 
            
            self.statusbar.showMessage("Operator connection removed") 

    def reset_operators(self, tool_number):
        # reset connection list of operators whose connections have become invalid
        # tool_number is batchlocations list location that was changed
    
        batchconnections = self.parent.tools_widget.batchconnections
        batchlocations = self.parent.tools_widget.batchlocations    
        locationgroups = self.parent.tools_widget.locationgroups

        if not len(batchlocations):
            return
        
        # find first batchconnection that refers to changed tool
        changed_connection = -1
        for i in range(len(batchconnections)):
            origin = batchconnections[i][0]
            destination = batchconnections[i][1]
            origin_toolnumber = locationgroups[origin[0]][origin[1]]
            destination_toolnumber = locationgroups[destination[0]][destination[1]]
            
            if origin_toolnumber == tool_number or destination_toolnumber == tool_number:
                changed_connection = i
                break

        if changed_connection == -1:
            return
        
        for i in range(len(self.operators)):
            reset_list = []
            for j, value in enumerate(self.operators[i][0]): # all connections                    
                if value >= changed_connection:
                    reset_list.append(j)
            
            for k in sorted(reset_list, reverse=True):
                del self.operators[i][0][k]
            
        self.load_definition(False)

    def edit_operator_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select position"))
        elif (self.view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.edit_operator()
        else: # if child row is selected
            self.edit_batchconnection()

    def edit_operator(self):
        # start dialog to enable user to change settings        
        batchlocation_dialog = OperatorSettingsDialog(self.parent)  
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()        

    def edit_batchconnection(self):
        batchconnections = self.parent.tools_widget.batchconnections        
        
        # find out which connection was selected
        row = self.view.selectedIndexes()[0].parent().row()
        index = self.view.selectedIndexes()[0].row()       
        batchconnection = batchconnections[self.operators[row][0][index]]

        # start dialog to enable user to change settings
        connection_dialog = ConnectionSettingsDialog(self.parent,batchconnection)
        connection_dialog.setModal(True)
        connection_dialog.show()  

    def trash_operator_view(self):
        
        if not len(self.operators):
            return
        
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all operators. Continue?"))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtWidgets.QMessageBox.Ok):
            self.trash_operators()
            
    def trash_operators(self):            
        self.operators = []
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Operators']) 
        self.statusbar.showMessage(self.tr("All operators were removed"))
