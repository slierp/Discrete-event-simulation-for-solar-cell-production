# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddCassetteLoopDialog(QtWidgets.QDialog):
    def __init__(self, _parent):

        super(QtWidgets.QDialog, self).__init__(_parent)

        self.parent = _parent
        self.setWindowTitle(self.tr("Add cassette loop"))
        vbox = QtWidgets.QVBoxLayout()            

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Number of cassettes")
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999)
        self.spinbox0.setMinimum(1)
        self.spinbox0.setValue(100)
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
        self.spinbox1.setValue(100)
        label.setToolTip("Amount of wafers that fit in each cassette")
        self.spinbox1.setToolTip("Amount of wafers that fit in each cassette")
        hbox.addWidget(self.spinbox1)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        non_cassette_groups = []
        non_cassette_groups.append("Source")        
        non_cassette_groups.append("Plasma edge isolation")
        
        unavailable_groups = []
        for i in range(len(self.parent.cassette_loops)):
            for j in range(self.parent.cassette_loops[i][0]+1,self.parent.cassette_loops[i][1]):
                unavailable_groups.append(j)

        self.dataset_cb = []
        for i, value in enumerate(self.parent.locationgroups):
            name = self.parent.group_names[self.parent.batchlocations[self.parent.locationgroups[i][0]][0]]
            self.dataset_cb.append(QtWidgets.QCheckBox(name))
                
            if (name in non_cassette_groups):
                unavailable_groups.append(i)

        unavailable_groups.append(-1)
        unavailable_groups.append(len(self.parent.locationgroups))

        for i in range(len(self.parent.locationgroups)):
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
        no_cassettes = int(self.spinbox0.text())
        no_wafers = int(self.spinbox1.text())

        begin = end = 0

        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                begin = i
                break
            
        for i in range(begin,len(self.dataset_cb)):
            if (self.dataset_cb[i].isChecked()):    
                end = i
            elif (not self.dataset_cb[i].isChecked()):
                break
            
        if (begin >= end):
            self.parent.statusBar().showMessage(self.tr("Cassette loop could not be added"))                
            self.accept()
            return
        
        if (not len(self.parent.cassetteloops_view.selectedIndexes())):
            # if nothing selected
            self.parent.cassette_loops.append([begin,end,no_cassettes,no_wafers])           
        else:
            row = self.parent.cassetteloops_view.selectedIndexes()[0].parent().row()
            self.parent.cassette_loops.insert(row,[begin,end,no_cassettes,no_wafers])

        self.parent.load_definition_cassetteloops(False)

        self.parent.statusBar().showMessage(self.tr("Cassette loop added"))                
        self.accept()