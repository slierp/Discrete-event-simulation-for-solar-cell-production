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
         
        self.strings = []
        
        # Make QLineEdit for name
        hbox = QtWidgets.QHBoxLayout()
        self.strings.append(QtWidgets.QLineEdit(curr_params['name']))
        self.strings[-1].setObjectName('name')
        self.strings[-1].setMaxLength(5)
        description = QtWidgets.QLabel('Name of the individual operator')
        self.strings[-1].setToolTip('Name of the individual operator')
        hbox.addWidget(self.strings[-1]) 
        hbox.addWidget(description)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.integers = []
        for i in curr_params:
            if isinstance(curr_params[i], int):
                hbox = QtWidgets.QHBoxLayout()
                description = QtWidgets.QLabel(curr_params[i + "_desc"])
                self.integers.append(QtWidgets.QSpinBox())
                self.integers[-1].setAccelerated(True)
                self.integers[-1].setMaximum(999999999)
                self.integers[-1].setValue(curr_params[i])
                self.integers[-1].setObjectName(i)
                if (curr_params[i] >= 100):
                    self.integers[-1].setSingleStep(100)
                elif (curr_params[i] >= 10):
                    self.integers[-1].setSingleStep(10)                     
                if i + "_desc" in curr_params:
                    self.integers[-1].setToolTip(curr_params[i + "_desc"])
                hbox.addWidget(self.integers[-1])  
                hbox.addWidget(description)
                hbox.addStretch(1)                 
                vbox.addLayout(hbox)

        self.doubles = []
        for i in curr_params:
            if isinstance(curr_params[i], float):
                hbox = QtWidgets.QHBoxLayout()
                description = QtWidgets.QLabel(curr_params[i + "_desc"])
                self.doubles.append(QtWidgets.QDoubleSpinBox())
                self.doubles[-1].setAccelerated(True)
                self.doubles[-1].setMaximum(999999999)
                self.doubles[-1].setValue(curr_params[i])
                self.doubles[-1].setSingleStep(0.1)
                self.doubles[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    self.doubles[-1].setToolTip(curr_params[i + "_desc"])
                hbox.addWidget(self.doubles[-1])
                hbox.addWidget(description)
                hbox.addStretch(1)                  
                vbox.addLayout(hbox)
        
        self.booleans = []
        for i in curr_params:
            if isinstance(curr_params[i], bool):
                hbox = QtWidgets.QHBoxLayout()
                description = QtWidgets.QLabel(curr_params[i + "_desc"])
                self.booleans.append(QtWidgets.QCheckBox())                
                self.booleans[-1].setChecked(curr_params[i])
                self.booleans[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    self.booleans[-1].setToolTip(curr_params[i + "_desc"])
                hbox.addWidget(self.booleans[-1])
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

    def read(self):
        # read contents of each widget
        # update settings in self.operators[self.row] of parent
        new_params = {}
        for i in self.strings:
            new_params[str(i.objectName())] = str(i.text())

        for i in self.integers:
            new_params[str(i.objectName())] = int(i.text())

        for i in self.doubles:
            new_params[str(i.objectName())] = float(i.text())

        for i in self.booleans:
            new_params[str(i.objectName())] = i.isChecked()
        
        self.operators[self.row][1].update(new_params)
        
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
        self.statusbar.showMessage(self.tr("Operator settings updated"),3000)
        self.accept()