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
A buffer is used to store cassettes temporarily.
The space available in the buffer can be configured.\n
<h3>Description of the algorithm</h3>
A buffer is not an active process.\n
        """
        
        self.params['name'] = ""
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['cassette_size_type'] = "configuration"
        self.params['max_cassette_no'] = 50
        self.params['max_cassette_no_desc'] = "Number of cassette positions available"
        self.params['max_cassette_no_type'] = "configuration"
        self.params.update(_params)
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.output = self.input

    def report(self):
        string = "[Buffer][" + self.params['name'] + "] Currently buffered: " + str(self.output.container.level)
        self.output_text.sig.emit(string)
        
    def prod_volume(self):
        return self.output.container.level