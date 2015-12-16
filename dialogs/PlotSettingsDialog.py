# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

class PlotSettingsDialog(QtGui.QDialog):
    # Generates help document browser    
    
    def __init__(self, parent):
        super(QtGui.QDialog, self).__init__(parent)
        
        self.parent = parent       
        
        self.setWindowTitle(self.tr("Plot settings"))
        vbox = QtGui.QVBoxLayout()

        self.dataset_cb = []
        for i in range(len(self.parent.prod_rates_df.columns)):
            self.dataset_cb.append(QtGui.QCheckBox(str(i)))
            if i in self.parent.parent.plot_selection:
                self.dataset_cb[i].setChecked(True)

        for i in range(len(self.dataset_cb)):
            vbox.addWidget(self.dataset_cb[i])

        ### Buttonbox for ok ###
        hbox = QtGui.QHBoxLayout()
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        
    def read(self):
        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                if not i in self.parent.parent.plot_selection:
                    self.parent.parent.plot_selection.append(i)
            else:
                self.parent.parent.plot_selection = [x for x in self.parent.parent.plot_selection if x != i]

        self.parent.on_redraw()
        self.close()