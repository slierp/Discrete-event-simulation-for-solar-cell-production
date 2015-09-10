# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer

"""

TODO

Build in mechanism to have a preference for moving full boats to loadstation for load-out; should yield more load-outs when the input stops temporarily

"""

class TubePECVD(QtCore.QObject):
        
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
                       C [label = "Tube PECVD", stacked];
                       D [label = "Cooldown shelves", stacked];
                       E [label = "Output"];
                       A -> B -> C -> D -> B;
                       C -> D [folded];
                       B -> E [folded];
                       group { B; E; }                    
                       group { C; D; }
                       } """       
        
        self.params = {}
        self.params['specification'] = "TubePECVD consists of:\n"
        self.params['specification'] += "- Input buffer\n"
        self.params['specification'] += "- Loadstation\n"
        self.params['specification'] += "- Process tubes\n"
        self.params['specification'] += "- Cooldown locations\n"
        self.params['specification'] += "- Output buffer"
        self.params['specification'] += "\n"
        self.params['specification'] += "Boats are loaded and unloaded with wafers in the loadstation. "
        self.params['specification'] += "Wafer loading is performed only if there are enough wafers available in the input buffer. "      
        self.params['specification'] += "There is a downtime procedure for coating runs that need to be done after "
        self.params['specification'] += "the required boat cleaning. The cleaning itself is done externally so it does not affect the throughput significantly.\n"

        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['batch_size'] = 294
        self.params['batch_size_desc'] = "Number of units in a single process batch"
        self.params['process_time'] = 35*60
        self.params['process_time_desc'] = "Time for a single process (seconds)"
        self.params['cool_time'] = 5*60
        self.params['cool_time_desc'] = "Time for a single cooldown (seconds)"

        self.params['runs_before_boatclean'] = 100
        self.params['runs_before_boatclean_desc'] = "Number of PECVD processes before boat needs to be cleaned"
        self.params['coating_run_duration'] = 75*60
        self.params['coating_run_duration_desc'] = "Time for a single PECVD coating run (seconds)"
        
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

        self.params['wait_time'] = 10
        self.params['wait_time_desc'] = "Wait period between boat transport attempts (seconds)"
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)        

        self.transport_counter = 0
        self.batches_loaded = 0
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        
#        if (self.params['verbose']): #DEBUG
#            string = str(self.env.now) + " - [TubePECVD][" + self.params['name'] + "] Added a tube PECVD" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        ### Add input and boat load/unload location ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ### Add boats ###
        self.boat = [] # container for keeping tracking of wafer count
        self.boat_runs = [] # keep track of number of runs
        self.boat_status = [] # 0 is unprocessed; 1 is processed; 2 is cooled down
        for i in range(self.params['no_of_boats']):
            self.boat.append(BatchContainer(self.env,"boat",self.params['batch_size'],1))
            self.boat_runs.append(0)
            self.boat_status.append(0)

        ### Add furnaces ###
        self.furnace = []
        self.furnace_status = []
        for i in range(self.params['no_of_processes']):
            self.furnace.append(-1) # -1 is empty; 0 and onwards is boat number
            self.furnace_status.append(0) # 0 is free; 1 is busy

        ### Add cooldowns ###
        self.cooldown = []
        self.cooldown_status = []
        for i in range(self.params['no_of_cooldowns']):
            self.cooldown.append(-1) # -1 is empty; 0 and onwards is boat number
            self.cooldown_status.append(0) # 0 is free; 1 is busy
            
        ### Add loadstation ###
        self.loadstation = -1  # -1 is empty; 0 and onwards is boat number
        self.loadstation_status = 0 # 0 is free; 1 is busy        
            
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])        
     
        ### Distribute boats ###
        no_boats = self.params['no_of_boats']

        if no_boats:
            self.loadstation = 0
            no_boats -= 1        
            
        if no_boats:
            for i in range(self.params['no_of_cooldowns']):
                self.cooldown[i] = i+1
                no_boats -= 1
                
                if not no_boats:
                    break
                
        if no_boats:
            for i in range(self.params['no_of_processes']):
                self.furnace[i] = i+self.params['no_of_cooldowns']+1
                no_boats -= 1
                
                if not no_boats:
                    break
     
        self.env.process(self.run_transport())   
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())

    def report(self):
        string = "[TubePECVD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)
        
#        self.utilization.append("TubePECVD")
#        self.utilization.append(self.params['name'])
#        self.utilization.append(self.nominal_throughput())
#        production_volume = self.transport_counter
#        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
#        
#        if (self.nominal_throughput() > 0) and (production_hours > 0):
#            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))        
#        else:
#            self.utilization.append(0)            
#        
#        for i in range(len(self.batchprocesses)):
#            self.utilization.append([self.batchprocesses[i].name,round(self.batchprocesses[i].idle_time(),1)])        

    def prod_volume(self):
        return self.transport_counter

    def run_cooldown(self,num):
        yield self.env.timeout(self.params['cool_time'])
        self.boat_status[self.cooldown[num]] = 2 # set status as cooled down
        self.cooldown_status[num] = 0 # set status as non-busy
        #print "Cooldown " + str(num) + " finished on boat " + str(self.cooldown[num])

    def run_process(self,num,normal_process=True):
        if normal_process:
            yield self.env.timeout(self.params['process_time'])
        else:
            yield self.env.timeout(self.params['coating_run_duration'])
        self.boat_runs[self.furnace[num]] += 1 # keep track of number of runs with this boat
        self.boat_status[self.furnace[num]] = 1 # set boat status as processed     
        self.furnace_status[num] = 0 # set status furnace as non-busy
        #print "Process " + str(num) + " finished on boat " + str(self.furnace[num])
        
    def run_transport(self):

        batch_size = self.params['batch_size']
        transfer0_time = self.params['transfer0_time']
        transfer1_time = self.params['transfer1_time']
        transfer2_time = self.params['transfer2_time']
        no_of_processes = self.params['no_of_processes']
        no_of_cooldowns = self.params['no_of_cooldowns']
        runs_before_boatclean = self.params['runs_before_boatclean']        
        wait_time = self.params['wait_time']

        while True:            
            for i in range(no_of_processes): # first check if we can move any batch from tube to cool_down
                if (not self.furnace_status[i]) and (not (self.furnace[i] == -1)): # if boat is available
                    for j in range(no_of_cooldowns): # check cooldown locations
                        if (not self.cooldown_status[j]) and (self.cooldown[j] == -1): # if empty
                            boat = self.furnace[i] # store boat number
                            self.furnace[i] = -1 # empty the furnace
                            yield self.env.timeout(transfer1_time) # wait for transfer
                            self.cooldown[j] = boat # enter boat into cooldown
                            self.cooldown_status[j] = 1 # cooldown is busy status
                            self.env.process(self.run_cooldown(j)) # start process for cooldown
                            #print "Moved boat " + str(boat) + " to cooldown"                            
                            break # discontinue search for free cooldown locations for this boat

            if (not self.loadstation_status) and (self.loadstation == -1): # if loadstation is not busy and empty
                for i in range(no_of_cooldowns): # check if we can move a boat from cooldown to loadstation (should be followed by a re-load if possible)
                    if (not self.cooldown_status[i]) and (not self.cooldown[i] == -1):
                        boat = self.cooldown[i] # store boat number
                        self.cooldown[i] = -1 # empty the cooldown
                        yield self.env.timeout(transfer2_time) # wait for transfer
                        self.loadstation = boat # enter boat into loadstation
                        #print "Moved boat " + str(boat) + " to loadstation"
                        
                        if self.boat[self.loadstation].container.level and (self.boat_status[self.loadstation] == 2): # if there are wafers in the boat and they have been processed
                            self.loadstation_status = 1 # set status as busy
                            yield self.load_out_start.succeed() # ask for load-out
                            self.load_out_start = self.env.event() # create new event
                            #print "Asked for load-out"
                        break # stop search for available boat to put into loadstation

            if (not self.loadstation_status) and (not (self.loadstation == -1)): # if loadstation is not busy and contains boat 
                if (self.boat_runs[self.loadstation] >= runs_before_boatclean): # if boat needs coating run
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.boat_runs[boat] = 0 # reset number of runs
                            self.env.process(self.run_process(i, False)) # start coating run for furnace
                            #print "Moved boat " + str(boat) + " to furnace for coating run"                            
                            break # discontinue search for a free furnace for this boat                    
                elif (not self.boat[self.loadstation].container.level) and (self.input.container.level >= batch_size): # if boat is empty and wafers available ask for load-in (and boat does not require)
                    self.loadstation_status = 1 # set status as busy
                    yield self.load_in_start.succeed()
                    self.load_in_start = self.env.event() # create new event                    
                    #print "Asked for load-in"
                elif self.boat[self.loadstation].container.level and (not self.boat_status[self.loadstation]): # if boat is full and has not been processed try to load to furnace
                    #print "Boat " + str(self.loadstation) + " in loadstation contains unprocessed wafers"
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.env.process(self.run_process(i)) # start process for furnace
                            #print "Moved boat " + str(boat) + " to furnace"                            
                            break # discontinue search for a free furnace for this boat
                                    
            yield self.env.timeout(wait_time)                        
            
    def run_load_in(self):
        no_loads = self.params['batch_size'] // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            yield self.load_in_start

            #print "Starting load-in"
            for i in range(no_loads):
                yield self.input.container.get(automation_loadsize)                
                yield self.env.timeout(automation_time)            
                yield self.boat[self.loadstation].container.put(automation_loadsize)
            
            self.boat_status[self.loadstation] = 0 # set boat status to unprocessed
            self.loadstation_status = 0 # set loadstation status to non-busy
            #print "Finished load-in for boat " + str(self.loadstation)

    def run_load_out(self):
        no_loads = self.params['batch_size'] // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
        
        while True:
            yield self.load_out_start
            
            #print "Starting load-out"
            for i in range(no_loads):
                yield self.boat[self.loadstation].container.get(automation_loadsize)                
                yield self.env.timeout(automation_time)             
                yield self.output.container.put(automation_loadsize)
                self.transport_counter += automation_loadsize
            
            self.loadstation_status = 0
            #print "Finished load-out for boat " + str(self.loadstation)

    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['no_of_processes']*3600/self.params['process_time'])
        throughputs.append(self.params['batch_size']*self.params['no_of_cooldowns']*3600/self.params['cool_time'])
        return min(throughputs)                