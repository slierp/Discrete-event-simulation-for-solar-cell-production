# -*- coding: utf-8 -*-
from __future__ import division
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class TubePECVD(object):
        
    def __init__(self, _env, _output=None, _params = {}):
        self.env = _env
        self.output_text = _output
        self.utilization = []        
        
        self.params = {}
        self.params['specification'] = "TubePECVD consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Boat-load-unload container\n"
        self.params['specification'] += "- Process tubes\n"
        self.params['specification'] += "- Cooldown locations\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There are two transporters:\n"
        self.params['specification'] += "transport1: from load-in to boat-load-unload and from boat-load-unload to output\n"
        self.params['specification'] += "transport2: from boat-load-unload to tube process to cool-down to boat-load-unload\n"
        self.params['specification'] += "transport2 triggers transport1 when to do something (load or unload)\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The number of batches in the system is limited by the no_of_boats variable.\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "Unloading has priority as this enables you to start a new process (less idle time).\n"
        self.params['specification'] += "\n"        
        self.params['specification'] += "There is no tool downtime defined because boat cleaning does not impede "
        self.params['specification'] += "ongoing production, while the preventive maintenance needed is very infrequent."

        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['batch_size'] = 294
        self.params['batch_size_desc'] = "Number of units in a single process batch"
        self.params['process_time'] = 30*60
        self.params['process_time_desc'] = "Time for a single process (seconds)"
        self.params['cool_time'] = 10*60
        self.params['cool_time_desc'] = "Time for a single cooldown (seconds)"
        
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
        
        self.params['automation_loadsize'] = 21
        self.params['automation_loadsize_desc'] = "Number of units per loading/unloading automation cycle"
        self.params['automation_time'] = 10
        self.params['automation_time_desc'] = "Time for a single loading/unloading automation cycle (seconds)"

        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = "Wait period between boat transport attempts (seconds)"
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool"
        self.params.update(_params)        

        self.transport_counter = 0
        self.batches_loaded = 0
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.load_in_out_end = self.env.event()
        
        #if (self.params['verbose']):
        #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Added a tube PECVD"
        #    self.output_text.sig.emit(string)
        
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
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Add cooldown processes ###
        self.coolprocesses = []            
        for i in range(self.params['no_of_cooldowns']):
            process_params = {}
            process_params['name'] = "c" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['cool_time']
            process_params['verbose'] = self.params['verbose']
            self.coolprocesses.append(BatchProcess(self.env,self.output_text,process_params))            
            
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])        
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        #string = "[TubePECVD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        #self.output_text.sig.emit(string)      
        
        self.utilization.append("TubePECVD")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport_counter - self.output.container.level
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
        self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))        
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,round(self.batchprocesses[i].idle_time(),1)])        

    def run_transport(self):
        
        batchconnections = []
        j = 0
        for i in range(self.params['no_of_processes']*self.params['no_of_cooldowns']):
            if (i%self.params['no_of_processes'] == 0) & (i > 0):
                j += 1
                
            batchconnections.append([self.batchprocesses[i%self.params['no_of_processes']],self.coolprocesses[j]])
        
        while True:
            for i in range(len(batchconnections)):
                # first check if we can move any batch from tube to cool_down
                if (batchconnections[i][0].container.level > 0) & \
                        (batchconnections[i][1].container.level == 0) & \
                            batchconnections[i][0].process_finished:
                                        
                    with batchconnections[i][0].resource.request() as request_input, \
                        batchconnections[i][1].resource.request() as request_output: 
                        yield request_input                 
                        yield request_output

                        yield batchconnections[i][0].container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer1_time'])
                        yield batchconnections[i][1].container.put(self.params['batch_size'])

                        batchconnections[i][0].process_finished = 0
                        batchconnections[i][1].start_process()
                        
                        #if (self.params['verbose']):
                        #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Moved batch to cooldown"
                        #    self.output_text.sig.emit(string)

            for i in range(len(self.coolprocesses)):
                # check if we can unload a batch (should be followed by a re-load if possible)
                if (self.coolprocesses[i].container.level > 0) & \
                        (self.boat_load_unload.container.level == 0) & \
                            self.coolprocesses[i].process_finished:
                
                    with self.coolprocesses[i].resource.request() as request_input:
                        yield request_input

                        yield self.coolprocesses[i].container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer2_time'])
                        yield self.boat_load_unload.container.put(self.params['batch_size'])
                        
                        #if (self.params['verbose']):
                        #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Moved processed batch for load-out"
                        #    self.output_text.sig.emit(string)
                    
                        self.coolprocesses[i].process_finished = 0                    
                    
                        yield self.load_out_start.succeed()
                        yield self.load_in_out_end
                        self.load_out_start = self.env.event()                    
            
            if (self.batches_loaded < self.params['no_of_boats']) & (self.input.container.level >= self.params['batch_size']) & \
                    (self.boat_load_unload.container.level == 0):
                # ask for more wafers if there is a boat and wafers available
                yield self.load_in_start.succeed()
                yield self.load_in_out_end
                self.load_in_start = self.env.event() # make new event                

            for i in range(len(self.batchprocesses)):
                # check if we can load new wafers into a tube
                if (self.batchprocesses[i].container.level == 0) & \
                        (self.boat_load_unload.container.level == self.params['batch_size']):

                    with self.batchprocesses[i].resource.request() as request_output:                  
                        yield request_output
                        
                        yield self.boat_load_unload.container.get(self.params['batch_size'])
                        yield self.env.timeout(self.params['transfer0_time'])
                        yield self.batchprocesses[i].container.put(self.params['batch_size'])

                        self.batchprocesses[i].start_process()
                        
                        #if (self.params['verbose']):
                        #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Started a process"
                        #    self.output_text.sig.emit(string)
            
            yield self.env.timeout(self.params['wait_time'])                        
            
    def run_load_in(self):
        while True:
            yield self.load_in_start
            for i in range(self.params['batch_size'] // self.params['automation_loadsize']):
                yield self.env.timeout(self.params['automation_time'])
                yield self.input.container.get(self.params['automation_loadsize'])            
                yield self.boat_load_unload.container.put(self.params['automation_loadsize'])
            
            self.batches_loaded += 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event

            #if (self.params['verbose']):
            #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Loaded batch"
            #    self.output_text.sig.emit(string)

    def run_load_out(self):
        while True:
            yield self.load_out_start
            for i in range(self.params['batch_size'] // self.params['automation_loadsize']):
                yield self.env.timeout(self.params['automation_time']) 
                yield self.boat_load_unload.container.get(self.params['automation_loadsize']) 
                yield self.output.container.put(self.params['automation_loadsize'])
                self.transport_counter += self.params['automation_loadsize']
            
            self.batches_loaded -= 1
            yield self.load_in_out_end.succeed()
            self.load_in_out_end = self.env.event() # make new event            

            #if (self.params['verbose']):            
            #    string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Unloaded batch"
            #    self.output_text.sig.emit(string)

    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['no_of_processes']*3600/self.params['process_time'])
        throughputs.append(self.params['batch_size']*self.params['no_of_cooldowns']*3600/self.params['cool_time'])
        return min(throughputs)                