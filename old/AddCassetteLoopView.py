# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from dialogs.AddCassetteLoopDialog import AddCassetteLoopDialog

class AddCassetteLoopView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        cassetteloops_dialog = AddCassetteLoopDialog(self.parent)
        cassetteloops_dialog.setModal(True)
        cassetteloops_dialog.show()                                   