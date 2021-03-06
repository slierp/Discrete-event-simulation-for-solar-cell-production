# -*- coding: utf-8 -*-
# runfile('file', wdir='dir',args='-i test.desc -d 24')

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

from MainGui import MainGui
import Required_resources

if __name__ == "__main__":

    app = QtWidgets.QApplication.instance()
    if not app:
        # if no other PyQt program is running (such as the IDE) create a new instance
        app = QtWidgets.QApplication(sys.argv)
           
    app.setStyle("Fusion")

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(200,201,209))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255,255,255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(200,201,209))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(200,201,209))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(255,79,0))
    app.setPalette(palette)
    
    window = MainGui()        
    window.show()
    app.exec_()
    sys.exit()
