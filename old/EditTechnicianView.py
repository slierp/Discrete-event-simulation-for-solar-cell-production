# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from dialogs.TechnicianSettingsDialog import TechnicianSettingsDialog

class EditTechnicianView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)

        self.parent = _parent
        
        if (not len(self.parent.technicians_view.selectedIndexes())):
            # if nothing selected
            self.parent.statusBar().showMessage(self.tr("Please select position"))
        elif (self.parent.technicians_view.selectedIndexes()[0].parent().row() == -1):
            # if parent row is selected
            self.edit_technician()
        else: # if child row is selected
            self.parent.statusBar().showMessage(self.tr("No tool settings available"))

    def edit_technician(self):
        # start dialog to enable user to change settings        
        batchlocation_dialog = TechnicianSettingsDialog(self.parent)  
        batchlocation_dialog.setModal(True)
        batchlocation_dialog.show()         