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
#        self.setWindowIcon(QtGui.QIcon(icon_name))
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
        
        self.create_menu()
        self.create_main_frame()
        self.load_default_line()

    def load_default_line(self):
        for i in self.batchlocations:
            item = QtGui.QStandardItem(str(i) + ". " + self.batchlocations[i][0])
            self.batchlocations_model.appendRow(item)                        
            
        self.exec_batchlocations()

    def add_batchlocation(self):
        pass

    def del_batchlocation(self):
        pass

    def exec_batchlocations(self):
        # first read batchlocations_model and then generate a locationgroups_model
        # read step not yet implemented

        self.locationgroups = {}
        num = 0
        for i in self.batchlocations:
            
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
            number_list = ""
            for j in self.locationgroups[i]:
                number_list += str(j) + ", "
            
            item = QtGui.QStandardItem(number_list)
            self.locationgroups_model.appendRow(item)

    def exec_locationgroups(self):
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
        
        self.add_batchlocation_button = QtGui.QPushButton(self.tr("Add"))
        self.connect(self.add_batchlocation_button, QtCore.SIGNAL('clicked()'), self.add_batchlocation)
        
        self.del_batchlocation_button = QtGui.QPushButton(self.tr("Delete"))
        self.connect(self.del_batchlocation_button, QtCore.SIGNAL('clicked()'), self.del_batchlocation)       

        self.exec_batchlocations_button = QtGui.QPushButton(self.tr("Execute"))
        self.connect(self.exec_batchlocations_button, QtCore.SIGNAL('clicked()'), self.exec_batchlocations) 

        vbox0 = QtGui.QVBoxLayout()
        vbox0.addWidget(vbox0_label)
        vbox0.addWidget(self.batchlocations_view)
        vbox0.addWidget(self.add_batchlocation_button) 
        vbox0.addWidget(self.del_batchlocation_button)
        vbox0.addWidget(self.exec_batchlocations_button)

        ##### Location groups #####        
        vbox1_label = QtGui.QLabel(self.tr("Location groups:"))
        
        self.location_groups_view = QtGui.QListView()
        self.location_groups_view.setModel(self.locationgroups_model)             

        self.exec_locationgroups_button = QtGui.QPushButton(self.tr("Execute"))
        self.connect(self.exec_locationgroups_button, QtCore.SIGNAL('clicked()'), self.exec_locationgroups)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(vbox1_label)
        vbox1.addWidget(self.location_groups_view)
        vbox1.addWidget(self.exec_locationgroups_button)

        ##### Batch connections #####        
        vbox2_label = QtGui.QLabel(self.tr("Batch connections:"))
        
        self.batchconnections_view = QtGui.QListView()
        self.batchconnections_view.setModel(self.batchconnections_model)             

        self.exec_batchconnections_button = QtGui.QPushButton(self.tr("Execute"))
        self.connect(self.exec_batchconnections_button, QtCore.SIGNAL('clicked()'), self.exec_batchconnections)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(vbox2_label)
        vbox2.addWidget(self.batchconnections_view)
        vbox2.addWidget(self.exec_batchconnections_button)
        
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