# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from BatchlocationSettingsDialog import BatchlocationSettingsDialog

class OperatorSettingsDialog(BatchlocationSettingsDialog):

    def read(self):
        # read contents of each widget
        # update settings in self.operators[self.row] of parent
        new_params = {}
        for i in self.strings:
            new_params[str(i.objectName())] = str(i.text())

        for i in self.integers:
            new_params[str(i.objectName())] = int(i.text())

        for i in self.doubles:
            new_params[str(i.objectName())] = float(i.text())

        for i in self.booleans:
            new_params[str(i.objectName())] = i.isChecked()
        
        self.parent.operators[self.row][1].update(new_params)
        self.parent.load_definition_operators(False)

        # select row again after reloading operator definitions
        index = self.parent.operators_model.index(self.row, 0)
        self.parent.operators_view.setCurrentIndex(index)
        self.parent.statusBar().showMessage(self.tr("Operator settings updated"))
        self.accept()