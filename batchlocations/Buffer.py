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
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Buffer"];
                       A;
                       } """          
        
        self.params = {}
        
        self.params['specification'] = """
<h3>General description</h3>
A buffer is used to store wafers temporarily.\n
<h3>Description of the algorithm</h3>
TO BE ADDED\n
        """        
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 50
        self.params['max_cassette_no_desc'] = "Number of cassette positions available"
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
#        if (self.params['verbose']): #DEBUG
#            string = str(self.env.now) + " - [Buffer][" + self.params['name'] + "] Added a buffer location" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.output = self.input

    def report(self):
        string = "[Buffer][" + self.params['name'] + "] Currently buffered: " + str(self.output.container.level)
        self.output_text.sig.emit(string)
        
    def prod_volume(self):
        return self.output.container.level