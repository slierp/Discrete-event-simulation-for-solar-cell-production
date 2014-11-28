# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:19:49 2014

@author: rnaber
"""

from __future__ import division
import numpy as np
from PyQt4 import QtCore, QtGui
import os, ntpath
from dialogs.AddBatchlocationView import AddBatchlocationView
from dialogs.DelBatchlocationView import DelBatchlocationView
from dialogs.EditBatchlocationView import EditBatchlocationView
from dialogs.AddOperatorView import AddOperatorView
from dialogs.DelOperatorView import DelOperatorView
from dialogs.EditOperatorView import EditOperatorView
from RunSimulation import RunSimulation
from RunSimulationThread import RunSimulationThread
import pickle

class DeselectableTreeView(QtGui.QTreeView):
    # de-select by right click or by clicking on white space
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.clearSelection()
        else:
            self.clearSelection()            
            QtGui.QTreeView.mousePressEvent(self, event)    

class MainGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell production simulation"))
        self.setWindowIcon(QtGui.QIcon(":Logo_Tempress.png"))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # DISABLE BEFORE RELEASE
        
        self.edit = QtGui.QTextBrowser()
        self.edit.verticalScrollBar().setValue(self.edit.verticalScrollBar().maximum())
        
        self.table_widget = QtGui.QTableWidget()        
        self.clip = QtGui.QApplication.clipboard()

        self.simulation_thread = RunSimulationThread(self,self.edit)
        self.simulation_thread.signal.sig.connect(self.simulation_end_signal)
        self.simulation_thread.output.sig.connect(self.simulation_output)
        self.simulation_thread.util.sig.connect(self.utilization_output)
        self.output_signal_counter = 0        
        self.output_overload_signal_given = False        

        self.prev_dir_path = ""
        self.prev_save_path = ""

        self.batchlocations_model = QtGui.QStandardItemModel()
        self.batchlocations_view = DeselectableTreeView()
        self.batchlocations_view.doubleClicked.connect(self.edit_batchlocation_view)
        self.batchlocations_view.setAlternatingRowColors(True)
        self.operators_model = QtGui.QStandardItemModel()
        self.operators_view = DeselectableTreeView()
        self.operators_view.doubleClicked.connect(self.edit_operator_view)
        self.operators_view.setAlternatingRowColors(True)
        self.batchlocation_dialog = None

        self.batchlocations = [] #tool class name, no of tools, dict with settings
        self.batchlocations.append(["WaferSource", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker",{'name' : '1'}])
        self.batchlocations.append(["BatchTex", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '1'}])
        self.batchlocations.append(["Buffer", {'name' : '0'}])
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
            self.exec_locationgroups()
            
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
        AddBatchlocationView(self)

    def del_batchlocation_view(self):        
        DelBatchlocationView(self)
    
    def edit_batchlocation_view(self):
        EditBatchlocationView(self)

    def trash_batchlocation_view(self):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtGui.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all batch locations. Continue?"))
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtGui.QMessageBox.Ok):
            self.batchlocations = []
            self.locationgroups = []
            self.batchconnections = []
            self.batchlocations_model.clear()
            self.batchlocations_model.setHorizontalHeaderLabels(['Batch locations']) 
            self.statusBar().showMessage(self.tr("All batch locations were removed"))

    def print_batchlocation(self, num):
        if (num >= len(self.batchlocations)):
            return "Error"
            
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
        if (num >= len(self.batchconnections)):
            return "Error"
            
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
        
    def add_operator_view(self):
        AddOperatorView(self)    

    def del_operator_view(self):
        DelOperatorView(self)

    def edit_operator_view(self):
        EditOperatorView(self)

    def trash_operator_view(self):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtGui.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all operators. Continue?"))
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtGui.QMessageBox.Ok):
            self.operators = []
            self.operators_model.clear()
            self.operators_model.setHorizontalHeaderLabels(['Operators']) 
            self.statusBar().showMessage(self.tr("All operators were removed"))

    def run_simulation(self):
        self.output_signal_counter = 0
        RunSimulation(self)        

    def stop_simulation(self):
        self.simulation_thread.stop_simulation = True
        self.statusBar().showMessage(self.tr("Simulation stop signal was sent"))

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier): # Ctrl
            selected = self.table_widget.selectedRanges()                 
 
            if e.key() == QtCore.Qt.Key_C: # Copy
                s = ""
                for r in xrange(selected[0].topRow(),selected[0].bottomRow()+1):
                    for c in xrange(selected[0].leftColumn(),selected[0].rightColumn()+1):
                        try:
                            s += str(self.table_widget.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)

    @QtCore.pyqtSlot(str)
    def simulation_output(self,string):        
        
        if self.output_signal_counter < 1000:
            # limit text output to 999 lines to prevent GUI from becoming unresponsive
            self.edit.moveCursor(QtGui.QTextCursor.End) # make sure user cannot re-arrange the output
            self.edit.insertPlainText(string + '\n')
            self.output_signal_counter += 1
        elif not self.output_overload_signal_given:
            self.edit.moveCursor(QtGui.QTextCursor.End) # make sure user cannot re-arrange the output
            self.edit.insertPlainText('Output overload\n') 
            self.output_overload_signal_given = True
        #self.edit.insertHtml(QtCore.QString(string))

    @QtCore.pyqtSlot(list)
    def utilization_output(self,utilization):

        for i, value in enumerate(utilization):
            item0 = QtGui.QTableWidgetItem(utilization[i][0])
            item1 = QtGui.QTableWidgetItem(utilization[i][1])
            item2 = QtGui.QTableWidgetItem(str(int(utilization[i][2])))
            item3 = QtGui.QTableWidgetItem(str(int(utilization[i][3])) + "%")
            self.table_widget.setItem(i, 0, item0)
            self.table_widget.setItem(i, 1, item1)
            self.table_widget.setItem(i, 2, item2)
            self.table_widget.setItem(i, 3, item3)            
            
            for j in np.arange(4,len(utilization[i])):
                item = QtGui.QTableWidgetItem(str(utilization[i][j][0]) + "-" + str(utilization[i][j][1]) + "%")
                self.table_widget.setItem(i, j, item)
                
                if (utilization[i][j][1] < 10): color_code = QtGui.QColor(255,255,255)
                elif (utilization[i][j][1] < 25): color_code = QtGui.QColor(255,200,200)
                elif (utilization[i][j][1] < 50): color_code = QtGui.QColor(255,150,150)
                else: color_code = QtGui.QColor(255,100,100)
                    
                self.table_widget.item(i, j).setBackground(color_code)

    @QtCore.pyqtSlot(str)
    def simulation_end_signal(self):
        self.run_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)
        self.statusBar().showMessage(self.tr("Simulation has ended"))

    def on_about(self):
        msg = self.tr("Solar cell production simulation\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
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
        
        edit_batchlocation_button = QtGui.QPushButton()
        edit_batchlocation_button.clicked.connect(self.edit_batchlocation_view)        
        edit_batchlocation_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_batchlocation_button.setToolTip(self.tr("Edit settings"))
        edit_batchlocation_button.setStatusTip(self.tr("Edit settings"))        

        empty_batchlocation_view_button = QtGui.QPushButton()
        empty_batchlocation_view_button.clicked.connect(self.trash_batchlocation_view)        
        empty_batchlocation_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_batchlocation_view_button.setToolTip(self.tr("Remove all"))
        empty_batchlocation_view_button.setStatusTip(self.tr("Remove all")) 

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(add_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(del_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(edit_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)        
        buttonbox0.addButton(empty_batchlocation_view_button, QtGui.QDialogButtonBox.ActionRole)

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
        
        empty_operator_view_button = QtGui.QPushButton()
        empty_operator_view_button.clicked.connect(self.trash_operator_view)        
        empty_operator_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_operator_view_button.setToolTip(self.tr("Remove all"))
        empty_operator_view_button.setStatusTip(self.tr("Remove all"))        

        buttonbox1 = QtGui.QDialogButtonBox()
        buttonbox1.addButton(import_batchlocations_button, QtGui.QDialogButtonBox.ActionRole)       
        buttonbox1.addButton(add_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(del_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(edit_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(empty_operator_view_button, QtGui.QDialogButtonBox.ActionRole)

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
        
        bottom_tabwidget = QtGui.QTabWidget()
        bottom_tabwidget.addTab(self.edit, QtCore.QString("Activity log"))

        ##### Idle time tab #####       
        self.table_widget.setRowCount(64)
        self.table_widget.setColumnCount(35)
        self.table_widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)        

        headerlabels = ['Tool type','Name','Nominal','Util rate']
        for i in np.arange(4,35):
            headerlabels.append("Process " + str(i-4))
        self.table_widget.setHorizontalHeaderLabels(headerlabels)
        self.table_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
                
        bottom_tabwidget.addTab(self.table_widget, QtCore.QString("Utilization"))
        
        ##### Main layout #####
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.setDirection(QtGui.QBoxLayout.LeftToRight)
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)

        vbox = QtGui.QVBoxLayout()       
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox)
        #vbox.addLayout(textbox_hbox)
        vbox.addWidget(bottom_tabwidget)
                                                         
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