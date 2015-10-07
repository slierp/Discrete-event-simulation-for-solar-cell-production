# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class TubeFurnace(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []
        self.diagram = """blockdiag {     
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       default_group_color = none               
                       A [label = "Input"];
                       B [label = "Load station"];
                       C [label = "Tube furnaces", stacked];
                       D [label = "Cooldown shelves", stacked];
                       E [label = "Output"];
                       A -> B -> C -> D -> B;
                       C -> D [folded];
                       B -> E [folded];
                       group { B; E; }                    
                       group { C; D; }
                       } """       
        
        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
A tube furnace is used for high-temperature processes such as diffusion.
Tool downtime is defined as a procedure where the whole tool is put offline for a short period during which preventive maintenance is performed.\n
<h3>Description of the algorithm</h3>
TO BE ADDED. The number of batches in the system is limited by the no_of_boats variable.\n
        """

        self.params['name'] = ""
        self.params['batch_size'] = 500
        self.params['batch_size_desc'] = "Number of units in a single process batch"
        self.params['process_time'] = 60*60
        self.params['process_time_desc'] = "Time for a single process (seconds)"
        self.params['cool_time'] = 10*60
        self.params['cool_time_desc'] = "Time for a single cooldown (seconds)"

        self.params['downtime_runs'] = 1000
        self.params['downtime_runs_desc'] = "Number of furnace processes before downtime"
        self.params['downtime_duration'] = 60*60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (seconds)"
        
        self.params['no_of_processes'] = 4
        self.params['no_of_processes_desc'] = "Number of process locations in the tool"
        self.params['no_of_cooldowns'] = 3
        self.params['no_of_cooldowns_desc'] = "Number of cooldown locations in the tool"
        
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 5
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        
        self.params['no_of_boats'] = 6
        self.params['no_of_boats_desc'] = "Number of boats available"
        
        self.params['transfer0_time'] = 90
        self.params['transfer0_time_desc'] = "Time for boat transfer from load-in to process tube (seconds)"
        self.params['transfer1_time'] = 90
        self.params['transfer1_time_desc'] = "Time for boat transfer from process tube to cooldown (seconds)"
        self.params['transfer2_time'] = 90
        self.params['transfer2_time_desc'] = "Time for boat transfer from cooldown to load-out (seconds)"
        
        self.params['automation_loadsize'] = 50
        self.params['automation_loadsize_desc'] = "Number of units per loading/unloading automation cycle"
        self.params['automation_time'] = 30
        self.params['automation_time_desc'] = "Time for a single loading/unloading automation cycle (seconds)"

        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between boat transport attempts (seconds)"
        
        self.params.update(_params)        

        self.transport_counter = 0
        self.batches_loaded = 0
        self.process_counter = 0        
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.load_in_out_end = self.env.event()
        
        ### Add input and boat load/unload location ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.boat_load_unload = BatchContainer(self.env,"boat_load_unload",self.params['batch_size'],1)

        ### Add batch processes ###
        self.batchprocesses = [] 
        for i in range(self.params['no_of_processes']):
            process_params = {}
            process_params['name'] = "t" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['process_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Add cooldown processes ###
        self.coolprocesses = []            
        for i in range(self.params['no_of_cooldowns']):
            process_params = {}
            process_params['name'] = "c" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['cool_time']
            self.coolprocesses.append(BatchProcess(self.env,self.output_text,process_params))            
            
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])        
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        string = "[TubeFurnace][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)        

        self.utilization.append("TubeFurnace")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport_counter
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)            
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,round(self.batchprocesses[i].idle_time(),1)])

    def prod_volume(self):
        return self.transport_counter

    def run_transport(self):
        
        batchconnections = []
        j = 0
        for i in range(self.params['no_of_processes']*self.params['no_of_cooldowns']):
            if (i%self.params['no_of_processes'] == 0) & (i > 0):
                j += 1
                
            batchconnections.append([self.batchprocesses[i%self.params['no_of_processes']],self.coolprocesses[j]])
        
        downtime_runs = self.params['downtime_runs']
        downtime_duration = self.params['downtime_duration']
        batch_size = self.params['batch_size']
        transfer0_time = self.params['transfer0_time']
        transfer1_time = self.params['transfer1_time']
        transfer2_time = self.params['transfer2_time']
        no_of_boats = self.params['no_of_boats']
        wait_time = self.params['wait_time']
        
        while True:
            if (downtime_runs > 0) & (self.process_counter >= downtime_runs) & \
                (self.batches_loaded == 0):
                    # if downtime is needed and all batches have been unloaded, enter downtime
                    yield self.env.timeout(downtime_duration)
                    self.process_counter = 0
                    
                    string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] End downtime"
                    self.output_text.sig.emit(string)
            
            for i in range(len(batchconnections)):
                # first check if we can move any batch from tube to cool_down
                if (batchconnections[i][0].container.level > 0) & \
                        (batchconnections[i][1].container.level == 0) & \
                            batchconnections[i][0].process_finished:
                                        
                    with batchconnections[i][0].resource.request() as request_input, \
                        batchconnections[i][1].resource.request() as request_output: 
                        yield request_input                 
                        yield request_output

                        yield batchconnections[i][0].container.get(batch_size)
                        yield self.env.timeout(transfer1_time)
                        yield batchconnections[i][1].container.put(batch_size)

                        batchconnections[i][0].process_finished = 0
                        batchconnections[i][1].start_process()
                        
#                        if (verbose): #DEBUG
#                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Moved batch to cooldown" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG

            for i in range(len(self.coolprocesses)):
                # check if we can unload a batch (should be followed by a re-load if possible)
                if (self.coolprocesses[i].container.level > 0) & \
                        (self.boat_load_unload.container.level == 0) & \
                            self.coolprocesses[i].process_finished:
                
                    with self.coolprocesses[i].resource.request() as request_input:
                        yield request_input

                        yield self.coolprocesses[i].container.get(batch_size)
                        yield self.env.timeout(transfer2_time)
                        yield self.boat_load_unload.container.put(batch_size)
                        
#                        if (verbose): #DEBUG
#                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Moved processed batch for load-out" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG
                    
                        self.coolprocesses[i].process_finished = 0                    
                    
                        yield self.load_out_start.succeed()
                        yield self.load_in_out_end
                        self.load_out_start = self.env.event()                    

            if (downtime_runs > 0) & (self.process_counter >= downtime_runs):
                # do not perform load-in if machine needs to enter downtime
                pass            
            elif (self.batches_loaded < no_of_boats) & (self.input.container.level >= batch_size) & \
                    (self.boat_load_unload.container.level == 0):
                # ask for more wafers if there is a boat and wafers available
                yield self.load_in_start.succeed()
                yield self.load_in_out_end
                self.load_in_start = self.env.event() # make new event                

            for i in range(len(self.batchprocesses)):
                # check if we can load new wafers into a tube
                if (self.batchprocesses[i].container.level == 0) & \
                        (self.boat_load_unload.container.level == batch_size):

                    with self.batchprocesses[i].resource.request() as request_output:                  
                        yield request_output
                        
                        yield self.boat_load_unload.container.get(batch_size)
                        yield self.env.timeout(transfer0_time)
                        yield self.batchprocesses[i].container.put(batch_size)

                        self.batchprocesses[i].start_process()
                        self.process_counter += 1
                        
#                        if (verbose): #DEBUG
#                            string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Started a process" #DEBUG
#                            self.output_text.sig.emit(string) #DEBUG
            
            yield self.env.timeout(wait_time)                        
            
    def run_load_in(self):
        no_loads = self.params['batch_size'] // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            yield self.load_in_start
            for i in range(no_loads):
                yield self.env.timeout(automation_time)
                yield self.input.container.get(automation_loadsize)            
                yield self.boat_load_unload.container.put(automation_loadsize)
            
            self.batches_loaded += 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event

#            if (verbose): #DEBUG
#                string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Loaded batch" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG

    def run_load_out(self):
        no_loads = self.params['batch_size'] // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            yield self.load_out_start
            for i in range(no_loads):
                yield self.env.timeout(automation_time) 
                yield self.boat_load_unload.container.get(automation_loadsize) 
                yield self.output.container.put(automation_loadsize)
                self.transport_counter += automation_loadsize
            
            self.batches_loaded -= 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event            

#            if (verbose): #DEBUG
#                string = str(self.env.now) + " - [TubeFurnace][" + self.params['name'] + "] Unloaded batch" #DEBUG
#                self.output_text.sig.emit(string) #DEBUG
        
    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['no_of_processes']*3600/self.params['process_time'])
        throughputs.append(self.params['batch_size']*self.params['no_of_cooldowns']*3600/self.params['cool_time'])
        return min(throughputs)                 