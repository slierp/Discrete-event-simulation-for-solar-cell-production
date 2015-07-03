# -*- coding: utf-8 -*-
from __future__ import division
from RunSimulation import RunSimulation
import sys
import numpy #needed for PyInstaller (currently only because cPickle uses numpy)

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
            print "usage: python " + sys.argv[0] + " file duration"
            print "Options:"
            print "--h, --help  : Print help message"
            print "file : .desc file containing simulation description"
            print "duration: simulation time in hours (1 hour by default)"
            exit()
    else:
        print "Please specify simulation description file."
        exit()

    if no_args > 2:
        thread = RunSimulation(sys.argv[1],check_int(sys.argv[2]))
    else:
        thread = RunSimulation(sys.argv[1])
    
    thread.run()
