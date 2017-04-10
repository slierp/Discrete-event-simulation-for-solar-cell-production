# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
import random, simpy

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
        self.params['type'] = "PlasmaEtcher"        
        self.params['stack_size'] = 500
        self.params['stack_size_desc'] = "Number of wafers in a single stack"
        self.params['stack_size_type'] = "configuration"
        self.params['process_time'] = 30
        self.params['process_time_desc'] = "Time for a single plasma etch process (minutes)"
        self.params['process_time_type'] = "process"

        self.params['mtbf'] = 1000
        self.params['mtbf_desc'] = "Mean time between failures (hours) (0 to disable function)"
        self.params['mtbf_type'] = "downtime"
        self.params['mttr'] = 60
        self.params['mttr_desc'] = "Mean time to repair (minutes) (0 to disable function)"
        self.params['mttr_type'] = "downtime"                   
                   
        self.params.update(_params)
        
        self.input = BatchContainer(self.env,"input",self.params['stack_size'],1)
        self.output = self.input
        
        self.production_volume = 0
        self.start_time = -1
        self.start = self.env.event()

        self.downtime_finished = None
        self.technician_resource = simpy.Resource(self.env,1)
        self.downtime_duration =  0
        self.maintenance_needed = False
        
        random.seed(42)
        self.mtbf_enable = False
        if (self.params['mtbf'] > 0) and (self.params['mttr'] > 0):
            self.next_failure = random.expovariate(1/(3600*self.params['mtbf']))
            self.mtbf_enable = True
        
        self.env.process(self.run())        

    def report(self):
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_hours = (self.env.now - self.start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0): 
            self.utilization.append(round(100*(self.production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)

        self.utilization.append(self.production_volume)
        
    def prod_volume(self):
        return self.production_volume

    def nominal_throughput(self):
        return self.params['stack_size']*60/self.params['process_time']

    def start_process(self):
        self.start.succeed()
        self.start = self.env.event() # make new event
        
    def run(self):
        process_time = self.params['process_time']
        stack_size = self.params['stack_size']
        first_run = True

        mtbf_enable = self.mtbf_enable
        if mtbf_enable:
            mtbf = 1/(3600*self.params['mtbf'])
            mttr = 1/(60*self.params['mttr'])
        
        while True:

            if mtbf_enable and self.env.now >= self.next_failure:
                with self.input.oper_resource.request() as request:
                    yield request
                    self.downtime_duration = random.expovariate(mttr)
                    #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF set failure - maintenance needed for " + str(round(self.downtime_duration/60)) + " minutes")
                    self.downtime_finished = self.env.event()
                    self.maintenance_needed = True                    
                    yield self.downtime_finished
                    self.next_failure = self.env.now + random.expovariate(mtbf)
                    #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF maintenance finished - next maintenance in " + str(round((self.next_failure - self.env.now)/3600)) + " hours")  
            
            yield self.start

            if first_run:
                self.start_time = self.env.now
                first_run = False
            
            with self.input.oper_resource.request() as request:
                yield request
                yield self.env.timeout(process_time*60)
                self.production_volume += stack_size
        
        