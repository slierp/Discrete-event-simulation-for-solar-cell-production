# -*- coding: utf-8 -*-
# runfile('file', wdir='dir',args='-i test.desc -d 24')

import sys, getopt
from PyQt5 import QtWidgets

from RunSimulation import RunSimulation
from MainGui import MainGui
import Required_resources

def check_number(user_input):
    try:
        float(user_input)
        return user_input
    except ValueError:
        print("Duration input not understood.")
        exit()

if __name__ == "__main__":
    inputfile = ''
    duration = 1
    profiling = False

    if(not len(sys.argv[1:])):
        app = QtWidgets.QApplication.instance()
        if not app:
            # if no other PyQt program is running (such as the IDE) create a new instance
            app = QtWidgets.QApplication(sys.argv)
    
        app.setStyle("windows")       
        window = MainGui()        
        window.show()
        app.exec_()
        sys.exit()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:d:p",["input_file=","duration=","profile"])
    except getopt.GetoptError:
        print("Solar cell production simulation program DescPro")
        print("Running with no arguments will start graphical user interface")
        print("Command-line usage: " + sys.argv[0] + " input_file duration")
        print("Options:")
        print("-h, --help: Print help message")
        print("-p, --profile: Enable profiling mode (output will be written to output.csv)")
        print("input_file: .desc file containing simulation description")
        print("duration: simulation time in hours (1 hour by default)")
        exit()
        
    profiling_mode = False
    
    for opt, arg in opts:
        if opt == '-h':
            print("Solar cell production simulation program DescPro")
            print("Running with no arguments will start graphical user interface")
            print("Command-line usage: " + sys.argv[0] + " input_file duration")
            print("Options:")
            print("-h, --help: Print help message")
            print("-p, --profile: Enable profiling mode (output will be written to output.csv)")
            print("file: .desc file containing simulation description")
            print("duration: simulation time in hours (1 hour by default)")
            sys.exit()
        elif opt in ("-i", "--input_file"):
            inputfile = arg
        elif opt in ("-d", "--duration"):
            duration = arg
        elif opt in ("-p", "--profile"):
            profiling_mode = True            

    thread = RunSimulation(inputfile,check_number(duration),profiling_mode)
    thread.run()
