# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
import ntpath
from dialogs.HelpDialog import HelpDialog
from ToolsWidget import ToolsWidget
from CassetteloopsWidget import CassetteloopsWidget
from OperatorsWidget import OperatorsWidget
from TechniciansWidget import TechniciansWidget
from RunSimulationThread import RunSimulationThread
from MainPlot import MultiPlot
import pickle
from copy import deepcopy

class DeselectableTreeView(QtWidgets.QTreeView):
    # de-select by right click or by clicking on white space
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.clearSelection()
        else:
            self.clearSelection()            
            QtWidgets.QTreeView.mousePressEvent(self, event)    

class BatchlocationsViewKeyFilter(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    
    def eventFilter(self,  obj,  event):

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                self.signal.emit("del_batch_view")
                return True
            elif event.key() == QtCore.Qt.Key_A:
                self.signal.emit("add_batch_view")
                return True
        return False

class CassetteLoopsKeyFilter(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    
    def eventFilter(self,  obj,  event):

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                self.signal.emit("del_cassetteloop_view")
                return True
            elif event.key() == QtCore.Qt.Key_A:
                self.signal.emit("add_cassetteloop_view")
                return True
        return False

class OperatorsViewKeyFilter(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    
    def eventFilter(self,  obj,  event):

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                self.signal.emit("del_operator_view")
                return True
            elif event.key() == QtCore.Qt.Key_A:
                self.signal.emit("add_operator_view")
                return True
        return False

class TechniciansViewKeyFilter(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    
    def eventFilter(self,  obj,  event):

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                self.signal.emit("del_technician_view")
                return True
            elif event.key() == QtCore.Qt.Key_A:
                self.signal.emit("add_technician_view")
                return True
        return False

class MainGui(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell production simulation"))
        self.setWindowIcon(QtGui.QIcon(":DescPro_icon.png"))

        ### Set initial geometry and center the window on the screen ###
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
        ### Set default font size ###
        self.setStyleSheet('font-size: 12pt;')

        self.edit = QtWidgets.QTextBrowser()
        self.edit.verticalScrollBar().setValue(self.edit.verticalScrollBar().maximum())
        
        self.table_widget = QtWidgets.QTableWidget()        
        self.clip = QtWidgets.QApplication.clipboard()
        
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
        self.plot_selection = [] # selected items for display

        self.prev_dir_path = ""
        self.prev_save_path = ""

        # Batchlocations
        self.batchlocations_model = QtGui.QStandardItemModel()
        self.batchlocations_view = DeselectableTreeView()
        self.tools_widget = ToolsWidget(self)
        self.batchlocations_view.doubleClicked.connect(self.tools_widget.edit_batchlocation_view)
        self.batchlocations_view.setAlternatingRowColors(False)
        self.batch_filter = BatchlocationsViewKeyFilter()
        self.batchlocations_view.installEventFilter(self.batch_filter)
        self.batch_filter.signal.connect(self.treeview_signals)         

        # Cassette loops
        self.cassetteloops_model = QtGui.QStandardItemModel()
        self.cassetteloops_view = DeselectableTreeView()
        self.cassetteloops_widget = CassetteloopsWidget(self)
        self.cassetteloops_view.doubleClicked.connect(self.cassetteloops_widget.edit_cassetteloop_view)
        self.cassetteloops_view.setAlternatingRowColors(False)
        self.cassetteloops_filter = CassetteLoopsKeyFilter()
        self.cassetteloops_view.installEventFilter(self.cassetteloops_filter)
        self.cassetteloops_filter.signal.connect(self.treeview_signals)

        # Operators
        self.operators_model = QtGui.QStandardItemModel()
        self.operators_view = DeselectableTreeView()
        self.operators_widget = OperatorsWidget(self)
        self.operators_view.doubleClicked.connect(self.operators_widget.edit_operator_view)
        self.operators_view.setAlternatingRowColors(False)
        self.oper_filter = OperatorsViewKeyFilter()
        self.operators_view.installEventFilter(self.oper_filter)
        self.oper_filter.signal.connect(self.treeview_signals)

        # Technicians       
        self.technicians_model = QtGui.QStandardItemModel()
        self.technicians_view = DeselectableTreeView()
        self.technicians_widget = TechniciansWidget(self)
        self.technicians_view.doubleClicked.connect(self.technicians_widget.edit_technician_view)
        self.technicians_view.setAlternatingRowColors(False)
        self.tech_filter = TechniciansViewKeyFilter()
        self.technicians_view.installEventFilter(self.tech_filter)
        self.tech_filter.signal.connect(self.treeview_signals)

        self.sim_time_selection_list = ['1 hour','1 day','1 week','1 month','1 year']

        self.params = {}
        self.params['time_limit'] = 60*60
        self.params['profiling_mode'] = False
        
        self.create_menu()
        self.create_main_frame()
        self.tools_widget.load_definition()
        self.cassetteloops_widget.load_definition()
        self.operators_widget.load_definition()
        self.technicians_widget.load_definition()        

    @QtCore.pyqtSlot(str)
    def treeview_signals(self,signal):
        if signal == "del_batch_view":
            self.tools_widget.del_batchlocation_view()
        elif signal == "add_batch_view":
            self.tools_widget.add_batchlocation_view()
        elif signal == "add_operator_view":
            self.operators_widget.add_operator_view()
        elif signal == "del_operator_view":
            self.operators_widget.del_operator_view()          
        elif signal == "add_cassetteloop_view":
            self.cassetteloops_widget.add_cassetteloop_view()
        elif signal == "del_cassetteloop_view":
            self.cassetteloops_widget.del_cassetteloop_view()            
        elif signal == "add_technician_view":
            self.technicians_widget.add_technician_view()
        elif signal == "del_technician_view":
            self.technicians_widget.del_technician_view()
            
    def open_file(self):

        filename = QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open file"), self.prev_dir_path, "Description Files (*.desc)")
        filename = filename[0]

        if (not filename):
            return
        
        self.prev_save_path = filename
        self.prev_dir_path = ntpath.dirname(filename)
        
        try:
            with open(filename,'rb') as f:
                self.tools_widget.batchlocations,self.tools_widget.locationgroups,self.cassetteloops_widget.cassette_loops,\
                    self.tools_widget.batchconnections,self.operators_widget.operators,self.technicians_widget.technicians = pickle.load(f)
        except:
            msg = self.tr("Could not read file \"" + ntpath.basename(filename) + "\"")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg) 
            return
        
        self.tools_widget.load_definition(False)
        self.cassetteloops_widget.load_definition(False)
        self.operators_widget.load_definition(False)
        self.technicians_widget.load_definition(False)
            
        self.statusBar().showMessage(self.tr("New description loaded"),3000)

    def save_to_file(self):

        if (not self.prev_save_path):
            self.save_to_file_as()
            return
        
        with open(self.prev_save_path, 'wb') as f:
            pickle.dump([self.tools_widget.batchlocations,self.tools_widget.locationgroups,self.cassetteloops_widget.cassette_loops,\
                             self.tools_widget.batchconnections,self.operators_widget.operators,self.technicians_widget.technicians], f)
            
        self.statusBar().showMessage(self.tr("File saved"),3000)

    def save_to_file_as(self):

        filename = QtWidgets.QFileDialog.getSaveFileName(self,self.tr("Save file"), self.prev_dir_path, "Description Files (*.desc)")
        filename = filename[0]
        
        if (not filename):
            return
            
        # Check for non-ASCII here does not seem to work
        
        self.prev_save_path = filename
        self.prev_dir_path = ntpath.dirname(filename)
        
        with open(filename, 'wb') as f:        
            pickle.dump([self.tools_widget.batchlocations,self.tools_widget.locationgroups,self.cassetteloops_widget.cassette_loops,\
                             self.tools_widget.batchconnections,self.operators_widget.operators,self.technicians_widget.technicians], f)
            
        self.statusBar().showMessage(self.tr("File saved"),3000)

    def run_simulation(self):

        batchlocations = self.tools_widget.batchlocations
        locationgroups = self.tools_widget.locationgroups
        cassette_loops = self.cassetteloops_widget.cassette_loops
        batchconnections = self.tools_widget.batchconnections
        operators = self.operators_widget.operators
        technicians = self.technicians_widget.technicians
        
        self.output_signal_counter = 0

        if (len(batchlocations) < 2) | (len(locationgroups) < 2):
            self.statusBar().showMessage(self.tr("Not enough batch locations found"),3000)
            return

        # reset selection in case definition changed
        # only include last locationgroup in plot       
        self.plot_selection = locationgroups[len(locationgroups)-1] 
        
        for i, value in enumerate(batchconnections):
            # check if all batchconnections exist inside locationgroups
            # no separate check whether all batchlocations inside locationgroups exist
            # since GUI should not allow for any errors to appear
            if (batchconnections[i][0][0] > (len(locationgroups)-1)) | \
                    (batchconnections[i][1][0] > (len(locationgroups)-1)):
                self.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"),3000)
                return
            elif (batchconnections[i][0][1] > (len(locationgroups[batchconnections[i][0][0]])-1)) | \
                    (batchconnections[i][1][1] > (len(locationgroups[batchconnections[i][1][0]])-1)):
                self.statusBar().showMessage(self.tr("Invalid batch location found inside batch connection definitions"),3000)
                return

        for i, value in enumerate(operators):
            # check if all batchconnection numbers inside self.operators exist inside self.batchconnections
            for j in operators[i][0]:
                if (j > len(batchconnections)):
                    self.statusBar().showMessage(self.tr("Invalid batch connection found inside operator definitions"),3000)
                    return
        
        time_limits = [60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]
        for i, value in enumerate(self.sim_time_selection_list):
            if (value == self.sim_time_combo.currentText()):
                self.params['time_limit'] = time_limits[i]
     
        if not self.qt_thread.isRunning():
        
            # clear log tab
            self.edit.clear()
            
            # send production line definition to simulation thread using deep copy
            self.simulation_thread.batchlocations = deepcopy(batchlocations)
            self.simulation_thread.locationgroups = deepcopy(locationgroups)
            self.simulation_thread.batchconnections = deepcopy(batchconnections)
            self.simulation_thread.operators = deepcopy(operators)
            self.simulation_thread.cassette_loops = deepcopy(cassette_loops)
            self.simulation_thread.technicians = deepcopy(technicians)
            
            self.simulation_thread.params = {}
            self.simulation_thread.params.update(self.params)
            
            self.simulation_thread.stop_simulation = False
            self.run_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)

            # clear idle tab and reset headers
            self.table_widget.clear()
             
            headerlabels = ['Type','Name','Nominal','Utilization','Volume']
            for i in range(5,35):
                headerlabels.append("Process " + str(i-5))
            
            self.table_widget.setHorizontalHeaderLabels(headerlabels)
            self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            
            self.qt_thread.start() # Start separate thread and automatically start simulation also
            self.statusBar().showMessage(self.tr("Simulation started"),3000)
            self.bottom_tabwidget.setCurrentIndex(0)            


    def stop_simulation(self):
        self.simulation_thread.stop_simulation = True # sending signal does not work since simulationthread run function will not be interrupted
        self.statusBar().showMessage(self.tr("Simulation stop signal was sent"),3000)

    def switch_profiling_mode(self):
        
        if (self.params['profiling_mode']):
            self.params['profiling_mode'] = False
            self.statusBar().showMessage(self.tr("Profiling mode has been turned off"),3000)
        else:
            self.params['profiling_mode'] = True
            self.statusBar().showMessage(self.tr("Profiling mode has been turned on"),3000)

    def plot_production_rates(self):
        
        if len(self.simulation_thread.prod_rates_df):
             self.statusBar().showMessage(self.tr("Creating plot window..."),3000)
        else:
            self.statusBar().showMessage(self.tr("Please run a simulation first"),3000)
            return     
        
        #if (self.wid):
        #    if (self.wid.isWindow()):
        #        # close previous instances of child windows to save system memory                
        #        self.wid.close()                

        self.wid = MultiPlot(self)
                        
        self.wid.show() 
        
        self.statusBar().showMessage(self.tr("Ready"),3000)

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier): # Ctrl
            selected = self.table_widget.selectedRanges()                 
 
            if e.key() == QtCore.Qt.Key_C: # Copy
                s = ""
                for r in range(selected[0].topRow(),selected[0].bottomRow()+1):
                    for c in range(selected[0].leftColumn(),selected[0].rightColumn()+1):
                        try:
                            s += str(self.table_widget.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)
        """
        elif e.key() == QtCore.Qt.Key_Delete:
            # delete item from either view if del is pressed
            if self.batchlocations_view.hasFocus():
                self.del_batchlocation_view()
            elif self.operators_view.hasFocus():
                self.del_operator_view()
        elif (e.modifiers() == QtCore.Qt.ShiftModifier) and (e.key() == QtCore.Qt.Key_A):
            # add item into either view if enter key is pressed

            if self.batchlocations_view.hasFocus():
                self.add_batchlocation_view()
            elif self.operators_view.hasFocus():
                self.add_operator_view()
        """

    @QtCore.pyqtSlot(str)
    def simulation_output(self,string):        
        
        if self.output_signal_counter < 1000:
            # limit text output to 999 lines to prevent GUI from becoming unresponsive
            self.edit.moveCursor(QtGui.QTextCursor.End) # make sure user cannot re-arrange the output
            #self.edit.insertPlainText(string + '\n')
            self.edit.insertHtml(string + '<br>')
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
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)        

        headerlabels = ['Type','Name','Nominal','Utilization','Volume']
        for i in range(4,15):
            headerlabels.append("Process " + str(i-4))
        self.table_widget.setHorizontalHeaderLabels(headerlabels)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        for i, value in enumerate(utilization):
            overall_util = utilization[i][3]
            item0 = QtWidgets.QTableWidgetItem(utilization[i][0]) # Type
            item1 = QtWidgets.QTableWidgetItem(utilization[i][1]) # Tool name
            item2 = QtWidgets.QTableWidgetItem(str(utilization[i][2])) # Nominal throughput
            item3 = QtWidgets.QTableWidgetItem(str(overall_util) + "%") # Overall utilization                                                          
            item4 = QtWidgets.QTableWidgetItem(str(utilization[i][4])) # Total volume

            if overall_util > 90:
                color = QtGui.QColor(192,80,77)
            elif overall_util < 10:
                color = QtGui.QColor(79,129,189)                
            else:
                color = QtGui.QColor(255,255,255)                
            item3.setBackground(color)
                                                          
            self.table_widget.setItem(i, 0, item0)
            self.table_widget.setItem(i, 1, item1)
            self.table_widget.setItem(i, 2, item2)
            self.table_widget.setItem(i, 3, item3)
            self.table_widget.setItem(i, 4, item4) 
            
            for j in range(5,len(utilization[i])):
                part_name = utilization[i][j][0]
                part_util = utilization[i][j][1]
                item = QtWidgets.QTableWidgetItem(str(part_name) + ": " + str(part_util) + "%")
                if part_util > 90:
                    color = QtGui.QColor(192,80,77)
                elif part_util < 10:
                    color = QtGui.QColor(79,129,189)                
                else:
                    color = QtGui.QColor(255,255,255)                
                item.setBackground(color)
                self.table_widget.setItem(i, j, item)

    @QtCore.pyqtSlot(str)
    def simulation_end_signal(self):
        self.run_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)
        self.statusBar().showMessage(self.tr("Simulation has ended"),3000)

    def open_help_dialog(self):
        help_dialog = HelpDialog(self)
        help_dialog.setModal(True)
        help_dialog.show() 

    def on_about(self):
        msg = self.tr("Solar cell production simulation\nAuthor: Ronald Naber\nLicense: Public domain")
        QtWidgets.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtWidgets.QWidget()        

        ##### Batch locations #####        
        self.batchlocations_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.batchlocations_view.setExpandsOnDoubleClick(False)
        self.batchlocations_model.setHorizontalHeaderLabels(['Process flow'])
        self.batchlocations_view.setModel(self.batchlocations_model)
        self.batchlocations_view.setUniformRowHeights(True)
        self.batchlocations_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.batchlocations_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        line_diagram_button = QtWidgets.QPushButton()
        line_diagram_button.clicked.connect(self.tools_widget.line_diagram_view)
        line_diagram_button.setIcon(QtGui.QIcon(":eye.png"))
        line_diagram_button.setToolTip(self.tr("View production line"))
        line_diagram_button.setStatusTip(self.tr("View production line"))
        
        add_batchlocation_button = QtWidgets.QPushButton()
        add_batchlocation_button.clicked.connect(self.tools_widget.add_batchlocation_view)
        add_batchlocation_button.setIcon(QtGui.QIcon(":plus.png"))
        add_batchlocation_button.setToolTip(self.tr("Add [A]"))
        add_batchlocation_button.setStatusTip(self.tr("Add [A]"))
        
        del_batchlocation_button = QtWidgets.QPushButton()
        del_batchlocation_button.clicked.connect(self.tools_widget.del_batchlocation_view)
        del_batchlocation_button.setIcon(QtGui.QIcon(":minus.png"))
        del_batchlocation_button.setToolTip(self.tr("Remove [Del]"))
        del_batchlocation_button.setStatusTip(self.tr("Remove [Del]"))
        
        edit_batchlocation_button = QtWidgets.QPushButton()
        edit_batchlocation_button.clicked.connect(self.tools_widget.edit_batchlocation_view)        
        edit_batchlocation_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_batchlocation_button.setToolTip(self.tr("Edit settings"))
        edit_batchlocation_button.setStatusTip(self.tr("Edit settings"))        

        empty_batchlocation_view_button = QtWidgets.QPushButton()
        empty_batchlocation_view_button.clicked.connect(self.tools_widget.trash_batchlocation_view)        
        empty_batchlocation_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_batchlocation_view_button.setToolTip(self.tr("Remove all"))
        empty_batchlocation_view_button.setStatusTip(self.tr("Remove all")) 

        buttonbox0 = QtWidgets.QDialogButtonBox()
        buttonbox0.addButton(line_diagram_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(add_batchlocation_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(del_batchlocation_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(edit_batchlocation_button, QtWidgets.QDialogButtonBox.ActionRole)        
        buttonbox0.addButton(empty_batchlocation_view_button, QtWidgets.QDialogButtonBox.ActionRole)

        vbox0 = QtWidgets.QVBoxLayout()
        vbox0.addWidget(self.batchlocations_view)
        vbox0.addWidget(buttonbox0)

        ##### Cassette loops #####
        self.cassetteloops_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cassetteloops_view.setExpandsOnDoubleClick(False)
        self.cassetteloops_model.setHorizontalHeaderLabels(['Cassette loops'])
        self.cassetteloops_view.setModel(self.cassetteloops_model)
        self.cassetteloops_view.setUniformRowHeights(True)
        self.cassetteloops_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.cassetteloops_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        import_locationgroups_button = QtWidgets.QPushButton()
        import_locationgroups_button.clicked.connect(self.cassetteloops_widget.import_locationgroups)        
        import_locationgroups_button.setIcon(QtGui.QIcon(":import.png"))
        import_locationgroups_button.setToolTip(self.tr("Import tools"))
        import_locationgroups_button.setStatusTip(self.tr("Import tools"))

        add_cassetteloop_button = QtWidgets.QPushButton()
        add_cassetteloop_button.clicked.connect(self.cassetteloops_widget.add_cassetteloop_view)           
        add_cassetteloop_button.setIcon(QtGui.QIcon(":plus.png"))
        add_cassetteloop_button.setToolTip(self.tr("Add [A]"))
        add_cassetteloop_button.setStatusTip(self.tr("Add [A]"))
        
        del_cassetteloop_button = QtWidgets.QPushButton()
        del_cassetteloop_button.clicked.connect(self.cassetteloops_widget.del_cassetteloop_view)          
        del_cassetteloop_button.setIcon(QtGui.QIcon(":minus.png"))
        del_cassetteloop_button.setToolTip(self.tr("Remove [Del]"))
        del_cassetteloop_button.setStatusTip(self.tr("Remove [Del]"))

        edit_cassetteloop_button = QtWidgets.QPushButton()
        edit_cassetteloop_button.clicked.connect(self.cassetteloops_widget.edit_cassetteloop_view)        
        edit_cassetteloop_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_cassetteloop_button.setToolTip(self.tr("Edit settings"))
        edit_cassetteloop_button.setStatusTip(self.tr("Edit settings"))
        
        empty_cassetteloop_view_button = QtWidgets.QPushButton()
        empty_cassetteloop_view_button.clicked.connect(self.cassetteloops_widget.trash_cassetteloops_view)        
        empty_cassetteloop_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_cassetteloop_view_button.setToolTip(self.tr("Remove all"))
        empty_cassetteloop_view_button.setStatusTip(self.tr("Remove all"))        

        buttonbox1 = QtWidgets.QDialogButtonBox()
        buttonbox1.addButton(import_locationgroups_button, QtWidgets.QDialogButtonBox.ActionRole)       
        buttonbox1.addButton(add_cassetteloop_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(del_cassetteloop_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(edit_cassetteloop_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(empty_cassetteloop_view_button, QtWidgets.QDialogButtonBox.ActionRole)

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.cassetteloops_view)
        vbox1.addWidget(buttonbox1)

        ##### Operators #####
        self.operators_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.operators_view.setExpandsOnDoubleClick(False)
        self.operators_model.setHorizontalHeaderLabels(['Operators'])
        self.operators_view.setModel(self.operators_model)
        self.operators_view.setUniformRowHeights(True)
        self.operators_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.operators_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        import_batchlocations_button = QtWidgets.QPushButton()
        import_batchlocations_button.clicked.connect(self.operators_widget.import_batchlocations)        
        import_batchlocations_button.setIcon(QtGui.QIcon(":import.png"))
        import_batchlocations_button.setToolTip(self.tr("Auto-generate operators"))
        import_batchlocations_button.setStatusTip(self.tr("Auto-generate operators"))

        add_operator_button = QtWidgets.QPushButton()
        add_operator_button.clicked.connect(self.operators_widget.add_operator_view)           
        add_operator_button.setIcon(QtGui.QIcon(":plus.png"))
        add_operator_button.setToolTip(self.tr("Add [A]"))
        add_operator_button.setStatusTip(self.tr("Add [A]"))
        
        del_operator_button = QtWidgets.QPushButton()
        del_operator_button.clicked.connect(self.operators_widget.del_operator_view)          
        del_operator_button.setIcon(QtGui.QIcon(":minus.png"))
        del_operator_button.setToolTip(self.tr("Remove [Del]"))
        del_operator_button.setStatusTip(self.tr("Remove [Del]"))

        edit_operator_button = QtWidgets.QPushButton()
        edit_operator_button.clicked.connect(self.operators_widget.edit_operator_view)        
        edit_operator_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_operator_button.setToolTip(self.tr("Edit settings"))
        edit_operator_button.setStatusTip(self.tr("Edit settings"))
        
        empty_operator_view_button = QtWidgets.QPushButton()
        empty_operator_view_button.clicked.connect(self.operators_widget.trash_operator_view)        
        empty_operator_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_operator_view_button.setToolTip(self.tr("Remove all"))
        empty_operator_view_button.setStatusTip(self.tr("Remove all"))        

        buttonbox2 = QtWidgets.QDialogButtonBox()
        buttonbox2.addButton(import_batchlocations_button, QtWidgets.QDialogButtonBox.ActionRole)       
        buttonbox2.addButton(add_operator_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox2.addButton(del_operator_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox2.addButton(edit_operator_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox2.addButton(empty_operator_view_button, QtWidgets.QDialogButtonBox.ActionRole)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.operators_view)
        vbox2.addWidget(buttonbox2)

        ##### Technicians #####
        self.technicians_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.technicians_view.setExpandsOnDoubleClick(False)
        self.technicians_model.setHorizontalHeaderLabels(['Technicians'])
        self.technicians_view.setModel(self.technicians_model)
        self.technicians_view.setUniformRowHeights(True)
        self.technicians_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.technicians_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        import_batchlocations_tech_button = QtWidgets.QPushButton()
        import_batchlocations_tech_button.clicked.connect(self.technicians_widget.import_batchlocations_tech)        
        import_batchlocations_tech_button.setIcon(QtGui.QIcon(":import.png"))
        import_batchlocations_tech_button.setToolTip(self.tr("Auto-generate technicians"))
        import_batchlocations_tech_button.setStatusTip(self.tr("Auto-generate technicians"))

        add_technician_button = QtWidgets.QPushButton()
        add_technician_button.clicked.connect(self.technicians_widget.add_technician_view)           
        add_technician_button.setIcon(QtGui.QIcon(":plus.png"))
        add_technician_button.setToolTip(self.tr("Add [A]"))
        add_technician_button.setStatusTip(self.tr("Add [A]"))
        
        del_technician_button = QtWidgets.QPushButton()
        del_technician_button.clicked.connect(self.technicians_widget.del_technician_view)          
        del_technician_button.setIcon(QtGui.QIcon(":minus.png"))
        del_technician_button.setToolTip(self.tr("Remove [Del]"))
        del_technician_button.setStatusTip(self.tr("Remove [Del]"))

        edit_technician_button = QtWidgets.QPushButton()
        edit_technician_button.clicked.connect(self.technicians_widget.edit_technician_view)        
        edit_technician_button.setIcon(QtGui.QIcon(":gear.png"))
        edit_technician_button.setToolTip(self.tr("Edit settings"))
        edit_technician_button.setStatusTip(self.tr("Edit settings"))
        
        empty_technician_view_button = QtWidgets.QPushButton()
        empty_technician_view_button.clicked.connect(self.technicians_widget.trash_technician_view)        
        empty_technician_view_button.setIcon(QtGui.QIcon(":trash.png"))
        empty_technician_view_button.setToolTip(self.tr("Remove all"))
        empty_technician_view_button.setStatusTip(self.tr("Remove all"))        

        buttonbox3 = QtWidgets.QDialogButtonBox()
        buttonbox3.addButton(import_batchlocations_tech_button, QtWidgets.QDialogButtonBox.ActionRole)       
        buttonbox3.addButton(add_technician_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox3.addButton(del_technician_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox3.addButton(edit_technician_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox3.addButton(empty_technician_view_button, QtWidgets.QDialogButtonBox.ActionRole)

        vbox3 = QtWidgets.QVBoxLayout()
        vbox3.addWidget(self.technicians_view)
        vbox3.addWidget(buttonbox3)

        ##### Top buttonbox #####
        open_file_button = QtWidgets.QPushButton()
        tip = self.tr("Open file")
        open_file_button.clicked.connect(self.open_file)        
        open_file_button.setIcon(QtGui.QIcon(":open.png"))
        open_file_button.setToolTip(tip)
        open_file_button.setStatusTip(tip)     

        save_file_button = QtWidgets.QPushButton()
        tip = self.tr("Save to file")
        save_file_button.clicked.connect(self.save_to_file) 
        save_file_button.setIcon(QtGui.QIcon(":save.png"))
        save_file_button.setToolTip(tip)
        save_file_button.setStatusTip(tip)

        self.run_sim_button = QtWidgets.QPushButton()
        tip = self.tr("Run simulation")
        self.run_sim_button.clicked.connect(self.run_simulation)         
        self.run_sim_button.setIcon(QtGui.QIcon(":play.png"))
        self.run_sim_button.setToolTip(tip)
        self.run_sim_button.setStatusTip(tip)
        self.run_sim_button.setShortcut('Ctrl+R')
        
        self.stop_sim_button = QtWidgets.QPushButton()
        tip = self.tr("Stop simulation")
        self.stop_sim_button.clicked.connect(self.stop_simulation)          
        self.stop_sim_button.setIcon(QtGui.QIcon(":stop.png"))
        self.stop_sim_button.setToolTip(tip)
        self.stop_sim_button.setStatusTip(tip)
        self.stop_sim_button.setEnabled(False)
        self.stop_sim_button.setShortcut('Escape')

        self.plot_production_rates_button = QtWidgets.QPushButton()
        self.plot_production_rates_button.clicked.connect(self.plot_production_rates)
        self.plot_production_rates_button.setIcon(QtGui.QIcon(":chart.png"))
        self.plot_production_rates_button.setToolTip(self.tr("Plot production rate results"))
        self.plot_production_rates_button.setStatusTip(self.tr("Plot production rate results"))

        self.switch_profiling_mode_button = QtWidgets.QCheckBox()
        self.switch_profiling_mode_button.clicked.connect(self.switch_profiling_mode)
        self.switch_profiling_mode_button.setChecked(False)
        self.switch_profiling_mode_button.setToolTip(self.tr("Turn profiling mode on or off"))
        self.switch_profiling_mode_button.setStatusTip(self.tr("Turn profiling mode on or off"))

        top_buttonbox = QtWidgets.QDialogButtonBox()
        top_buttonbox.addButton(open_file_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(save_file_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.run_sim_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.stop_sim_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.plot_production_rates_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.switch_profiling_mode_button, QtWidgets.QDialogButtonBox.ActionRole)

        self.sim_time_combo = QtWidgets.QComboBox(self)
        for i in self.sim_time_selection_list:
            self.sim_time_combo.addItem(i)
        
        toolbar_hbox = QtWidgets.QHBoxLayout()
        toolbar_hbox.addWidget(top_buttonbox)
        toolbar_hbox.addWidget(self.sim_time_combo)        
        
        self.bottom_tabwidget = QtWidgets.QTabWidget()
        self.bottom_tabwidget.addTab(self.edit, "Activity")
        self.bottom_tabwidget.addTab(self.table_widget, "Utilization")
        
        ##### Main layout #####
        top_hbox = QtWidgets.QHBoxLayout()
        top_hbox.setDirection(QtWidgets.QBoxLayout.LeftToRight)
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)
        top_hbox.addLayout(vbox2)
        top_hbox.addLayout(vbox3)

        vbox = QtWidgets.QVBoxLayout()       
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox)
        vbox.addWidget(self.bottom_tabwidget)
                                                         
        self.main_frame.setLayout(vbox)

        self.setCentralWidget(self.main_frame)

        self.status_text = QtWidgets.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Ready"),3000)

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))

        tip = self.tr("Open file")        
        load_action = QtWidgets.QAction(self.tr("Open..."), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self.open_file)
        load_action.setStatusTip(tip)
        load_action.setShortcut('Ctrl+O')

        tip = self.tr("Save to file")        
        save_action = QtWidgets.QAction(self.tr("Save"), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self.save_to_file)        
        save_action.setStatusTip(tip)
        save_action.setShortcut('Ctrl+S')

        tip = self.tr("Save to file as...")        
        saveas_action = QtWidgets.QAction(self.tr("Save as..."), self)
        saveas_action.triggered.connect(self.save_to_file_as)         
        saveas_action.setStatusTip(tip)        

        tip = self.tr("Quit")        
        quit_action = QtWidgets.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)        
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)        
        self.file_menu.addAction(quit_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("Help information")        
        help_action = QtWidgets.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self.open_help_dialog)         
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')

        tip = self.tr("About the application")        
        about_action = QtWidgets.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self.on_about)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(help_action)
        self.help_menu.addAction(about_action)
