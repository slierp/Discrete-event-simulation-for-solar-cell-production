# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

"""

from __future__ import division
from PyQt4 import QtCore, QtGui
from MainGui import MainGui
import Required_resources
import sys

if __name__ == "__main__":      

    app = QtGui.QApplication.instance()
    if not app:
        # if no other PyQt program is running (such as the IDE) create a new instance
        app = QtGui.QApplication(sys.argv)
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Solar cell manufacturing simulation"
            print "Options:"
            print "--h, --help  : Help message"
            exit()
               
    window = MainGui()
    window.show()
    app.exec_()
        