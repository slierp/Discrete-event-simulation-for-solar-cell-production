# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddCassetteLoopDialog(QtWidgets.QDialog):
    def __init__(self, _parent):

        super(QtWidgets.QDialog, self).__init__(_parent)

        self.parent = _parent
        self.cassette_loops = self.parent.cassetteloops_widget.cassette_loops
        self.input_types = self.parent.cassetteloops_widget.input_types
        self.output_types = self.parent.cassetteloops_widget.output_types
        self.load_definition = self.parent.cassetteloops_widget.load_definition
        self.locationgroups = self.parent.tools_widget.locationgroups
        self.batchlocations = self.parent.tools_widget.batchlocations
        self.view = self.parent.cassetteloops_view        
        self.model = self.parent.cassetteloops_model
        self.group_names = self.parent.tools_widget.group_names
        self.statusbar = self.parent.statusBar()        
        
        self.setWindowTitle(self.tr("Add cassette loop"))
        vbox = QtWidgets.QVBoxLayout()

        ## Beginning of loop ###
        begin_label = QtWidgets.QLabel(self.tr("Begin positions:"))
        vbox.addWidget(begin_label)
        
        # remove groups already allocated in other cassette loops
        unavailable_groups = []

        for i in range(len(self.cassette_loops)):
            for j in range(self.cassette_loops[i][0],self.cassette_loops[i][1]):
                unavailable_groups.append(j)

        # find locationgroups where all tools have a dual cassette output buffer
        self.begin_positions = []

        for i in range(len(self.locationgroups)-1):
            suitable = True
            for j in range(len(self.locationgroups[i])):
                name = self.batchlocations[self.locationgroups[i][j]][0]
                    
                if not 3 in self.output_types[name]:
                    suitable = False
                    
            if suitable and not i in unavailable_groups:
                self.begin_positions.append(i)

        self.combo_begin = QtWidgets.QComboBox(self)
        
        for i in self.begin_positions:
            name = self.group_names[self.batchlocations[self.locationgroups[i][0]][0]]
            self.combo_begin.addItem(name)

        self.combo_begin.currentIndexChanged.connect(self.find_end_positions)
        vbox.addWidget(self.combo_begin)

        ### End of loop ###
        end_label = QtWidgets.QLabel(self.tr("End positions:"))
        vbox.addWidget(end_label)

        self.combo_end = QtWidgets.QComboBox(self)

        self.end_positions = []
        
        vbox.addWidget(self.combo_end)

        self.find_end_positions()

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft) 
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def find_end_positions(self):
        self.combo_end.clear()
        self.end_positions = []
        
        begin = self.combo_begin.currentIndex()
        
        if begin == -1:
            return
        
        begin = self.begin_positions[begin]

        # remove groups already allocated in other cassette loops
        unavailable_groups = []

        for i in range(len(self.cassette_loops)):
            for j in range(self.cassette_loops[i][0],self.cassette_loops[i][1]):
                if j > begin:
                    for k in range(j+1,len(self.locationgroups)):
                        unavailable_groups.append(k)

        # find suitable end groups
        for i in range(begin+1,len(self.locationgroups)):

            suitable = True
            stop_search = False
            for j in range(len(self.locationgroups[i])):
                name = self.batchlocations[self.locationgroups[i][j]][0]
                
                if not 3 in self.input_types[name]:
                    suitable = False
                
                if not 2 in self.input_types[name] or 1 in self.input_types[name]:
                    stop_search = True
            
            if suitable and not i in unavailable_groups:
                self.end_positions.append(i)

            if stop_search:
                break

        for i in self.end_positions:
            name = self.group_names[self.batchlocations[self.locationgroups[i][0]][0]]
            self.combo_end.addItem(name)

    def read(self):

        begin = self.begin_positions[self.combo_begin.currentIndex()]
        
        end = self.combo_end.currentIndex()
    
        if end == -1:
            self.statusbar.showMessage(self.tr("Cassette loop could not be added"))
            self.accept()
            return
        
        end = self.end_positions[end]

        transport_time = 60 # default duration for cassette return to source
        time_per_unit = 10 # default additional duration for each cassette
        min_units = 1 # default minimum number of cassettes for return transport
        max_units = 99 # default maximum number of cassettes for return transport

        self.cassette_loops.append([begin,end,50,100,transport_time,time_per_unit,min_units,max_units])
        self.load_definition(False)

        self.statusbar.showMessage(self.tr("Cassette loop added"))                
        self.accept()