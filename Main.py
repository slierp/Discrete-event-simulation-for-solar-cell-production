# -*- coding: utf-8 -*-
from __future__ import division
from RunSimulation import RunSimulation
import sys
import numpy #needed for PyInstaller (currently only because cPickle uses numpy)

from PyQt4 import QtCore, QtGui
from MainGui import MainGui
import Required_resources

def check_int(user_input):
    try:
        return int(user_input)
    except ValueError:
        print "Duration input not understood."
        exit()

if __name__ == "__main__":
    no_args = len(sys.argv)
    if no_args > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print "Solar cell production simulation"
            print "Running with no arguments will start graphical user interface"            
            print "Command-line usage: python " + sys.argv[0] + " file duration"
            print "Options:"
            print "--h, --help  : Print help message"
            print "file : .desc file containing simulation description"
            print "duration: simulation time in hours (1 hour by default)"
            exit()

    if no_args > 2:
        thread = RunSimulation(sys.argv[1],check_int(sys.argv[2]))
        thread.run()
    elif no_args > 1:
        thread = RunSimulation(sys.argv[1])  
        thread.run()
    else:
    
        app = QtGui.QApplication.instance()
        if not app:
            # if no other PyQt program is running (such as the IDE) create a new instance
            app = QtGui.QApplication(sys.argv)
               
        window = MainGui()
        window.show()
        app.exec_()
