# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer

class PlasmaEtcher(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):    
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []
        self.diagram = """blockdiag {       
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Etch station"];
                       A;
                       } """          
        
        self.params = {}
        
        self.params['specification'] = """
<h3>General description</h3>
A plasma etcher is used to apply edge isolation on a stack of wafers.
The size of the stack and the required process time can be configured.\n
<h3>Description of the algorithm</h3>
There is one container which acts as both input and output and there is one loop to simulate the machine.
The loop continuously checks if unprocessed wafers are available and if so, performs a delay to simulate the process.\n
        """
        
        self.params['name'] = ""
        self.params['stack_size'] = 400
        self.params['stack_size_desc'] = "Number of wafers in a single stack"
        self.params['stack_size_type'] = "configuration"
        self.params['process_time'] = 30
        self.params['process_time_desc'] = "Time for a single plasma etch process (minutes)"
        self.params['process_time_type'] = "process"        
        self.params.update(_params)
        
        self.input = BatchContainer(self.env,"input",self.params['stack_size'],1)
        self.output = self.input
        
        self.production_volume = 0
        self.start_time = -1
        
        self.env.process(self.run())        

    def report(self):
        self.utilization.append("PlasmaEtcher")
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0): 
            self.utilization.append(round(100*(self.production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)

        self.utilization.append(self.production_volume)
        
    def prod_volume(self):
        return self.output.container.level

    def nominal_throughput(self):
        return self.params['stack_size']*60/self.params['process_time']
        
    def run(self):
        process_time = self.params['process_time']
        stack_size = self.params['stack_size']
        process_finished = False
        first_run = True
        
        while True:
            
            if self.input.container.level and (not process_finished):
                # start process if stack available that has not been processed yet

                if first_run:
                    self.start_time = self.env.now
                    first_run = False
            
                with self.input.oper_resource.request() as request:
                    yield request
                    yield self.env.timeout(process_time*60)
                    process_finished = True
                    self.production_volume += stack_size
            
            if (not self.input.container.level) and process_finished:
                # update process status if no wafers available anymore
                process_finished = False
                
            yield self.env.timeout(1)
        
        