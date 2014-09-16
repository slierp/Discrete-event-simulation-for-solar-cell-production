# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:19:49 2014

@author: rnaber
"""

from __future__ import division
import numpy as np
from PyQt4 import QtCore, QtGui
import os, ntpath
from batchlocations.WaferSource import WaferSource
from batchlocations.WaferUnstacker import WaferUnstacker
from batchlocations.WaferBin import WaferBin
from batchlocations.BatchTex import BatchTex
from batchlocations.TubeFurnace import TubeFurnace
from batchlocations.SingleSideEtch import SingleSideEtch
from batchlocations.TubePECVD import TubePECVD
from batchlocations.PrintLine import PrintLine
from batchlocations.Operator import Operator
from RunSimulationThread import RunSimulationThread
from BatchlocationSettingsDialog import BatchlocationSettingsDialog
from OperatorSettingsDialog import OperatorSettingsDialog
from AddBatchlocationDialog import AddBatchlocationDialog
from ConnectionSettingsDialog import ConnectionSettingsDialog
from AddOperatorConnectionDialog import AddOperatorConnectionDialog
from copy import deepcopy
import pickle

class dummy_env(object):
    
    def process(dummy0=None,dummy1=None):
        pass

    def now(self):
        pass
    
    def event(dummy0=None):
        pass

class MainGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell manufacturing simulation"))
        self.setWindowIcon(QtGui.QIcon(":Logo_Tempress.png"))
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # DISABLE BEFORE RELEASE

        self.edit = QtGui.QTextEdit()
        self.edit.setReadOnly(True)               

        self.simulation_thread = RunSimulationThread(self.edit)
        self.simulation_thread.signal.sig.connect(self.simulation_end_signal)
        self.simulation_thread.output.sig.connect(self.simulation_output)

        self.prev_dir_path = ""
        self.prev_save_path = ""

        self.batchlocations_model = QtGui.QStandardItemModel()
        self.batchlocations_view = QtGui.QTreeView()
        self.batchlocations_view.doubleClicked.connect(self.edit_batchlocation_view)
        self.batchlocations_view.setAlternatingRowColors(True)
        self.operators_model = QtGui.QStandardItemModel()
        self.operators_view = QtGui.QTreeView()
        self.operators_view.doubleClicked.connect(self.edit_operator_view)
        self.operators_view.setAlternatingRowColors(True)
        self.batchlocation_dialog = None

        self.modified_batchlocation_number = None

        self.batchlocations = [] #tool class name, no of tools, dict with settings
        self.batchlocations.append(["WaferSource", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker",{'name' : '1'}])
        self.batchlocations.append(["BatchTex", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '1'}])
        self.batchlocations.append(["SingleSideEtch", {'name' : '0'}])
        self.batchlocations.append(["TubePECVD", {'name' : '0'}])
        self.batchlocations.append(["TubePECVD", {'name' : '1'}])
        self.batchlocations.append(["PrintLine", {'name' : '0'}])
        self.batchlocations.append(["PrintLine", {'name' : '1'}])

        self.locationgroups = []
        self.batchconnections = []
        self.operators = []

        self.sim_time_selection_list = ['1 hour','1 day','1 week','1 month','1 year']

        self.params = {}
        self.params['time_limit'] = 60*60
        
        self.create_menu()
        self.create_main_frame()
        self.load_definition_batchlocations()
        self.load_definition_operators()

    def open_file(self):

        filename = QtGui.QFileDialog.getOpenFileName(self,self.tr("Open file"), self.prev_dir_path, "Description Files (*.desc)")
        
        if (not filename):
            return

        if (not os.path.isfile(filename.toAscii())):
            msg = self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            QtGui.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
        self.prev_save_path = str(filename)
        self.prev_dir_path = ntpath.dirname(str(filename))
        
        with open(str(filename)) as f:
            self.batchlocations,self.locationgroups,self.batchconnections,self.operators = pickle.load(f)
        
        self.load_definition_batchlocations(False)
        self.load_definition_operators(False) 
            
        self.statusBar().showMessage(self.tr("New description loaded"))

    def save_to_file(self):
        
        if (not self.prev_save_path):
            self.save_to_file_as()
            return
        
        with open(self.prev_save_path, 'w') as f:
            pickle.dump([self.batchlocations,self.locationgroups,self.batchconnections,self.operators], f)
            
        self.statusBar().showMessage(self.tr("File saved"))

    def save_to_file_as(self):

        filename = QtGui.QFileDialog.getSaveFileName(self,self.tr("Save file"), self.prev_dir_path, "Description Files (*.desc)")
        
        if (not filename):
            return
            
        # Check for non-ASCII here does not seem to work
        
        self.prev_save_path = str(filename)
        self.prev_dir_path = ntpath.dirname(str(filename))
        
        with open(str(filename), 'w') as f:
            pickle.dump([self.batchlocations,self.locationgroups,self.batchconnections,self.operators], f)
            
        self.statusBar().showMessage(self.tr("File saved"))            

    def load_definition_batchlocations(self, default=True):

        if (default): # generate default locationgroup arrangement by batchlocation contents        
            self.exec_batchlocations()
            
        self.exec_locationgroups() # make sure batchconnections are updated every time locationgroups changes
        self.batchlocations_model.clear()
        self.batchlocations_model.setHorizontalHeaderLabels(['Batch locations'])           

        for i, value in enumerate(self.locationgroups):
            parent = QtGui.QStandardItem(self.batchlocations[self.locationgroups[i][0]][0])

            for j in self.locationgroups[i]:
                child = QtGui.QStandardItem(self.batchlocations[j][1]['name'])
                parent.appendRow(child)
            self.batchlocations_model.appendRow(parent)
            self.batchlocations_view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True)            

    def load_definition_operators(self, default=True):

        if (default): # generate default operator list based on locationgroup
            self.exec_batchconnections()

        self.operators_model.clear()
        self.operators_model.setHorizontalHeaderLabels(['Operators'])                       

        for i, value in enumerate(self.operators):
            parent = QtGui.QStandardItem('Operator ' + self.operators[i][1]['name'])

            for j, value in enumerate(self.operators[i][0]):               
                child = QtGui.QStandardItem(self.print_batchconnection(self.operators[i][0][j]))
                parent.appendRow(child)
            self.operators_model.appendRow(parent)
            self.operators_view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True) 

    def reindex_locationgroups(self):
        # change it so that all indexes are consecutive, which should always be the case
        num = 0
        for i, value0 in enumerate(self.locationgroups):
            for j, value1 in enumerate(self.locationgroups[i]):
                self.locationgroups[i][j] = num
                num += 1

    def add_batchlocation_view(self):
        if (not len(self.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
            return
            
        if (self.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            row = self.batchlocations_view.selectedIndexes()[0].row()
            index = None
        else:
            row = self.batchlocations_view.selectedIndexes()[0].parent().row()
            index = self.batchlocations_view.selectedIndexes()[0].row()

        # start dialog to enable user to add batch location
        add_batchlocation_dialog = AddBatchlocationDialog(self,row,index)
        add_batchlocation_dialog.setModal(True)
        add_batchlocation_dialog.show()

    def del_batchlocation_view(self):
        if (not len(self.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
            return
        
        child_item = False
        
        if (self.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent item, remove all batchlocation children and row in locationgroups
        
            row = self.batchlocations_view.selectedIndexes()[0].row() # selected row in locationgroups            
            del self.batchlocations[self.locationgroups[row][0]:self.locationgroups[row][len(self.locationgroups[row])-1]+1]
            del self.locationgroups[row]            

        else: # if child item
            row = self.batchlocations_view.selectedIndexes()[0].parent().row() # selected row in locationgroups
            
            if (len(self.locationgroups[row]) == 1):
                # if last child item, remove batchlocation and whole row in locationgroups
                del self.batchlocations[self.locationgroups[row][0]:self.locationgroups[row][len(self.locationgroups[row])-1]+1]
                del self.locationgroups[row]
            else:
                # if not last child item, remove batchlocation and element in locationgroup row
                index = self.batchlocations_view.selectedIndexes()[0].row()
                del self.batchlocations[self.locationgroups[row][index]]
                del self.locationgroups[row][index]
                child_item = True
      
        self.reindex_locationgroups()
        self.load_definition_batchlocations(False)
        
        if child_item:
            index = self.batchlocations_model.index(row, 0)
            self.batchlocations_view.setExpanded(index, True)        
        
        self.statusBar().showMessage(self.tr("Batch location(s) removed"))

    #def up_batchlocation(self):
    #    pass

    #def down_batchlocation(self):
    #    pass
    
    def edit_batchlocation_view(self):
        if (not len(self.batchlocations_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
            return
        elif (self.batchlocations_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            # TO BE IMPLEMENTED: change all children, provided that they are of the same class
            self.statusBar().showMessage("Not yet implemented")            
            return

        # find out which batchlocation was selected
        row = self.batchlocations_view.selectedIndexes()[0].parent().row()
        index = self.batchlocations_view.selectedIndexes()[0].row()
        self.modified_batchlocation_number = self.locationgroups[row][index]       
        batchlocation = self.batchlocations[self.modified_batchlocation_number]

        env = dummy_env()
        curr_params = {}
        # load default settings list
        if (batchlocation[0] == "WaferSource"):
            curr_params = WaferSource(env).params
        elif (batchlocation[0] == "WaferUnstacker"):
            curr_params = WaferUnstacker(env).params
        elif (batchlocation[0] == "BatchTex"):
            curr_params = BatchTex(env).params
        elif (batchlocation[0] == "TubeFurnace"):
            curr_params = TubeFurnace(env).params
        elif (batchlocation[0] == "SingleSideEtch"):
            curr_params = SingleSideEtch(env).params
        elif (batchlocation[0] == "TubePECVD"):
            curr_params = TubePECVD(env).params
        elif (batchlocation[0] == "PrintLine"):
            curr_params = PrintLine(env).params            
        elif (batchlocation[0] == "WaferBin"):
            curr_params = WaferBin(env).params
        else:
            return                         
        
        # update default settings list with currently stored settings
        curr_params.update(batchlocation[1])

        # start dialog to enable user to change settings
        batchlocation_dialog = BatchlocationSettingsDialog(self,curr_params,row)
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()

    def print_batchlocation(self, num):
        return self.batchlocations[num][0] + " " + self.batchlocations[num][1]['name']

    def exec_batchlocations(self):
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

    def exec_locationgroups(self):
        # generate a default batchconnections list from locationgroups        
        self.batchconnections = []

        transport_time = 90
        time_per_unit = 20
                           
        #num = 0
        for i in np.arange(len(self.locationgroups)-1):
            for j, value in enumerate(self.locationgroups[i]):
                for k, value in enumerate(self.locationgroups[i+1]):
                    #self.batchconnections[num] = [[i,j],[i+1,k],transport_time, time_per_unit]
                    self.batchconnections.append([[i,j],[i+1,k],transport_time, time_per_unit])
                    #num  += 1                            

    def import_batchlocations(self):
        self.exec_locationgroups() # reload connections again just to be sure
        self.load_definition_operators() # default operators list
        self.statusBar().showMessage(self.tr("Batch locations imported"))

    def print_batchconnection(self, num):
        value1 = self.locationgroups[self.batchconnections[num][0][0]][self.batchconnections[num][0][1]]
        value2 = self.locationgroups[self.batchconnections[num][1][0]][self.batchconnections[num][1][1]]
        self.print_batchlocation
        return self.print_batchlocation(value1) + " -> " + self.print_batchlocation(value2)           

    def exec_batchconnections(self):
        # generate a default operators list from batchconnections list
        
        self.operators = []    
        for i in np.arange(len(self.locationgroups)-1):
            # make as many operators as there are locationgroups minus one
            self.operators.append([[],{'name' : str(i)}])
            
        num = 0
        curr_locationgroup = 0
        for i, value in enumerate(self.batchconnections):
            if (self.batchconnections[i][0][0] == curr_locationgroup):
                self.operators[num][0].append(i)
            else:
                curr_locationgroup = self.batchconnections[i][0][0]
                num += 1
                self.operators[num][0].append(i)

    def add_operator_batchconnections(self):
        # find out which connection was selected
        row = self.operators_view.selectedIndexes()[0].parent().row()
        index = self.operators_view.selectedIndexes()[0].row()
        
        # start dialog to enable user to add operator
        connection_dialog = AddOperatorConnectionDialog(self,row,index)
        connection_dialog.setModal(True)
        connection_dialog.show()        

    def del_operator_batchconnections(self):
        # find out which connection was selected
        row = self.operators_view.selectedIndexes()[0].parent().row()
        index = self.operators_view.selectedIndexes()[0].row()

        if (len(self.operators[row][0]) == 1):
            # if last child item, remove the operator
            del self.operators[row]
            
            # reload definition into view
            self.load_definition_operators(False) 
            
            self.statusBar().showMessage("Last operator connection and operator removed")            
        else:
            del self.operators[row][0][index]
            
            # reload definition into view
            self.load_definition_operators(False)

            # re-expand the operator parent item
            index = self.operators_model.index(row, 0)
            self.operators_view.setExpanded(index, True) 
            
            self.statusBar().showMessage("Operator connection removed")          

    def edit_batchconnection(self):
        # find out which connection was selected
        row = self.operators_view.selectedIndexes()[0].parent().row()
        index = self.operators_view.selectedIndexes()[0].row()
        self.modified_batchconnection_number = self.operators[row][0][index]       
        batchconnection = self.batchconnections[self.modified_batchconnection_number]

        # start dialog to enable user to change settings
        connection_dialog = ConnectionSettingsDialog(self,batchconnection)
        connection_dialog.setModal(True)
        connection_dialog.show()

    def add_operator(self):
        # find out which operator was selected
        row = self.operators_view.selectedIndexes()[0].row()
        
        # copy selected operator and give it name 'new'
        self.operators.insert(row,deepcopy(self.operators[row]))
        self.operators[row][1].update({'name' : 'new'})
        
        # reload definitions
        self.load_definition_operators(False)
        
        index = self.operators_model.index(row, 0)
        self.operators_view.setCurrentIndex(index)
        
        self.statusBar().showMessage(self.tr("Operator added"))

    def del_operator(self):
        # find out which operator was selected
        row = self.operators_view.selectedIndexes()[0].row()
        
        # remove selected operator
        del self.operators[row]
        
        # reload definitions
        self.load_definition_operators(False)        
        
        self.statusBar().showMessage(self.tr("Operator removed"))

    def edit_operator(self):
        # find out which operator was selected
        row = self.operators_view.selectedIndexes()[0].row()

        env = dummy_env()
        curr_params = {}
        # load default settings list
        curr_params = Operator(env).params

        # update default settings list with currently stored settings
        curr_params.update(self.operators[row][1])

        # start dialog to enable user to change settings
        batchlocation_dialog = OperatorSettingsDialog(self,curr_params,row)
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()

    def add_operator_view(self):
        if (not len(self.operators_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
        elif (self.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.add_operator()
        else: # if child row is selected
            self.add_operator_batchconnections()

    def del_operator_view(self):
        if (not len(self.operators_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
        elif (self.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.del_operator()
        else: # if child row is selected
            self.del_operator_batchconnections()

    def edit_operator_view(self):
        if (not len(self.operators_view.selectedIndexes())):
            # if nothing selected
            self.statusBar().showMessage(self.tr("Please select position"))
        elif (self.operators_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.edit_operator()
        else: # if child row is selected
            self.edit_batchconnection()

    def run_simulation(self):
        
        for i, value in enumerate(self.batchconnections):
            # check if all batchconnections exist inside locationgroups
            # no separate check whether all batchlocations inside locationgroups exist
            # since GUI should not allow for any errors to appear
            if (self.batchconnections[i][0][0] > (len(self.locationgroups)-1)) | \
                    (self.batchconnections[i][1][0] > (len(self.locationgroups)-1)):
                self.statusBar().showMessage(self.tr("Invalid batchconnections found"))
                return
            elif (self.batchconnections[i][0][1] > (len(self.locationgroups[self.batchconnections[i][0][0]])-1)) | \
                    (self.batchconnections[i][1][1] > (len(self.locationgroups[self.batchconnections[i][1][0]])-1)):
                self.statusBar().showMessage(self.tr("Invalid batchconnections found"))
                return
        
        time_limits = [60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]
        for i, value in enumerate(self.sim_time_selection_list):
            if (value == self.sim_time_combo.currentText()):
                self.params['time_limit'] = time_limits[i]
        
        if not self.simulation_thread.isRunning():
        #if True: # interchange for isRunning when not running simulation in separate thread
            self.edit.clear()
            self.simulation_thread.batchlocations = deepcopy(self.batchlocations)
            self.simulation_thread.locationgroups = deepcopy(self.locationgroups)
            self.simulation_thread.batchconnections = deepcopy(self.batchconnections)
            self.simulation_thread.operators = deepcopy(self.operators)

            self.simulation_thread.params = {}
            self.simulation_thread.params['time_limit'] = 1000
            self.simulation_thread.params.update(self.params)
            
            self.simulation_thread.stop_simulation = False
            self.simulation_thread.start()
            #self.simulation_thread.run() # interchange for start when not running simulation in separate thread
            self.run_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)
            
            self.statusBar().showMessage(self.tr("Simulation started"))

    def stop_simulation(self):
        self.simulation_thread.stop_simulation = True
        self.statusBar().showMessage(self.tr("Simulation stop signal was sent"))

    @QtCore.pyqtSlot(str)
    def simulation_output(self,string):
        self.edit.insertPlainText(string + '\n')

    @QtCore.pyqtSlot(str)
    def simulation_end_signal(self):
        self.run_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)
        self.statusBar().showMessage(self.tr("Simulation has ended"))

    def on_about(self):
        msg = self.tr("Solar cell manufacturing simulation\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()        

        ##### Batch locations #####        
        self.batchlocations_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.batchlocations_view.setExpandsOnDoubleClick(False)
        self.batchlocations_model.setHorizontalHeaderLabels(['Batch locations'])
        self.batchlocations_view.setModel(self.batchlocations_model)
        self.batchlocations_view.setUniformRowHeights(True)
        self.batchlocations_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.batchlocations_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)          
        
        add_batchlocation_button = QtGui.QPushButton()
        add_batchlocation_button.clicked.connect(self.add_batchlocation_view)
        add_batchlocation_button.setIcon(QtGui.QIcon(":plus.png"))
        add_batchlocation_button.setToolTip(self.tr("Add batchlocation"))
        add_batchlocation_button.setStatusTip(self.tr("Add batchlocation"))
        
        del_batchlocation_button = QtGui.QPushButton()
        del_batchlocation_button.clicked.connect(self.del_batchlocation_view)
        del_batchlocation_button.setIcon(QtGui.QIcon(":minus.png"))
        del_batchlocation_button.setToolTip(self.tr("Remove batchlocation"))
        del_batchlocation_button.setStatusTip(self.tr("Remove batchlocation"))

        #up_batchlocation_button = QtGui.QPushButton()
        #up_batchlocation_button.clicked.connect(self.up_batchlocation)        
        #up_batchlocation_button.setIcon(QtGui.QIcon(":up.png"))
        #up_batchlocation_button.setToolTip(self.tr("Move up in list"))
        #up_batchlocation_button.setStatusTip(self.tr("Move up in list"))
        
        #down_batchlocation_button = QtGui.QPushButton()
        #down_batchlocation_button.clicked.connect(self.down_batchlocation)         
        #down_batchlocation_button.setIcon(QtGui.QIcon(":down.png"))
        #down_batchlocation_button.setToolTip(self.tr("Move down in list"))
        #down_batchlocation_button.setStatusTip(self.tr("Move down in list"))
        
        edit_batchlocation_button = QtGui.QPushButton()
        edit_batchlocation_button.clicked.connect(self.edit_batchlocation_view)        
        edit_batchlocation_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_batchlocation_button.setToolTip(self.tr("Edit settings"))
        edit_batchlocation_button.setStatusTip(self.tr("Edit settings"))        

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(add_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(del_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        #buttonbox0.addButton(up_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        #buttonbox0.addButton(down_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(edit_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)        

        vbox0 = QtGui.QVBoxLayout()
        vbox0.addWidget(self.batchlocations_view)
        vbox0.addWidget(buttonbox0)

        ##### Operators #####
        self.operators_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.operators_view.setExpandsOnDoubleClick(False)
        self.operators_model.setHorizontalHeaderLabels(['Operators'])
        self.operators_view.setModel(self.operators_model)
        self.operators_view.setUniformRowHeights(True)
        self.operators_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.operators_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        import_batchlocations_button = QtGui.QPushButton()
        import_batchlocations_button.clicked.connect(self.import_batchlocations)        
        import_batchlocations_button.setIcon(QtGui.QIcon(":import.png"))
        import_batchlocations_button.setToolTip(self.tr("Import locations"))
        import_batchlocations_button.setStatusTip(self.tr("Import locations"))

        add_operator_button = QtGui.QPushButton()
        add_operator_button.clicked.connect(self.add_operator_view)           
        add_operator_button.setIcon(QtGui.QIcon(":plus.png"))
        add_operator_button.setToolTip(self.tr("Add operator"))
        add_operator_button.setStatusTip(self.tr("Add operator"))
        
        del_operator_button = QtGui.QPushButton()
        del_operator_button.clicked.connect(self.del_operator_view)          
        del_operator_button.setIcon(QtGui.QIcon(":minus.png"))
        del_operator_button.setToolTip(self.tr("Remove operator"))
        del_operator_button.setStatusTip(self.tr("Remove operator"))

        edit_operator_button = QtGui.QPushButton()
        edit_operator_button.clicked.connect(self.edit_operator_view)        
        edit_operator_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_operator_button.setToolTip(self.tr("Edit settings"))
        edit_operator_button.setStatusTip(self.tr("Edit settings"))

        buttonbox1 = QtGui.QDialogButtonBox()
        buttonbox1.addButton(import_batchlocations_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(add_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(del_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(edit_operator_button, QtGui.QDialogButtonBox.ActionRole)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.operators_view)
        vbox1.addWidget(buttonbox1)

        ##### Top buttonbox #####

        open_file_button = QtGui.QPushButton()
        tip = self.tr("Open file")
        open_file_button.clicked.connect(self.open_file)        
        open_file_button.setIcon(QtGui.QIcon(":open.png"))
        open_file_button.setToolTip(tip)
        open_file_button.setStatusTip(tip)

        save_file_button = QtGui.QPushButton()
        tip = self.tr("Save to file")
        save_file_button.clicked.connect(self.save_to_file) 
        save_file_button.setIcon(QtGui.QIcon(":save.png"))
        save_file_button.setToolTip(tip)
        save_file_button.setStatusTip(tip)

        self.run_sim_button = QtGui.QPushButton()
        tip = self.tr("Run simulation")
        self.run_sim_button.clicked.connect(self.run_simulation)         
        self.run_sim_button.setIcon(QtGui.QIcon(":play.png"))
        self.run_sim_button.setToolTip(tip)
        self.run_sim_button.setStatusTip(tip)
        self.run_sim_button.setShortcut('Ctrl+R')
        
        self.stop_sim_button = QtGui.QPushButton()
        tip = self.tr("Stop simulation")
        self.stop_sim_button.clicked.connect(self.stop_simulation)          
        self.stop_sim_button.setIcon(QtGui.QIcon(":stop.png"))
        self.stop_sim_button.setToolTip(tip)
        self.stop_sim_button.setStatusTip(tip)
        self.stop_sim_button.setEnabled(False)
        self.stop_sim_button.setShortcut('Escape')

        top_buttonbox = QtGui.QDialogButtonBox()
        top_buttonbox.addButton(open_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(save_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.run_sim_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.stop_sim_button, QtGui.QDialogButtonBox.ActionRole)

        self.sim_time_combo = QtGui.QComboBox(self)
        for i in self.sim_time_selection_list:
            self.sim_time_combo.addItem(i)
        
        toolbar_hbox = QtGui.QHBoxLayout()
        toolbar_hbox.addWidget(top_buttonbox)
        toolbar_hbox.addWidget(self.sim_time_combo)        
        
        textbox_hbox = QtGui.QHBoxLayout()
        textbox_hbox.addWidget(self.edit)
        
        ##### Main layout #####
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.setDirection(QtGui.QBoxLayout.LeftToRight)
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)

        vbox = QtGui.QVBoxLayout()       
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox)
        vbox.addLayout(textbox_hbox)
                                                         
        self.main_frame.setLayout(vbox)

        self.setCentralWidget(self.main_frame)

        self.status_text = QtGui.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Ready"))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))

        tip = self.tr("Open file")        
        load_action = QtGui.QAction(self.tr("Open..."), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self.open_file)
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)
        load_action.setShortcut('Ctrl+O')

        tip = self.tr("Save to file")        
        save_action = QtGui.QAction(self.tr("Save"), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self.save_to_file)        
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)
        save_action.setShortcut('Ctrl+S')

        tip = self.tr("Save to file as...")        
        saveas_action = QtGui.QAction(self.tr("Save as..."), self)
        saveas_action.triggered.connect(self.save_to_file_as)         
        saveas_action.setToolTip(tip)
        saveas_action.setStatusTip(tip)        

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)        
        self.file_menu.addAction(quit_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(about_action)