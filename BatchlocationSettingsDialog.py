# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtGui

class BatchlocationSettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None, curr_params = {}):
        super(QtGui.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent
        self.setWindowTitle(self.tr("Available settings"))
        vbox = QtGui.QVBoxLayout()

        if 'specification' in curr_params:
            spec = QtGui.QPlainTextEdit(curr_params['specification'])
            spec.setReadOnly(True)
            vbox.addWidget(spec)
        else:
            title_label = QtGui.QLabel(self.tr("Edit settings:"))
            vbox.addWidget(title_label)             
        
        self.strings = []
        for i in curr_params:
            if ("_desc" in i) | ('specification' in i):
                continue
            elif isinstance(curr_params[i], str):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.strings.append(QtGui.QLineEdit(curr_params[i]))
                self.strings[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.strings[-1].setToolTip(curr_params[i + "_desc"])
                hbox.addWidget(label)
                hbox.addWidget(self.strings[-1]) 
                vbox.addLayout(hbox)
        
        self.integers = []
        for i in curr_params:
            if isinstance(curr_params[i], int) & (not i == 'verbose'):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.integers.append(QtGui.QSpinBox())
                self.integers[-1].setAccelerated(True)
                self.integers[-1].setMaximum(999999999)
                self.integers[-1].setValue(curr_params[i])
                self.integers[-1].setObjectName(i)
                if (curr_params[i] >= 100):
                    self.integers[-1].setSingleStep(100)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.integers[-1].setToolTip(curr_params[i + "_desc"])                  
                hbox.addWidget(label)
                hbox.addWidget(self.integers[-1])  
                vbox.addLayout(hbox)

        self.doubles = []
        for i in curr_params:
            if isinstance(curr_params[i], float):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.doubles.append(QtGui.QDoubleSpinBox())
                self.doubles[-1].setAccelerated(True)
                self.doubles[-1].setMaximum(999999999)
                self.doubles[-1].setValue(curr_params[i])
                self.doubles[-1].setSingleStep(0.1)
                self.doubles[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.doubles[-1].setToolTip(curr_params[i + "_desc"])             
                hbox.addWidget(label)
                hbox.addWidget(self.doubles[-1]) 
                vbox.addLayout(hbox)
        
        self.booleans = []
        for i in curr_params:
            if isinstance(curr_params[i], bool):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.booleans.append(QtGui.QCheckBox())                
                self.booleans[-1].setChecked(curr_params[i])
                self.booleans[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.booleans[-1].setToolTip(curr_params[i + "_desc"])               
                hbox.addWidget(label)
                hbox.addWidget(self.booleans[-1]) 
                vbox.addLayout(hbox)

        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def read(self):
        # read contents of each widget
        # update settings in self.batchlocations[self.modified_batchlocation_number] of parent
        new_params = {}
        for i in self.strings:
            new_params[str(i.objectName())] = str(i.text())

        for i in self.integers:
            new_params[str(i.objectName())] = int(i.text())

        for i in self.doubles:
            new_params[str(i.objectName())] = float(i.text())

        for i in self.booleans:
            new_params[str(i.objectName())] = i.isChecked()
        
        self.parent.batchlocations[self.parent.modified_batchlocation_number][1].update(new_params)
        self.parent.load_definition_batchlocations(False)
        self.accept()