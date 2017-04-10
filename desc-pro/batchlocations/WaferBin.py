# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.CassetteContainer import CassetteContainer
import simpy

class WaferBin(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Bin"];
                       A -> B;                    
                       } """      
        
        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
WaferBin is an imaginary machine that accepts wafer cassettes and places them in an infinitely sized container.
The user can set a time period between attempts to place the cassettes into the container.\n
\n
<h3>Description of the algorithm</h3>
There is one simple loop that consists of two steps:
<ol>
<li>Check if the number of wafers at the input is at least that of a cassette. If so, place one cassette in the container.</li>
<li>Wait for a defined period of time</li>
</ol>
\n
        """         
        
        self.params['name'] = ""
        self.params['type'] = "WaferBin"        
        self.params['max_batch_no'] = 8
        self.params['max_batch_no_desc'] = "Number of input cassette positions"
        self.params['max_batch_no_type'] = "configuration"
        self.params['wait_time'] = 10
        self.params['wait_time_desc'] = "Wait period between wafer removal attempts (seconds)"
        self.params['wait_time_type'] = "automation"
                   
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)
            
#        string = str(self.env.now) + " - [" + self.params['type'] + "][" + self.params['name'] + "] Added a wafer bin" #DEBUG
#        self.output_text.sig.emit(string) #DEBUG
      
        self.input = CassetteContainer(self.env,"input",self.params['max_batch_no'])
        self.output = InfiniteContainer(self.env,"output")

        self.maintenance_needed = False
        
        self.env.process(self.run())

    def report(self):
        return

    def prod_volume(self):
        return self.output.container.level
        
    def run(self):
        wait_time = self.params['wait_time']
        cassette_size = self.params['cassette_size']
        
        while True:
            cassette = yield self.input.input.get() # receive cassette
            yield self.env.timeout(wait_time) # simulate time taken to perform action
            yield self.output.container.put(cassette_size) # put wafers into infinite output container
            yield self.input.output.put(cassette) # return empty cassette
            
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):
        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)                                       