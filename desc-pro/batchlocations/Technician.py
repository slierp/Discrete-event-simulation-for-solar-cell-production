# -*- coding: utf-8 -*-
from PyQt5 import QtCore

class Technician(QtCore.QObject):
    # Technician checks regularly whether he/she can perform maintenance on the tools it is responsible for
        
    def __init__(self, _env, _tools = None, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.tools = _tools
        self.utilization = []

        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
Technicians are responsible for maintaining a defined set tools and checks periodically if maintenance is required.
The technician will start the specified downtime procedure of each the tools and wait until it is done.
<h3>Description of the algorithm</h3>
There is one loop that describes the functionality of the technician.
The first step in this loop is to go over all the tools assigned to this technician and do the following:
<ol>
<li>Check if the tool is requesting a technician</li>
<li>If so, wait as long as the prescribed downtime duration and then restart the tool</li>
</ol>
\n
        """
        
        self.params['name'] = ""
        self.params['type'] = "Technician"
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between maintenance attempts (seconds)"        
        self.params.update(_params)
        
        self.transport_counter = 0
        self.start_time = -1
        self.idle_time = 0
            
        self.env.process(self.run())      

    def report(self):        
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append("n/a")
        
        util = 100-(100*self.idle_time/self.env.now)
        self.utilization.append(round(util,1))
            
        self.utilization.append(self.transport_counter)
    
    def run(self):

        wait_time = self.params['wait_time']
        continue_loop = False

        no_tools = len(self.tools)

        # Main loop to find tools that require maintenance
        while True:
            
            for i in range(no_tools):
                
                if self.tools[i].maintenance_needed:
                    
                    if self.tools[i].technician_resource.count:
                        continue

                    continue_loop = True
                    
                    with self.tools[i].technician_resource.request() as request:
                        yield request

                        self.tools[i].maintenance_needed = False
                        yield self.env.timeout(self.tools[i].downtime_duration)
                        yield self.tools[i].downtime_finished.succeed()
                        self.transport_counter += 1
                        
                        string = str(self.env.now) + " - [" + self.params['type'] + "][" + self.params['name'] + "] Maintenance event duration: "
                        string += str(round(self.tools[i].downtime_duration/60)) + " minutes"
                        #self.output_text.sig.emit(string)

            # if something useful was done then continue checking connections
            if (continue_loop):
                continue_loop = False
                continue
        
            yield self.env.timeout(wait_time)
            self.idle_time += wait_time        