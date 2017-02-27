# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class CassetteLoopSettingsDialog(QtWidgets.QDialog):
    def __init__(self, _parent, _row):

        super(QtWidgets.QDialog, self).__init__(_parent)
        
        self.parent = _parent
        self.row = _row
        self.setWindowTitle(self.tr("Cassette loop settings"))
        vbox = QtWidgets.QVBoxLayout()            

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Number of cassettes")
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999)
        self.spinbox0.setMinimum(1)
        self.spinbox0.setValue(self.parent.cassette_loops[self.row][2])
        label.setToolTip("Number of cassettes")
        self.spinbox0.setToolTip("Number of cassettes")
        hbox.addWidget(self.spinbox0)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Amount of wafers that fit in each cassette")
        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox1.setAccelerated(True)
        self.spinbox1.setMaximum(999)
        self.spinbox1.setMinimum(1)
        self.spinbox1.setValue(self.parent.cassette_loops[self.row][3])
        label.setToolTip("Amount of wafers that fit in each cassette")
        self.spinbox1.setToolTip("Amount of wafers that fit in each cassette")
        hbox.addWidget(self.spinbox1)  
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

    def read(self):
        # read contents of each widget
        self.parent.cassette_loops[self.row][2] = int(self.spinbox0.text())
        self.parent.cassette_loops[self.row][3] = int(self.spinbox1.text())
        self.parent.statusBar().showMessage(self.tr("Cassette loop settings updated"))
                
        self.accept()