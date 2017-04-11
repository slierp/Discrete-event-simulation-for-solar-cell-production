# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
from sys import platform as _platform

class CassetteLoopSettingsDialog(QtWidgets.QDialog):
    def __init__(self, _parent):

        super(QtWidgets.QDialog, self).__init__(_parent)

        self.parent = _parent
        self.row = -1
        self.cassette_loops = self.parent.cassetteloops_widget.cassette_loops
        self.statusbar = self.parent.statusBar()          

        self.input_types = self.parent.cassetteloops_widget.input_types
        self.output_types = self.parent.cassetteloops_widget.output_types
        self.load_definition = self.parent.cassetteloops_widget.load_definition
        self.locationgroups = self.parent.tools_widget.locationgroups
        self.batchlocations = self.parent.tools_widget.batchlocations
        self.view = self.parent.cassetteloops_view        
        self.model = self.parent.cassetteloops_model
        self.group_names = self.parent.tools_widget.group_names

        if len(self.view.selectedIndexes()): # widget only allows selecting loops, not tools
            self.row = self.view.selectedIndexes()[0].row()
            
        self.setWindowTitle(self.tr("Cassette loop settings"))

        if not self.row == -1: # if position selected, use that cassette loop
            self.cassette_loop = self.cassette_loops[self.row]
        else: # default cassette loop
            transport_time = 60 # default duration for cassette return to source
            time_per_unit = 10 # default additional duration for each cassette
            min_units = 1 # default minimum number of cassettes for return transport
            max_units = 99 # default maximum number of cassettes for return transport

            self.cassette_loop = [-1,-1,50,100,transport_time,time_per_unit,min_units,max_units]

        self.show_positions = False
        if self.cassette_loop[0] == -1:
            self.show_positions = True
            
        tabwidget = QtWidgets.QTabWidget()

        ### Loop positions tab ###
        if self.show_positions:
            
            vbox = QtWidgets.QVBoxLayout()

            ## Beginning of loop ###
            hbox = QtWidgets.QHBoxLayout()            
            begin_label = QtWidgets.QLabel(self.tr("Begin positions:"))
            hbox.addWidget(begin_label)
        
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
            
            hbox.addWidget(self.combo_begin)
            hbox.addStretch(1)                 
            vbox.addLayout(hbox)            

            ### End of loop ###
            hbox = QtWidgets.QHBoxLayout()
            end_label = QtWidgets.QLabel(self.tr("End positions:"))
            hbox.addWidget(end_label)

            self.combo_end = QtWidgets.QComboBox(self)
            
            self.end_positions = []
        
            hbox.addWidget(self.combo_end)
            hbox.addStretch(1)                 
            vbox.addLayout(hbox)
            vbox.addStretch(1)            

            self.find_end_positions()

            generic_widget_positions = QtWidgets.QWidget()
            generic_widget_positions.setLayout(vbox)
            tabwidget.addTab(generic_widget_positions, "Loop positions")
        
        ### Settings tab ###
        vbox = QtWidgets.QVBoxLayout()            

        hbox = QtWidgets.QHBoxLayout()
        text = "Number of cassettes in loop"
        label = QtWidgets.QLabel(text)
        self.spinbox0 = QtWidgets.QSpinBox()
        self.spinbox0.setAccelerated(True)
        self.spinbox0.setMaximum(999)
        self.spinbox0.setMinimum(1)
        self.spinbox0.setValue(self.cassette_loop[2])
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
        self.spinbox1.setValue(self.cassette_loop[3])
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
        self.spinbox2.setValue(self.cassette_loop[4])
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
        self.spinbox3.setValue(self.cassette_loop[5])
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
        self.spinbox4.setValue(self.cassette_loop[6])
        label.setToolTip(text)
        self.spinbox4.setToolTip(text)
        hbox.addWidget(self.spinbox4)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hard_limit_check = False
        # if not integer then it is a hard transport limit
        if (self.cassette_loop[6] % 1) > 0:
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
        self.spinbox5.setValue(self.cassette_loop[7])
        label.setToolTip(text)
        self.spinbox5.setToolTip(text)
        hbox.addWidget(self.spinbox5)  
        hbox.addWidget(label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        if not self.show_positions:
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

        generic_widget_settings = QtWidgets.QWidget()
        generic_widget_settings.setLayout(vbox)
        tabwidget.addTab(generic_widget_settings, "Settings")

        ### Description tab ###
        vbox_description = QtWidgets.QVBoxLayout() # vbox for description elements        
       
        description = """
<h3>General description</h3>
A cassette loop defines a list of tools that share the same set of cassettes.
The first tool in the list will receive empty cassettes from the cassette source buffer
and after passing through all the tools in the list the cassettes will be returned to the buffer.
<p>
When adding a new cassette loop or when editing a loop with no tools this dialog will allow you to select
the begin and end positions of the loop. The tools that can be selected as a begin or
are pre-defined by the program, based on the type of input/output buffers that the tools can have.
A batch texturing tool for example always puts out the same cassettes as it receives
so it cannot serve as a begin or end position of a cassette loop.
</p>
\n
        """        
        
        hbox = QtWidgets.QHBoxLayout()           
        browser = QtWidgets.QTextBrowser()
        browser.insertHtml(description)
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

    def switch_boolean(self, event):
        # function for making QLabel near checkbox clickable
        self.boolean.setChecked(not self.boolean.isChecked())

    def switch_hard_limit(self, event):
        # function for making QLabel near checkbox clickable
        self.hard_limit_boolean.setChecked(not self.hard_limit_boolean.isChecked())

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

        no_cassettes = int(self.spinbox0.text())
        no_wafers = int(self.spinbox1.text())
        transport_time = int(self.spinbox2.text())
        time_per_unit = int(self.spinbox3.text())
        min_units = int(self.spinbox4.text())        
        if self.hard_limit_boolean.isChecked(): # change value slightly to convey hard limit setting      
            min_units += 0.1       
        max_units = int(self.spinbox5.text())
        
        if self.show_positions:
            # add loop or update existing loop if one was selected
            
            begin_index = self.combo_begin.currentIndex()
            
            if begin_index == -1:
                self.statusbar.showMessage(self.tr("Cassette loop could not be added"),3000)
                self.accept()
                return                
            
            begin = self.begin_positions[begin_index]
        
            end = self.combo_end.currentIndex()
    
            if end == -1:
                self.statusbar.showMessage(self.tr("Cassette loop could not be added"),3000)
                self.accept()
                return
        
            end = self.end_positions[end]


            if not self.row == -1:
                self.cassette_loops[self.row][0] = begin
                self.cassette_loops[self.row][1] = end
                self.cassette_loops[self.row][2] = no_cassettes
                self.cassette_loops[self.row][3] = no_wafers
                self.cassette_loops[self.row][4] = transport_time
                self.cassette_loops[self.row][5] = time_per_unit
                self.cassette_loops[self.row][6] = min_units
                self.cassette_loops[self.row][7] = max_units
                message = self.tr("Cassette loop settings updated")
            else:
                cassette_loop = []
                cassette_loop.append(begin)
                cassette_loop.append(end)
                cassette_loop.append(no_cassettes)
                cassette_loop.append(no_wafers)
                cassette_loop.append(transport_time)
                cassette_loop.append(time_per_unit)
                cassette_loop.append(min_units)
                cassette_loop.append(max_units)                
                self.cassette_loops.append(cassette_loop)
                message = self.tr("Cassette loop added")
            
            self.load_definition(False)
            
            self.statusbar.showMessage(message,3000)                
            self.accept()
        
        else:
            # update settings only
            # read contents of each widget
            if self.boolean.isChecked():
                for i in range(len(self.cassette_loops)):
                    self.cassette_loops[i][2] = no_cassettes
                    self.cassette_loops[i][3] = no_wafers
                    self.cassette_loops[i][4] = transport_time
                    self.cassette_loops[i][5] = time_per_unit               
                    self.cassette_loops[i][6] = min_units
                    self.cassette_loops[i][7] = max_units
                message = self.tr("Settings for all cassette loops updated")
            else:
                self.cassette_loops[self.row][2] = no_cassettes
                self.cassette_loops[self.row][3] = no_wafers
                self.cassette_loops[self.row][4] = transport_time
                self.cassette_loops[self.row][5] = time_per_unit
                self.cassette_loops[self.row][6] = min_units
                self.cassette_loops[self.row][7] = max_units
                message = self.tr("Cassette loop settings updated")
    
            self.statusbar.showMessage(message,3000)                
            self.accept()