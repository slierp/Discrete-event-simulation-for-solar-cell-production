# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
from batchlocations.Operator import Operator
from sys import platform as _platform

class dummy_env(object):
    
    def process(dummy0=None,dummy1=None):
        pass

    def now(self):
        pass
    
    def event(dummy0=None):
        pass

class OperatorSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):

        super(QtWidgets.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.view = self.parent.operators_view
        self.model = self.parent.operators_model
        self.batchlocations = self.parent.tools_widget.batchlocations
        self.operators = self.parent.operators_widget.operators
        self.statusbar = self.parent.statusBar()
        self.load_definition = self.parent.operators_widget.load_definition

        self.batchconnections = self.parent.tools_widget.batchconnections
        self.print_batchconnection = self.parent.operators_widget.print_batchconnection

        # find out which operator was selected
        self.row = self.view.selectedIndexes()[0].row()

        env = dummy_env()
        curr_params = {}
        # load default settings list
        curr_params = Operator(env).params

        # update default settings list with currently stored settings
        curr_params.update(self.operators[self.row][1])

        self.setWindowTitle(self.tr("Operator settings"))

        tabwidget = QtWidgets.QTabWidget()

        ### Connections tab ###
        vbox = QtWidgets.QVBoxLayout() # vbox for all connections

        title_label = QtWidgets.QLabel(self.tr("Available connections:"))
        vbox.addWidget(title_label)

        self.dataset_cb = []
        for i, value in enumerate(self.batchconnections):
            self.dataset_cb.append(QtWidgets.QCheckBox(self.print_batchconnection(i)))
            if i in self.operators[self.row][0]:
                self.dataset_cb[i].setChecked(True)

        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()

        for i in range(len(self.dataset_cb)):
            self.dataset_cb[i].setMinimumWidth(400) # prevent obscured text
            checkbox_vbox.addWidget(self.dataset_cb[i])

        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)

        generic_widget_connections = QtWidgets.QWidget()
        generic_widget_connections.setLayout(vbox)
        tabwidget.addTab(generic_widget_connections, "Connections")

        ### Settings tab ###
        vbox = QtWidgets.QVBoxLayout() # vbox for all settings  
        
        # Make QLineEdit for name
        hbox = QtWidgets.QHBoxLayout()
        self.lineedit0 = QtWidgets.QLineEdit(curr_params['name'])
        self.lineedit0.setMaxLength(5)
        description = QtWidgets.QLabel('Name of the individual operator')
        self.lineedit0.setToolTip('Name of the individual operator')
        hbox.addWidget(self.lineedit0) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(curr_params["wait_time_desc"])
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999)
        self.spinbox0.setValue(curr_params['wait_time'])                   
        self.spinbox0.setToolTip(curr_params["wait_time_desc"])
        hbox.addWidget(self.spinbox0)  
        hbox.addWidget(description)
        hbox.addStretch(1)                 
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel(curr_params['shuffle_connections_desc'])
        self.boolean0 = QtWidgets.QCheckBox()
        self.boolean0.setChecked(curr_params['shuffle_connections'])
        self.boolean0.setToolTip(curr_params['shuffle_connections_desc'])
        description.mouseReleaseEvent = self.switch_boolean0
        hbox.addWidget(self.boolean0)
        hbox.addWidget(description)
        hbox.addStretch(1)                 
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        description = QtWidgets.QLabel("Apply settings to all connections (excluding name)")
        self.boolean1 = QtWidgets.QCheckBox()
        self.boolean1.setChecked(False)
        self.boolean1.setToolTip("Apply settings to all connections (excluding name)")
        description.mouseReleaseEvent = self.switch_boolean1
        hbox.addWidget(self.boolean1)
        hbox.addWidget(description)
        hbox.addStretch(1)                 
        vbox.addLayout(hbox)        

        vbox.addStretch(1)
        generic_widget_settings = QtWidgets.QWidget()
        generic_widget_settings.setLayout(vbox)
        tabwidget.addTab(generic_widget_settings, "Settings")

        ### Description tab ###
        vbox_description = QtWidgets.QVBoxLayout() # vbox for description elements        
       
        hbox = QtWidgets.QHBoxLayout()           
        browser = QtWidgets.QTextBrowser()
        browser.insertHtml(curr_params['specification'])
        browser.moveCursor(QtGui.QTextCursor.Start)        
        hbox.addWidget(browser)
        vbox_description.addLayout(hbox)

        generic_widget_description = QtWidgets.QWidget()
        generic_widget_description.setLayout(vbox_description)
        tabwidget.addTab(generic_widget_description, "Description")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabwidget) 

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(800)

    def switch_boolean0(self, event):
        # function for making QLabel near checkbox clickable
        self.boolean0.setChecked(not self.boolean0.isChecked())

    def switch_boolean1(self, event):
        # function for making QLabel near checkbox clickable
        self.boolean1.setChecked(not self.boolean1.isChecked())

    def read(self):
        # read contents of each widget
        # update settings in self.operators[self.row] of parent
        
        if not self.boolean1.isChecked():
            new_params = {}
            new_params['name'] = str(self.lineedit0.text())
            new_params['wait_time'] = int(self.spinbox0.text())
            new_params['shuffle_connections'] = self.boolean0.isChecked()        
            self.operators[self.row][1].update(new_params)
        else:
            self.operators[self.row][1]['name'] = str(self.lineedit0.text())
            
            new_params = {}
            new_params['wait_time'] = int(self.spinbox0.text())
            new_params['shuffle_connections'] = self.boolean0.isChecked()
            
            for i in range(len(self.operators)):
                self.operators[i][1].update(new_params)
        
        # Add connections to operator
        self.operators[self.row][0] = []
        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                self.operators[self.row][0].append(i)
        
        self.operators[self.row][0].sort()
        
        self.load_definition(False)

        # select row again after reloading operator definitions
        index = self.model.index(self.row, 0)
        self.view.setCurrentIndex(index)
        self.view.setExpanded(index, True)                    
        
        self.statusbar.showMessage(self.tr("Operator settings updated"),3000)
        self.accept()