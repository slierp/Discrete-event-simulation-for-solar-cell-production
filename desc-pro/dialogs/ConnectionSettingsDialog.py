# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class ConnectionSettingsDialog(QtWidgets.QDialog):
    def __init__(self, _parent, _batchconnection):
        super(QtWidgets.QDialog, self).__init__(_parent)
        # create dialog screen for changing connection parameters
        
        self.parent = _parent
        self.batchconnection = _batchconnection
        self.setWindowTitle(self.tr("Connection settings"))
        vbox = QtWidgets.QVBoxLayout()            
        
        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Time needed for a single transport action")
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999999999)
        self.spinbox0.setValue(self.batchconnection[2])
        label.setToolTip("Time needed for a single transport action")
        self.spinbox0.setToolTip("Time needed for a single transport action")
        if (self.batchconnection[2] >= 100):
            self.spinbox0.setSingleStep(100)
        elif (self.batchconnection[2] >= 10):
            self.spinbox0.setSingleStep(10) 
        hbox.addWidget(self.spinbox0)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Time added for each additional batch")
        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox1.setAccelerated(True)
        self.spinbox1.setMaximum(999999999)
        self.spinbox1.setValue(self.batchconnection[3])
        label.setToolTip("Time added for each additional batch")
        self.spinbox1.setToolTip("Time added for each additional batch")
        if (self.batchconnection[3] >= 100):
            self.spinbox1.setSingleStep(100)
        elif (self.batchconnection[3] >= 10):
            self.spinbox1.setSingleStep(10) 
        hbox.addWidget(self.spinbox1)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Minimum number of batches needed to start transport")
        self.spinbox2 = QtWidgets.QSpinBox()
        self.spinbox2.setAccelerated(True)
        self.spinbox2.setMaximum(999)
        self.spinbox2.setMinimum(1)
        self.spinbox2.setValue(self.batchconnection[4])
        label.setToolTip("Minimum number of batches needed to start transport")
        self.spinbox2.setToolTip("Minimum number of batches needed to start transport")
        hbox.addWidget(self.spinbox2)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Maximum number of batches for one transport run")
        self.spinbox3 = QtWidgets.QSpinBox()
        self.spinbox3.setAccelerated(True)
        self.spinbox3.setMaximum(999)
        self.spinbox3.setMinimum(1)
        self.spinbox3.setValue(self.batchconnection[5])
        label.setToolTip("Maximum number of batches for one transport run")
        self.spinbox3.setToolTip("Maximum number of batches for one transport run")
        hbox.addWidget(self.spinbox3)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Apply current settings to all connections")
        self.boolean = QtWidgets.QCheckBox()
        self.boolean.setChecked(False)
        label.setToolTip("Apply current settings to all connections")
        self.boolean.setToolTip("Apply current settings to all connections")        
        label.mouseReleaseEvent = self.switch_boolean        
        hbox.addWidget(self.boolean)
        hbox.addWidget(label)
        hbox.addStretch(1)                 
        vbox.addLayout(hbox)

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft) 
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)        

    def switch_boolean(self, event):
        # function for making QLabel near checkbox clickable
        self.boolean.setChecked(not self.boolean.isChecked())

    def read(self):
        # read contents of each widget
        # update settings in batchconnection(s)
        if self.boolean.isChecked():
            for i in range(len(self.parent.batchconnections)):
                self.parent.batchconnections[i][2] = int(self.spinbox0.text())
                self.parent.batchconnections[i][3] = int(self.spinbox1.text())
                self.parent.batchconnections[i][4] = int(self.spinbox2.text())
                self.parent.batchconnections[i][5] = int(self.spinbox3.text())
            
            self.parent.statusBar().showMessage(self.tr("All connection settings updated"))
        else:
            self.batchconnection[2] = int(self.spinbox0.text())
            self.batchconnection[3] = int(self.spinbox1.text())
            self.batchconnection[4] = int(self.spinbox2.text())
            self.batchconnection[5] = int(self.spinbox3.text())
            self.parent.statusBar().showMessage(self.tr("Connection settings updated"))
        
        
        self.accept()