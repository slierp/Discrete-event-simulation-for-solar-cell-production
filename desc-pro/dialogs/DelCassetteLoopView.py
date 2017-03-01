# -*- coding: utf-8 -*-
from PyQt5 import QtCore

class DelCassetteLoopView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        if (not len(self.parent.cassetteloops_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select a cassette loop"))
            return
                
        row = self.parent.cassetteloops_view.selectedIndexes()[0].row()
        del self.parent.cassette_loops[row]

        self.parent.load_definition_cassetteloops(False)

        self.parent.statusBar().showMessage(self.tr("Cassette loop removed"))