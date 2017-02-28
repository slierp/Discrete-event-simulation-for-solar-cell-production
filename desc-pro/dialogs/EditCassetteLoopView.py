# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from dialogs.CassetteLoopSettingsDialog import CassetteLoopSettingsDialog

class EditCassetteLoopView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        if (not len(self.parent.cassetteloops_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select a cassette loop"))
            return
                
        row = self.parent.cassetteloops_view.selectedIndexes()[0].row()
        
        cassetteloops_dialog = CassetteLoopSettingsDialog(self.parent,row)
        cassetteloops_dialog.setModal(True)
        cassetteloops_dialog.show()                                   