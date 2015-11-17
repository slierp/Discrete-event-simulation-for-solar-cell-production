# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore, QtGui
import os, ntpath
from dialogs.AddBatchlocationView import AddBatchlocationView
from dialogs.DelBatchlocationView import DelBatchlocationView
from dialogs.EditBatchlocationView import EditBatchlocationView
from dialogs.AddOperatorView import AddOperatorView
from dialogs.DelOperatorView import DelOperatorView
from dialogs.EditOperatorView import EditOperatorView
from dialogs.LineDiagramView import LineDiagramView
from dialogs.HelpDialog import HelpDialog
from RunSimulationThread import RunSimulationThread
from MainPlot import MultiPlot
import pickle
from copy import deepcopy

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
        self.setWindowIcon(QtGui.QIcon(":DescPro_icon.png"))

        ### Set initial geometry and center the window on the screen ###
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
        ### Set default font size ###
        self.setStyleSheet('font-size: 12pt;')        
        
        self.edit = QtGui.QTextBrowser()
        self.edit.verticalScrollBar().setValue(self.edit.verticalScrollBar().maximum())
        
        self.table_widget = QtGui.QTableWidget()        
        self.clip = QtGui.QApplication.clipboard()
        
        self.qt_thread = QtCore.QThread(self) # Separate Qt thread
        self.simulation_thread = RunSimulationThread(self) # Where all the simulation work will be done
        self.simulation_thread.moveToThread(self.qt_thread) # Move simulation work to separate thread
        self.qt_thread.started.connect(self.simulation_thread.run) # Start simulation when thread is started
        self.simulation_thread.signal.sig.connect(self.simulation_end_signal) # Get signal to show message when simulation is finished
        self.simulation_thread.signal.sig.connect(self.qt_thread.quit) # Stop thread when simulation is finished
        self.simulation_thread.output.sig.connect(self.simulation_output) # Get signal to show simulation progress
        self.simulation_thread.util.sig.connect(self.utilization_output) # Get signal to show utilization results
        self.output_signal_counter = 0        
        self.output_overload_signal_given = False
        
        self.wid = None # will contain window for displaying production rates
        self.profiling_mode = False
        self.plot_selection = [] # selected items for display

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
        
        try:
            with open(str(filename)) as f:
                self.batchlocations,self.locationgroups,self.batchconnections,self.operators = pickle.load(f)
        except:
            msg = self.tr("Could not read file \"" + filename + "\"")
            QtGui.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
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
        self.batchlocations_model.setHorizontalHeaderLabels(['Tools'])           

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

    def line_diagram_view(self):
        LineDiagramView(self)

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
        msgBox.setText(self.tr("This will remove all tools. Continue?"))
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtGui.QMessageBox.Ok):
            self.batchlocations = []
            self.locationgroups = []
            self.batchconnections = []
            self.batchlocations_model.clear()
            self.batchlocations_model.setHorizontalHeaderLabels(['Tools']) 
            self.statusBar().showMessage(self.tr("All tools were removed"))

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

        transport_time = 60 # default duration for transport action
        time_per_unit = 10 # default additional duration for each unit
        min_units = 1 # default minimum number of units for transport
                           
        #num = 0
        for i in range(len(self.locationgroups)-1):
            for j, value in enumerate(self.locationgroups[i]):
                for k, value in enumerate(self.locationgroups[i+1]):
                    self.batchconnections.append([[i,j],[i+1,k],transport_time, time_per_unit,min_units])                           

    def import_batchlocations(self):
        self.exec_locationgroups() # reload connections again just to be sure
        self.load_definition_operators() # default operators list
        self.statusBar().showMessage(self.tr("Tools imported"))

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
        for i in range(len(self.locationgroups)-1):
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
        self.plot_selection = [] # reset selection in case definition changed

        if (len(self.batchlocations) < 2) | (len(self.locationgroups) < 2):
            self.statusBar().showMessage(self.tr("Not enough batch locations found"))
            return
        
        for i, value in enumerate(self.batchconnections):
            # check if all batchconnections exist inside locationgroups
            # no separate check whether all batchlocations inside locationgroups exist
            # since GUI should not allow for any errors to appear
            if (self.batchconnections[i][0][0] > (len(self.locationgroups)-1)) | \
                    (self.batchconnections[i][1][0] > (len(self.locationgroups)-1)):
                self.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"))
                return
            elif (self.batchconnections[i][0][1] > (len(self.locationgroups[self.batchconnections[i][0][0]])-1)) | \
                    (self.batchconnections[i][1][1] > (len(self.locationgroups[self.batchconnections[i][1][0]])-1)):
                self.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"))
                return

        for i, value in enumerate(self.operators):
            # check if all batchconnection numbers inside self.operators exist inside self.batchconnections
            for j in self.operators[i][0]:
                if (j > len(self.batchconnections)):
                    self.statusBar().showMessage(self.tr("Invalid batch connection found inside operator definitions"))
                    return
        
        time_limits = [60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]
        for i, value in enumerate(self.sim_time_selection_list):
            if (value == self.sim_time_combo.currentText()):
                self.params['time_limit'] = time_limits[i]
                
        if not self.qt_thread.isRunning():
        
            # clear log tab
            self.edit.clear()
            
            # send production line definition to simulation thread using deep copy
            self.simulation_thread.batchlocations = deepcopy(self.batchlocations)
            self.simulation_thread.locationgroups = deepcopy(self.locationgroups)
            self.simulation_thread.batchconnections = deepcopy(self.batchconnections)
            self.simulation_thread.operators = deepcopy(self.operators)

            self.simulation_thread.params = {}
            self.simulation_thread.params.update(self.params)
            
            self.simulation_thread.stop_simulation = False
            self.run_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)

            # clear idle tab and reset headers
            self.table_widget.clear()
        
            headerlabels = ['Tool type','Name','Nominal','Utilization']
            for i in range(4,35):
                headerlabels.append("Process " + str(i-4))
            self.table_widget.setHorizontalHeaderLabels(headerlabels)
            self.table_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
            self.table_widget.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

            self.qt_thread.start() # Start separate thread and automatically start simulation also
            self.statusBar().showMessage(self.tr("Simulation started")) 


    def stop_simulation(self):
        self.simulation_thread.stop_simulation = True # sending signal does not work since simulationthread run function will not be interrupted
        self.statusBar().showMessage(self.tr("Simulation stop signal was sent"))

    def switch_profiling_mode(self):
        
        if (self.profiling_mode):
            self.profiling_mode = False
            self.qt_thread.started.disconnect(self.simulation_thread.run_with_profiling) # Start simulation when thread is started
            self.qt_thread.started.connect(self.simulation_thread.run) # Start simulation when thread is started
            self.statusBar().showMessage(self.tr("Profiling mode has been turned off"))
        else:
            self.profiling_mode = True
            self.qt_thread.started.disconnect(self.simulation_thread.run) # Start simulation when thread is started
            self.qt_thread.started.connect(self.simulation_thread.run_with_profiling) # Start simulation when thread is started
            self.statusBar().showMessage(self.tr("Profiling mode has been turned on"))

    def plot_production_rates(self):
        
        if len(self.simulation_thread.prod_rates_df):
             self.statusBar().showMessage(self.tr("Creating plot window..."))
        else:
            self.statusBar().showMessage(self.tr("Please run a simulation first"))
            return     
        
        #if (self.wid):
        #    if (self.wid.isWindow()):
        #        # close previous instances of child windows to save system memory                
        #        self.wid.close()                

        self.wid = MultiPlot(self)
                        
        self.wid.show() 
        
        self.statusBar().showMessage(self.tr("Ready"))

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
            #self.edit.insertPlainText(string + '\n')
            self.edit.insertHtml(QtCore.QString(string + '<br>'))
            self.output_signal_counter += 1
        elif not self.output_overload_signal_given:
            self.edit.moveCursor(QtGui.QTextCursor.End) # make sure user cannot re-arrange the output
            self.edit.insertPlainText('Output overload\n') 
            self.output_overload_signal_given = True

    @QtCore.pyqtSlot(list)
    def utilization_output(self,utilization):
      
        self.table_widget.setRowCount(len(utilization))
        
        max_length = 0
        for i in range(len(utilization)):
            if len(utilization[i]) > max_length:
                max_length = len(utilization[i])
                
        self.table_widget.setColumnCount(max_length)
        self.table_widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)        

        headerlabels = ['Tool type','Name','Nominal','Utilization']
        for i in range(4,15):
            headerlabels.append("Process " + str(i-4))
        self.table_widget.setHorizontalHeaderLabels(headerlabels)
        self.table_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        for i, value in enumerate(utilization):
            item0 = QtGui.QTableWidgetItem(utilization[i][0]) # Tool type
            item1 = QtGui.QTableWidgetItem(utilization[i][1]) # Tool name
            item2 = QtGui.QTableWidgetItem(str(int(utilization[i][2]))) # Nominal throughput
            item3 = QtGui.QTableWidgetItem(str(int(utilization[i][3])) + "%") # Overall utilization
            self.table_widget.setItem(i, 0, item0)
            self.table_widget.setItem(i, 1, item1)
            self.table_widget.setItem(i, 2, item2)
            self.table_widget.setItem(i, 3, item3)            
            
            for j in range(4,len(utilization[i])):
                item = QtGui.QTableWidgetItem(str(utilization[i][j][0]) + ": " + str(utilization[i][j][1]) + "%")
                self.table_widget.setItem(i, j, item)

    @QtCore.pyqtSlot(str)
    def simulation_end_signal(self):
        self.run_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)
        self.statusBar().showMessage(self.tr("Simulation has ended"))

    def open_help_dialog(self):
        help_dialog = HelpDialog(self)
        help_dialog.setModal(True)
        help_dialog.show() 

    def on_about(self):
        msg = self.tr("Solar cell production simulation\nAuthor: Ronald Naber\nContact: rnaber (AT) tempress.nl\nLicense: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()        

        ##### Batch locations #####        
        self.batchlocations_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.batchlocations_view.setExpandsOnDoubleClick(False)
        self.batchlocations_model.setHorizontalHeaderLabels(['Tools'])
        self.batchlocations_view.setModel(self.batchlocations_model)
        self.batchlocations_view.setUniformRowHeights(True)
        self.batchlocations_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.batchlocations_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        line_diagram_button = QtGui.QPushButton()
        line_diagram_button.clicked.connect(self.line_diagram_view)
        line_diagram_button.setIcon(QtGui.QIcon(":eye.png"))
        line_diagram_button.setToolTip(self.tr("View production line"))
        line_diagram_button.setStatusTip(self.tr("View production line"))
        
        add_batchlocation_button = QtGui.QPushButton()
        add_batchlocation_button.clicked.connect(self.add_batchlocation_view)
        add_batchlocation_button.setIcon(QtGui.QIcon(":plus.png"))
        add_batchlocation_button.setToolTip(self.tr("Add"))
        add_batchlocation_button.setStatusTip(self.tr("Add"))
        
        del_batchlocation_button = QtGui.QPushButton()
        del_batchlocation_button.clicked.connect(self.del_batchlocation_view)
        del_batchlocation_button.setIcon(QtGui.QIcon(":minus.png"))
        del_batchlocation_button.setToolTip(self.tr("Remove"))
        del_batchlocation_button.setStatusTip(self.tr("Remove"))
        
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
        buttonbox0.addButton(line_diagram_button, QtGui.QDialogButtonBox.ActionRole)
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
        import_batchlocations_button.setToolTip(self.tr("Import tools"))
        import_batchlocations_button.setStatusTip(self.tr("Import tools"))

        add_operator_button = QtGui.QPushButton()
        add_operator_button.clicked.connect(self.add_operator_view)           
        add_operator_button.setIcon(QtGui.QIcon(":plus.png"))
        add_operator_button.setToolTip(self.tr("Add"))
        add_operator_button.setStatusTip(self.tr("Add"))
        
        del_operator_button = QtGui.QPushButton()
        del_operator_button.clicked.connect(self.del_operator_view)          
        del_operator_button.setIcon(QtGui.QIcon(":minus.png"))
        del_operator_button.setToolTip(self.tr("Remove"))
        del_operator_button.setStatusTip(self.tr("Remove"))

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

        self.plot_production_rates_button = QtGui.QPushButton()
        self.plot_production_rates_button.clicked.connect(self.plot_production_rates)
        self.plot_production_rates_button.setIcon(QtGui.QIcon(":chart.png"))
        self.plot_production_rates_button.setToolTip(self.tr("Plot production rate results"))
        self.plot_production_rates_button.setStatusTip(self.tr("Plot production rate results"))

        self.switch_profiling_mode_button = QtGui.QCheckBox()
        self.switch_profiling_mode_button.clicked.connect(self.switch_profiling_mode)
        self.switch_profiling_mode_button.setChecked(False)
        self.switch_profiling_mode_button.setToolTip(self.tr("Turn profiling mode on or off"))
        self.switch_profiling_mode_button.setStatusTip(self.tr("Turn profiling mode on or off"))

        top_buttonbox = QtGui.QDialogButtonBox()
        top_buttonbox.addButton(open_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(save_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.run_sim_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.stop_sim_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.plot_production_rates_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.switch_profiling_mode_button, QtGui.QDialogButtonBox.ActionRole)

        self.sim_time_combo = QtGui.QComboBox(self)
        for i in self.sim_time_selection_list:
            self.sim_time_combo.addItem(i)
        
        toolbar_hbox = QtGui.QHBoxLayout()
        toolbar_hbox.addWidget(top_buttonbox)
        toolbar_hbox.addWidget(self.sim_time_combo)        
        
        bottom_tabwidget = QtGui.QTabWidget()
        bottom_tabwidget.addTab(self.edit, QtCore.QString("Activity"))
                
        bottom_tabwidget.addTab(self.table_widget, QtCore.QString("Utilization"))
        
        ##### Main layout #####
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.setDirection(QtGui.QBoxLayout.LeftToRight)
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)

        vbox = QtGui.QVBoxLayout()       
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox)
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

        tip = self.tr("Help information")        
        help_action = QtGui.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self.open_help_dialog)         
        help_action.setToolTip(tip)
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)         
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(help_action)
        self.help_menu.addAction(about_action)
