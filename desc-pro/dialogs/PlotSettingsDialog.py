# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

class PlotSettingsDialog(QtWidgets.QDialog):
    # Generates help document browser    
    
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        
        self.parent = parent       
        
        self.setWindowTitle(self.tr("Plot settings"))
        vbox = QtWidgets.QVBoxLayout()

        self.dataset_cb = []
        for i in range(len(self.parent.prod_rates_df.columns)):
            self.dataset_cb.append(QtWidgets.QCheckBox(self.parent.prod_rates_df.iloc[:,i].name))
            if i in self.parent.parent.plot_selection:
                self.dataset_cb[i].setChecked(True)

        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()

        for i in range(len(self.dataset_cb)):
            self.dataset_cb[i].setMinimumWidth(200) # prevent obscured text
            checkbox_vbox.addWidget(self.dataset_cb[i])

        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)

        ### Buttonbox for ok ###
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumWidth(800)        
        
    def read(self):
        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                if not i in self.parent.parent.plot_selection:
                    self.parent.parent.plot_selection.append(i)
            else:
                self.parent.parent.plot_selection = [x for x in self.parent.parent.plot_selection if x != i]

        self.parent.on_redraw()
        self.close()