# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer

class Buffer(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):    
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []      
        
        self.params = {}
        self.params['specification'] = "Buffer consists of:\n"
        self.params['specification'] += "- Input/output container\n"
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 50
        self.params['max_cassette_no_desc'] = "Number of cassette positions available"
        self.params['verbose'] = False
        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool"
        self.params.update(_params)
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [Buffer][" + self.params['name'] + "] Added a buffer location"
            self.output_text.sig.emit(string)
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.output = self.input

    def report(self):
        string = "[Buffer][" + self.params['name'] + "] Currently buffered: " + str(self.output.container.level)
        self.output_text.sig.emit(string)