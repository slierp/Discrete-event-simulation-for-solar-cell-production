# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddTechnicianToolDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        
        self.parent = parent

        # find out which tool was selected
        self.row = self.parent.technicians_view.selectedIndexes()[0].parent().row()
        self.index = self.parent.technicians_view.selectedIndexes()[0].row()        
        
        self.setWindowTitle(self.tr("Add technician tools"))
        vbox = QtWidgets.QVBoxLayout()

        title_label = QtWidgets.QLabel(self.tr("Available tools:"))
        vbox.addWidget(title_label)

        self.tools_list = ['BatchClean','BatchTex','SingleSideEtch','TubeFurnace','IonImplanter',\
                      'WaferStacker','WaferUnstacker','PlasmaEtcher','TubePECVD','InlinePECVD','PrintLine','SpatialALD']

        self.dataset_cb = []
        self.dataset_tools = []
        for i, value in enumerate(self.parent.batchlocations):
            if value[0] in self.tools_list:
                item = value[0] + " " + value[1]['name']
                self.dataset_cb.append(QtWidgets.QCheckBox(item))
                self.dataset_tools.append(i)
                if i in self.parent.technicians[self.row][0]:
                    self.dataset_cb[-1].setChecked(True)

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
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumWidth(800)

    def read(self):
        # Add tools to technician
        self.parent.technicians[self.row][0] = []
        
        j = 0
        for i, value in enumerate(self.parent.batchlocations):
            if value[0] in self.tools_list:
                if self.dataset_cb[j].isChecked():
                    self.parent.technicians[self.row][0].append(self.dataset_tools[j])
                j += 1
        
        self.parent.technicians[self.row][0].sort()
        
        self.parent.load_definition_technicians(False)
        
        # re-expand the technican parent item
        index = self.parent.technicians_model.index(self.row, 0)
        self.parent.technicians_view.setExpanded(index, True)              
            
        self.parent.statusBar().showMessage("Technician tools updated") 
        
        self.accept()