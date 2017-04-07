# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class CassetteLoopSettingsDialog(QtWidgets.QDialog):
    def __init__(self, _parent, _row):

        super(QtWidgets.QDialog, self).__init__(_parent)

        self.parent = _parent
        self.cassette_loops = self.parent.cassetteloops_widget.cassette_loops
        self.statusbar = self.parent.statusBar()          
        
        self.row = _row
        self.setWindowTitle(self.tr("Cassette loop settings"))
        vbox = QtWidgets.QVBoxLayout()            

        hbox = QtWidgets.QHBoxLayout()
        text = "Number of cassettes in loop"
        label = QtWidgets.QLabel(text)
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999)
        self.spinbox0.setMinimum(1)
        self.spinbox0.setValue(self.cassette_loops[self.row][2])
        label.setToolTip(text)
        self.spinbox0.setToolTip(text)
        hbox.addWidget(self.spinbox0)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        text = "Amount of wafers that fit in each cassette"
        label = QtWidgets.QLabel(text)
        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox1.setAccelerated(True)
        self.spinbox1.setMaximum(999)
        self.spinbox1.setMinimum(1)
        self.spinbox1.setValue(self.cassette_loops[self.row][3])
        label.setToolTip(text)
        self.spinbox1.setToolTip(text)
        hbox.addWidget(self.spinbox1)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        text = "Time needed for a single empty cassette transport"
        label = QtWidgets.QLabel(text)
        self.spinbox2 = QtWidgets.QSpinBox()
        self.spinbox2.setAccelerated(True)
        self.spinbox2.setMaximum(999)
        self.spinbox2.setMinimum(1)
        self.spinbox2.setValue(self.cassette_loops[self.row][4])
        label.setToolTip(text)
        self.spinbox2.setToolTip(text)
        hbox.addWidget(self.spinbox2)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        text = "Time added for each additional cassette"
        label = QtWidgets.QLabel(text)
        self.spinbox3 = QtWidgets.QSpinBox()
        self.spinbox3.setAccelerated(True)
        self.spinbox3.setMaximum(999)
        self.spinbox3.setMinimum(0)
        self.spinbox3.setValue(self.cassette_loops[self.row][5])
        label.setToolTip(text)
        self.spinbox3.setToolTip(text)
        hbox.addWidget(self.spinbox3)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)        

        hbox = QtWidgets.QHBoxLayout()
        text = "Minimum number of cassettes needed to start transport"
        label = QtWidgets.QLabel(text)
        self.spinbox4 = QtWidgets.QSpinBox()
        self.spinbox4.setAccelerated(True)
        self.spinbox4.setMaximum(99)
        self.spinbox4.setMinimum(1)
        self.spinbox4.setValue(self.cassette_loops[self.row][6])
        label.setToolTip(text)
        self.spinbox4.setToolTip(text)
        hbox.addWidget(self.spinbox4)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hard_limit_check = False
        # if not integer then it is a hard transport limit
        if (self.cassette_loops[self.row][6] % 1) > 0:
            hard_limit_check = True

        hbox = QtWidgets.QHBoxLayout()
        text = "Apply minimum transport limit irrespective of space at destination"
        label = QtWidgets.QLabel(text)
        self.hard_limit_boolean = QtWidgets.QCheckBox()
        self.hard_limit_boolean.setChecked(hard_limit_check)
        label.setToolTip(text)
        self.hard_limit_boolean.setToolTip(text)        
        label.mouseReleaseEvent = self.switch_hard_limit       
        hbox.addWidget(self.hard_limit_boolean)
        hbox.addWidget(label)
        hbox.addStretch(1)                 
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        text = "Maximum number of cassettes for one transport run"
        label = QtWidgets.QLabel(text)
        self.spinbox5 = QtWidgets.QSpinBox()
        self.spinbox5.setAccelerated(True)
        self.spinbox5.setMaximum(99)
        self.spinbox5.setMinimum(1)
        self.spinbox5.setValue(self.cassette_loops[self.row][7])
        label.setToolTip(text)
        self.spinbox5.setToolTip(text)
        hbox.addWidget(self.spinbox5)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        text = "Apply current settings to all cassette loops"
        label = QtWidgets.QLabel(text)
        self.boolean = QtWidgets.QCheckBox()
        self.boolean.setChecked(False)
        label.setToolTip(text)
        self.boolean.setToolTip(text)        
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

    def switch_hard_limit(self, event):
        # function for making QLabel near checkbox clickable
        self.hard_limit_boolean.setChecked(not self.hard_limit_boolean.isChecked())

    def read(self):

        if self.hard_limit_boolean:        
            transport_min_limit = int(self.spinbox4.text()) + 0.1
        else:
            transport_min_limit = int(self.spinbox4.text())
        
        # read contents of each widget
        if self.boolean.isChecked():
            for i in range(len(self.cassette_loops)):
                self.cassette_loops[i][2] = int(self.spinbox0.text())
                self.cassette_loops[i][3] = int(self.spinbox1.text())
                self.cassette_loops[i][4] = int(self.spinbox2.text())
                self.cassette_loops[i][5] = int(self.spinbox3.text())                
                self.cassette_loops[i][6] = transport_min_limit
                self.cassette_loops[i][7] = int(self.spinbox5.text())
        else:
            self.cassette_loops[self.row][2] = int(self.spinbox0.text())
            self.cassette_loops[self.row][3] = int(self.spinbox1.text())
            self.cassette_loops[self.row][4] = int(self.spinbox2.text())
            self.cassette_loops[self.row][5] = int(self.spinbox3.text())
            self.cassette_loops[self.row][6] = transport_min_limit
            self.cassette_loops[self.row][7] = int(self.spinbox5.text())

        self.statusbar.showMessage(self.tr("Cassette loop settings updated"))                
        self.accept()