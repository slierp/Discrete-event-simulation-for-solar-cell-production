# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:19:49 2014

@author: rnaber
"""

from __future__ import division
#import numpy as np
#import pandas as pd
#import os, ntpath, sys
from PyQt4 import QtCore, QtGui
#from IVMainPlot import *
#import Required_resources
#icon_name = ":Logo_Tempress.ico"      

class MainGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell manufacturing simulation"))
#       self.setWindowIcon(QtGui.QIcon(icon_name))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # DISABLE BEFORE RELEASE

        self.clip = QtGui.QApplication.clipboard()
        self.batchlocations_model = QtGui.QStandardItemModel()
        self.locationgroups_model = QtGui.QStandardItemModel()
        self.batchconnections_model = QtGui.QStandardItemModel()             

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
        # first read batchlocations_model and then generate a locationgroups_model
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
        # first read locationgroups_model and then generate a batchconnections_model
        # read step not yet implemented        
        self.batchconnections = {}

        transport_time = 90
        time_per_unit = 20
        
        ### work in progress                    
        num = 0
        for i, value in enumerate(self.locationgroups):
            for j, value in enumerate(self.locationgroups[i]):
                if len(self.locationgroups) < (i+1):
                    for k, value in enumerate(self.locationgroups[i+1]):
                        self.batchconnections[num] = [[j,k],[j+1,k],transport_time, time_per_unit]
                        print str(num) + " " + str(i) + " " + str(j)  + " " +  str(k)
                        num  += 1
                
        print self.batchconnections        
        """
        self.batchconnections_model.clear()

        for i in self.locationgroups:
            number_list = ""
            for j, value in enumerate(self.locationgroups[i]):
                if (j == 0):
                    number_list += str(i) + ".\t" + str(value)
                else:
                    number_list += ", " + str(value)
            
            item = QtGui.QStandardItem(number_list)
            self.locationgroups_model.appendRow(item)
        """

    def edit_batchconnection(self):
        pass

    def exec_batchconnections(self):
        pass

    def on_about(self):
        msg = self.tr("Solar cell manufacturing simulation\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()        

        ##### Batch locations #####        
        vbox0_label = QtGui.QLabel(self.tr("Batch locations:"))
        
        self.batchlocations_view = QtGui.QListView()
        self.batchlocations_view.setModel(self.batchlocations_model)
        self.batchlocations_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.batchlocations_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)      
        
        self.add_batchlocation_button = QtGui.QPushButton()
        self.connect(self.add_batchlocation_button, QtCore.SIGNAL('clicked()'), self.add_batchlocation)
        self.add_batchlocation_button.setIcon(self.add_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        self.add_batchlocation_button.setToolTip(self.tr("Add batchlocation"))
        
        self.del_batchlocation_button = QtGui.QPushButton()
        self.connect(self.del_batchlocation_button, QtCore.SIGNAL('clicked()'), self.del_batchlocation)
        self.del_batchlocation_button.setIcon(self.del_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        self.del_batchlocation_button.setToolTip(self.tr("Delete batchlocation"))

        self.edit_batchlocation_button = QtGui.QPushButton()
        self.connect(self.edit_batchlocation_button, QtCore.SIGNAL('clicked()'), self.edit_batchlocation)
        self.edit_batchlocation_button.setIcon(self.edit_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        self.edit_batchlocation_button.setToolTip(self.tr("Edit settings"))

        self.up_batchlocation_button = QtGui.QPushButton()
        self.connect(self.up_batchlocation_button, QtCore.SIGNAL('clicked()'), self.up_batchlocation)
        self.up_batchlocation_button.setIcon(self.up_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowUp))
        self.up_batchlocation_button.setToolTip(self.tr("Move up in list"))
        
        self.down_batchlocation_button = QtGui.QPushButton()
        self.connect(self.del_batchlocation_button, QtCore.SIGNAL('clicked()'), self.down_batchlocation)
        self.down_batchlocation_button.setIcon(self.down_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
        self.down_batchlocation_button.setToolTip(self.tr("Move down in list"))

        self.exec_batchlocations_button = QtGui.QPushButton()
        self.connect(self.exec_batchlocations_button, QtCore.SIGNAL('clicked()'), self.exec_batchlocations)
        self.exec_batchlocations_button.setIcon(self.exec_batchlocations_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        self.exec_batchlocations_button.setToolTip(self.tr("Apply changes"))

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(self.add_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(self.del_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(self.edit_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(self.up_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(self.down_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(self.exec_batchlocations_button, QtGui.QDialogButtonBox.ActionRole)

        vbox0 = QtGui.QVBoxLayout()
        vbox0.addWidget(vbox0_label)
        vbox0.addWidget(self.batchlocations_view)
        vbox0.addWidget(buttonbox0)       
        
        ##### Location groups #####        
        vbox1_label = QtGui.QLabel(self.tr("Location groups:"))
        
        self.location_groups_view = QtGui.QListView()
        self.location_groups_view.setModel(self.locationgroups_model)             

        self.add_locationgroup_button = QtGui.QPushButton()
        self.connect(self.add_locationgroup_button, QtCore.SIGNAL('clicked()'), self.add_locationgroup)
        self.add_locationgroup_button.setIcon(self.add_locationgroup_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        self.add_locationgroup_button.setToolTip(self.tr("Add location group"))
        
        self.del_locationgroup_button = QtGui.QPushButton()
        self.connect(self.del_locationgroup_button, QtCore.SIGNAL('clicked()'), self.del_locationgroup)
        self.del_locationgroup_button.setIcon(self.del_locationgroup_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        self.del_locationgroup_button.setToolTip(self.tr("Delete location group"))

        self.exec_locationgroups_button = QtGui.QPushButton()
        self.connect(self.exec_locationgroups_button, QtCore.SIGNAL('clicked()'), self.exec_locationgroups)
        self.exec_locationgroups_button.setIcon(self.exec_locationgroups_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        self.exec_locationgroups_button.setToolTip(self.tr("Apply changes"))

        buttonbox1 = QtGui.QDialogButtonBox()
        buttonbox1.addButton(self.add_locationgroup_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(self.del_locationgroup_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(self.exec_locationgroups_button, QtGui.QDialogButtonBox.ActionRole)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(vbox1_label)
        vbox1.addWidget(self.location_groups_view)
        vbox1.addWidget(buttonbox1)

        ##### Batch connections #####        
        vbox2_label = QtGui.QLabel(self.tr("Batch connections:"))
        
        self.batchconnections_view = QtGui.QListView()
        self.batchconnections_view.setModel(self.batchconnections_model)             

        self.edit_batchconnection_button = QtGui.QPushButton()
        self.connect(self.edit_batchconnection_button, QtCore.SIGNAL('clicked()'), self.edit_batchconnection)
        self.edit_batchconnection_button.setIcon(self.edit_batchconnection_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        self.edit_batchconnection_button.setToolTip(self.tr("Edit settings"))

        self.exec_batchconnections_button = QtGui.QPushButton()
        self.connect(self.exec_batchconnections_button, QtCore.SIGNAL('clicked()'), self.exec_batchconnections)
        self.exec_batchconnections_button.setIcon(self.exec_batchconnections_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        self.exec_batchconnections_button.setToolTip(self.tr("Apply changes"))        

        buttonbox2 = QtGui.QDialogButtonBox()
        buttonbox2.addButton(self.edit_batchconnection_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox2.addButton(self.exec_batchconnections_button, QtGui.QDialogButtonBox.ActionRole)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(vbox2_label)
        vbox2.addWidget(self.batchconnections_view)
        vbox2.addWidget(buttonbox2)
        
        ##### Main layout ##### 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)
        top_hbox.addLayout(vbox2)
  
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(top_hbox)           
                                       
        self.main_frame.setLayout(vbox)

        self.setCentralWidget(self.main_frame)

        self.status_text = QtGui.QLabel("")        
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Testing..."))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))
        
        quit_action = self.create_action(self.tr("Quit"), slot=self.close, 
            shortcut="Ctrl+Q", tip=self.tr("Close the application"))
        
        self.add_actions(self.file_menu, (quit_action,))
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))
        about_action = self.create_action(self.tr("About"), 
            shortcut='F1', slot=self.on_about, 
            tip=self.tr("About the application"))
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action