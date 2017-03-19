# -*- coding: utf-8 -*-
# runfile('file', wdir='dir',args='-i test.desc -d 24')

import sys
from PyQt5 import QtWidgets

from MainGui import MainGui
import Required_resources

if __name__ == "__main__":

    app = QtWidgets.QApplication.instance()
    if not app:
        # if no other PyQt program is running (such as the IDE) create a new instance
        app = QtWidgets.QApplication(sys.argv)
    
    app.setStyle("windows")       
    window = MainGui()        
    window.show()
    app.exec_()
    sys.exit()
