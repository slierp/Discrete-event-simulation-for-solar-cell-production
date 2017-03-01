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

        non_cassette_names = []
        non_cassette_names.append("Source")        
        non_cassette_names.append("Plasma edge isolation")

        self.dataset_cb = []
        non_cassette_groups = []        
        for i, value in enumerate(self.parent.locationgroups):
            name = self.parent.group_names[self.parent.batchlocations[self.parent.locationgroups[i][0]][0]]
            self.dataset_cb.append(QtWidgets.QCheckBox(name))
            if self.parent.cassette_loops[self.row][0] <= i <= self.parent.cassette_loops[self.row][1]:
                self.dataset_cb[i].setChecked(True)

            if name in non_cassette_names:
                non_cassette_groups.append(i)

        unavailable_groups = []
        # remove groups already allocated in other cassette loops
        for i in range(len(self.parent.cassette_loops)):
            if not (i == self.row):
                for j in range(self.parent.cassette_loops[i][0],self.parent.cassette_loops[i][1]+1):
                    unavailable_groups.append(j)

        # re-insert groups that are in the current cassette loop
        for i in range(self.parent.cassette_loops[self.row][0],self.parent.cassette_loops[self.row][1]+1):
            if i in unavailable_groups:
                unavailable_groups = list(filter(lambda a: a != i, unavailable_groups))

        # groups before and after are the list are also unavailable
        unavailable_groups.append(-1)
        unavailable_groups.append(len(self.parent.locationgroups))

        unavailable_groups += non_cassette_groups

        for i in range(len(self.parent.locationgroups)):
            # remove any groups that cannot form a connection
            if ((i-1) in unavailable_groups) and ((i+1) in unavailable_groups):
                unavailable_groups.append(i)
        
            if i in unavailable_groups:
                self.dataset_cb[i].setEnabled(False)

        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()

        for i in range(len(self.dataset_cb)):
            self.dataset_cb[i].setMinimumWidth(400) # prevent obscured text
            checkbox_vbox.addWidget(self.dataset_cb[i])

        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)

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

        begin = end = 0

        for i in range(len(self.dataset_cb)-1):
            if self.dataset_cb[i].isChecked():
                begin = i
                break

        for i in range(begin,len(self.dataset_cb)):
            if (self.dataset_cb[i].isChecked()):    
                end = i
            elif (not self.dataset_cb[i].isChecked()):
                break
            
        if not begin >= end:
            self.parent.cassette_loops[self.row][0] = begin
            self.parent.cassette_loops[self.row][1] = end

        self.parent.load_definition_cassetteloops(False)

        self.parent.statusBar().showMessage(self.tr("Cassette loop settings updated"))                
        self.accept()