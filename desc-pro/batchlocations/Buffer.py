# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.CassetteContainer import CassetteContainer
#import simpy

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
        """
        
        self.params['name'] = ""
        self.params['max_cassette_no'] = 50
        self.params['max_cassette_no_desc'] = "Number of cassette positions available"
        self.params['max_cassette_no_type'] = "configuration"
        self.params.update(_params)

        # stores cassette number references
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'],True)
        self.output = self.input
                                           
    def space_available_input(self,added_units):
        self.input.space_available_input(added_units)      

    def space_available_output(self,added_units):
        self.input.space_available_input(added_units)

    def report(self):
        return
        
    def prod_volume(self):
        return len(self.output.input.items)