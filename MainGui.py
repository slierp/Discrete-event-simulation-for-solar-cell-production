# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:19:49 2014

@author: rnaber
"""

from __future__ import division
import numpy as np
from PyQt4 import QtCore, QtGui
icon_name = ":Logo_Tempress.ico"

class MainGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell manufacturing simulation"))
        self.setWindowIcon(QtGui.QIcon(icon_name))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # DISABLE BEFORE RELEASE

        self.clip = QtGui.QApplication.clipboard()
        self.batchlocations_model = QtGui.QStandardItemModel()
        self.locationgroups_model = QtGui.QStandardItemModel()
        self.batchconnections_model = QtGui.QStandardItemModel()
        self.operators_model = QtGui.QStandardItemModel()

        self.batchlocations = {} #tool class name, no of tools, dict with settings
        self.batchlocations[0] = ["WaferSource", {'name' : '0'}]
        self.batchlocations[1] = ["WaferUnstacker", {'name' : '0'}]
        self.batchlocations[2] = ["WaferUnstacker",{'name' : '1'}]
        self.batchlocations[3] = ["BatchTex", {'name' : '0'}]
        self.batchlocations[4] = ["TubeFurnace", {'name' : '0'}]
        self.batchlocations[5] = ["TubeFurnace", {'name' : '1'}]
        self.batchlocations[6] = ["SingleSideEtch", {'name' : '0'}]
        self.batchlocations[7] = ["TubePECVD", {'name' : '0'}]
        self.batchlocations[8] = ["TubePECVD", {'name' : '1'}]
        self.batchlocations[9] = ["PrintLine", {'name' : '0'}]
        self.batchlocations[10] = ["PrintLine", {'name' : '1'}]

        self.locationgroups = {}
        self.batchconnections = {}
        
        self.create_menu()
        self.create_main_frame()
        self.load_default_line()

    def load_default_line(self):
        for i in self.batchlocations:
            item = QtGui.QStandardItem(str(i) + ".\t" + self.batchlocations[i][0])
            self.batchlocations_model.appendRow(item)                        
            
        self.exec_batchlocations()
        self.exec_locationgroups()

    def add_batchlocation(self):
        pass

    def del_batchlocation(self):
        pass
    
    def edit_batchlocation(self):
        pass    

    def up_batchlocation(self):
        pass

    def down_batchlocation(self):
        pass

    def exec_batchlocations(self):
        # first read batchlocations_model and then generate a locationgroups list
        # read step not yet implemented

        self.locationgroups = {}
        num = 0
        for i in self.batchlocations:
            # generate new locationgroups
            
            if (i == 0):
                self.locationgroups[num] = [0]
                num += 1
            elif (self.batchlocations[i][0] == self.batchlocations[i-1][0]):
                self.locationgroups[num-1].append(i)
            else:
                self.locationgroups[num] = [i]
                num += 1

        self.locationgroups_model.clear()

        for i in self.locationgroups:
            # enter new locationgroups list into location groups model
            number_list = ""
            for j, value in enumerate(self.locationgroups[i]):
                if (j == 0):
                    number_list += str(i) + ".\t" + str(value)
                else:
                    number_list += ", " + str(value)
            
            item = QtGui.QStandardItem(number_list)
            self.locationgroups_model.appendRow(item)

    def add_locationgroup(self):
        pass
    
    def del_locationgroup(self):
        pass    

    def exec_locationgroups(self):
        # first read locationgroups_model and then generate a batchconnections list
        # read step not yet implemented        
        self.batchconnections = {}

        transport_time = 90
        time_per_unit = 20
                           
        num = 0
        for i in np.arange(len(self.locationgroups)-1):
            for j, value in enumerate(self.locationgroups[i]):
                for k, value in enumerate(self.locationgroups[i+1]):
                    self.batchconnections[num] = [[i,j],[i+1,k],transport_time, time_per_unit]
                    num  += 1
                            
        self.batchconnections_model.clear()

        for i in self.batchconnections:
            value1 = self.locationgroups[self.batchconnections[i][0][0]][self.batchconnections[i][0][1]]
            value2 = self.locationgroups[self.batchconnections[i][1][0]][self.batchconnections[i][1][1]]
            number_list = str(i) + ".\t" + str(value1) + " -> " + str(value2)           
            item = QtGui.QStandardItem(number_list)
            self.batchconnections_model.appendRow(item)

    def edit_batchconnection(self):
        pass

    def exec_batchconnections(self):
        # first read batchconnections_model and then generate an operators list
        # not yet implemented 
        pass

    def add_operator(self):
        pass

    def del_operator(self):
        pass

    def edit_operator(self):
        pass    

    def on_about(self):
        msg = self.tr("Solar cell manufacturing simulation\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()        

        ##### Batch locations #####        
        vbox0_label = QtGui.QLabel(self.tr("Batch locations:"))
        
        batchlocations_view = QtGui.QListView()
        batchlocations_view.setModel(self.batchlocations_model)
        batchlocations_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        batchlocations_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)      
        
        add_batchlocation_button = QtGui.QPushButton()
        self.connect(add_batchlocation_button, QtCore.SIGNAL('clicked()'), self.add_batchlocation)
        add_batchlocation_button.setIcon(add_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        add_batchlocation_button.setToolTip(self.tr("Add batchlocation"))
        add_batchlocation_button.setStatusTip(self.tr("Add batchlocation"))
        
        del_batchlocation_button = QtGui.QPushButton()
        self.connect(del_batchlocation_button, QtCore.SIGNAL('clicked()'), self.del_batchlocation)
        del_batchlocation_button.setIcon(del_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        del_batchlocation_button.setToolTip(self.tr("Remove batchlocation"))
        del_batchlocation_button.setStatusTip(self.tr("Remove batchlocation"))

        edit_batchlocation_button = QtGui.QPushButton()
        self.connect(edit_batchlocation_button, QtCore.SIGNAL('clicked()'), self.edit_batchlocation)
        edit_batchlocation_button.setIcon(edit_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        edit_batchlocation_button.setToolTip(self.tr("Edit settings"))
        edit_batchlocation_button.setStatusTip(self.tr("Edit settings"))

        up_batchlocation_button = QtGui.QPushButton()
        self.connect(up_batchlocation_button, QtCore.SIGNAL('clicked()'), self.up_batchlocation)
        up_batchlocation_button.setIcon(up_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowUp))
        up_batchlocation_button.setToolTip(self.tr("Move up in list"))
        up_batchlocation_button.setStatusTip(self.tr("Move up in list"))
        
        down_batchlocation_button = QtGui.QPushButton()
        self.connect(down_batchlocation_button, QtCore.SIGNAL('clicked()'), self.down_batchlocation)
        down_batchlocation_button.setIcon(down_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
        down_batchlocation_button.setToolTip(self.tr("Move down in list"))
        down_batchlocation_button.setStatusTip(self.tr("Move down in list"))

        exec_batchlocations_button = QtGui.QPushButton()
        self.connect(exec_batchlocations_button, QtCore.SIGNAL('clicked()'), self.exec_batchlocations)
        exec_batchlocations_button.setIcon(exec_batchlocations_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        exec_batchlocations_button.setToolTip(self.tr("Apply changes"))
        exec_batchlocations_button.setStatusTip(self.tr("Apply changes"))

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(add_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(del_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(edit_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(up_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(down_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(exec_batchlocations_button, QtGui.QDialogButtonBox.ActionRole)

        vbox0 = QtGui.QVBoxLayout()
        vbox0.addWidget(vbox0_label)
        vbox0.addWidget(batchlocations_view)
        vbox0.addWidget(buttonbox0)       
        
        ##### Location groups #####        
        vbox1_label = QtGui.QLabel(self.tr("Location groups:"))
        
        location_groups_view = QtGui.QListView()
        location_groups_view.setModel(self.locationgroups_model)
        location_groups_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        location_groups_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)             

        add_locationgroup_button = QtGui.QPushButton()
        self.connect(add_locationgroup_button, QtCore.SIGNAL('clicked()'), self.add_locationgroup)
        add_locationgroup_button.setIcon(add_locationgroup_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        add_locationgroup_button.setToolTip(self.tr("Add location group"))
        add_locationgroup_button.setStatusTip(self.tr("Add location group"))
        
        del_locationgroup_button = QtGui.QPushButton()
        self.connect(del_locationgroup_button, QtCore.SIGNAL('clicked()'), self.del_locationgroup)
        del_locationgroup_button.setIcon(del_locationgroup_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        del_locationgroup_button.setToolTip(self.tr("Remove location group"))
        del_locationgroup_button.setStatusTip(self.tr("Remove location group"))

        exec_locationgroups_button = QtGui.QPushButton()
        self.connect(exec_locationgroups_button, QtCore.SIGNAL('clicked()'), self.exec_locationgroups)
        exec_locationgroups_button.setIcon(exec_locationgroups_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        exec_locationgroups_button.setToolTip(self.tr("Apply changes"))
        exec_locationgroups_button.setStatusTip(self.tr("Apply changes"))

        buttonbox1 = QtGui.QDialogButtonBox()
        buttonbox1.addButton(add_locationgroup_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(del_locationgroup_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(exec_locationgroups_button, QtGui.QDialogButtonBox.ActionRole)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(vbox1_label)
        vbox1.addWidget(location_groups_view)
        vbox1.addWidget(buttonbox1)

        ##### Batch connections #####        
        vbox2_label = QtGui.QLabel(self.tr("Batch connections:"))
        
        batchconnections_view = QtGui.QListView()
        batchconnections_view.setModel(self.batchconnections_model)
        batchconnections_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        batchconnections_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)             

        edit_batchconnection_button = QtGui.QPushButton()
        self.connect(edit_batchconnection_button, QtCore.SIGNAL('clicked()'), self.edit_batchconnection)
        edit_batchconnection_button.setIcon(edit_batchconnection_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        edit_batchconnection_button.setToolTip(self.tr("Edit settings"))
        edit_batchconnection_button.setStatusTip(self.tr("Edit settings"))

        exec_batchconnections_button = QtGui.QPushButton()
        self.connect(exec_batchconnections_button, QtCore.SIGNAL('clicked()'), self.exec_batchconnections)
        exec_batchconnections_button.setIcon(exec_batchconnections_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        exec_batchconnections_button.setToolTip(self.tr("Apply changes"))
        exec_batchconnections_button.setStatusTip(self.tr("Apply changes"))

        buttonbox2 = QtGui.QDialogButtonBox()
        buttonbox2.addButton(edit_batchconnection_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox2.addButton(exec_batchconnections_button, QtGui.QDialogButtonBox.ActionRole)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(vbox2_label)
        vbox2.addWidget(batchconnections_view)
        vbox2.addWidget(buttonbox2)

        ##### Operators #####        
        vbox3_label = QtGui.QLabel(self.tr("Operators:"))
        
        operators_view = QtGui.QListView()
        operators_view.setModel(self.operators_model)
        operators_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        operators_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)             

        add_operator_button = QtGui.QPushButton()
        self.connect(add_operator_button, QtCore.SIGNAL('clicked()'), self.add_operator)
        add_operator_button.setIcon(add_operator_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        add_operator_button.setToolTip(self.tr("Add operator"))
        add_operator_button.setStatusTip(self.tr("Add operator"))
        
        del_operator_button = QtGui.QPushButton()
        self.connect(del_operator_button, QtCore.SIGNAL('clicked()'), self.del_operator)
        del_operator_button.setIcon(del_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        del_operator_button.setToolTip(self.tr("Remove operator"))
        del_operator_button.setStatusTip(self.tr("Remove operator"))

        edit_operator_button = QtGui.QPushButton()
        self.connect(edit_operator_button, QtCore.SIGNAL('clicked()'), self.edit_operator)
        edit_operator_button.setIcon(edit_operator_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        edit_operator_button.setToolTip(self.tr("Edit settings"))
        edit_operator_button.setStatusTip(self.tr("Edit settings"))

        buttonbox3 = QtGui.QDialogButtonBox()
        buttonbox3.addButton(add_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox3.addButton(del_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox3.addButton(edit_operator_button, QtGui.QDialogButtonBox.ActionRole)

        vbox3 = QtGui.QVBoxLayout()
        vbox3.addWidget(vbox3_label)
        vbox3.addWidget(operators_view)
        vbox3.addWidget(buttonbox3)
        
        ##### Main layout ##### 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)
        top_hbox.addLayout(vbox2)
        top_hbox.addLayout(vbox3)
  
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(top_hbox)           
                                       
        self.main_frame.setLayout(vbox)

        self.setCentralWidget(self.main_frame)

        self.status_text = QtGui.QLabel("")        
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Ready"))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))

        tip = self.tr("Open file")        
        load_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton),self.tr("&Open..."), self)
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)
        load_action.setShortcut('Ctrl+O')

        tip = self.tr("Save file")        
        save_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton),self.tr("&Save"), self)
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)
        save_action.setShortcut('Ctrl+S')

        tip = self.tr("Save current file as...")        
        saveas_action = QtGui.QAction(self.tr("Save as..."), self)
        saveas_action.setToolTip(tip)
        saveas_action.setStatusTip(tip)        

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_ArrowBack),self.tr("&Quit"), self)
        self.connect(quit_action, QtCore.SIGNAL("triggered()"), self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)        
        self.file_menu.addAction(quit_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_FileDialogInfoView),self.tr("About..."), self)
        self.connect(about_action, QtCore.SIGNAL("triggered()"), self.on_about)
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(about_action)