# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO

Add a function to calculate the number of wafers in the line at certain intervals
- wafer.bin - wafer.source after a certain time has passed for stabilization
- report an average value + calculate the investment of product in the line at any given time
- Calculate average pass-through by checking how long it takes for that amount of wafers to pass

Tools/locations to be added
- cassette to cassette transfer
- buffers
- wafer inspection tool? Perhaps combined with waferunstacker

Implement STORES instead of more abstract CONTAINERS?
- make a 'cassette' class and put those in stores
- cassette can be full or empty, have different sizes
- make a 'wafer' class and store these in cassette class, among others
- wafers can be processed or not processed, have a tool feed-in and out time, idle_time etc.

The end program should have a function to measure the maximum throughput of each tool
So with ever-present wafer supply and removal.

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
        