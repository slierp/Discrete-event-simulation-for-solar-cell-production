# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from dialogs.LineDiagramDialog import LineDiagramDialog

class LineDiagramView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent
        
        if (len(self.parent.batchlocations)) and (len(self.parent.locationgroups)):
            self.show_diagram()
        else:
            self.parent.statusBar().showMessage(self.tr("Please complete production line definition"))

    def show_diagram(self):        
        # start dialog to generate and show line diagram
        connection_dialog = LineDiagramDialog(self.parent)
        connection_dialog.setModal(True)
        connection_dialog.show()            