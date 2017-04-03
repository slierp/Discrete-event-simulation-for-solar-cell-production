# -*- coding: utf-8 -*-
from PyQt5 import QtCore
#import simpy

class Technician(QtCore.QObject):
    # Technician checks regularly whether he/she can perform maintenance on the tools it is responsible for
        
    def __init__(self, _env, _batchconnections = None, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.batchconnections = _batchconnections
        self.utilization = []

        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
A technician functions... 
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "Technician"
        self.params.update(_params)
        
        self.transport_counter = 0
        self.start_time = -1
        self.idle_time = 0
            
#        self.env.process(self.run())      

    def report(self):        
        return