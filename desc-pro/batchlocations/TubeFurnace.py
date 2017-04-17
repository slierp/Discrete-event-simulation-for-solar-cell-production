# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
import simpy, random

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
A tube furnace is used for high-temperature processes such as diffusion or annealing.
Wafers are first loaded into boats in the loadstation and then transferred to the tube furnaces where the process is performed.
When the processes are finished the boats are transferred to a cooldown shelf and then back to the loadstation for wafer load-out.
There is a downtime procedure available for preventive maintenance after a set number of process runs.
There is also a downtime procedure for performing a boat and tube cleaning process after a defined number of process runs on a boat, but this is not enabled by default.
<h3>Description of the algorithm</h3>
The main loop is primarily concerned with the boat transport inside the tool, as described in the list below:
<ol>
<li>Go into downtime mode if a set number of processes has been run and all wafers were loaded out</li>
<li>Try to move boat from furnace to cooldown; try full boats first</li>
<li>Try to move boat from cooldown to loadstation; try full boats first</li>
<li>Perform action on boat in loadstation depending on state of boat and wafers:</li>
<ol>
<li>Perform cleaning run on empty boat if boat has been used for a set number of times</li>
<li>Start wafer load-in if boat is empty and wafers are available, except if downtime is required</li>
<li>If boat is sitting idle and there are batches in the system that need to be loaded out, check idle time and move boat to furnace if it is too long</li>
<li>If boat is full and not yet processed, try to move it to a furnace for processing</li>
</ol></ol>
<p>The wafer loading and unloading actions are separate processes that are triggered by the main loop.
The actions themselves consists of a simple series of load/unload steps.
In each load/unload step the automation loadsize is transferred into or out of the boat in the loadstation with a set delay.
The process batch size therefore needs to be a multiple of the automation loadsize.</p>
        """

        self.params['name'] = ""
        self.params['type'] = "TubeFurnace"        
        self.params['batch_size'] = 6
        self.params['batch_size_desc'] = "Number of cassettes in a single process batch"
        self.params['batch_size_type'] = "configuration"
        self.params['process_time'] = 60
        self.params['process_time_desc'] = "Time for a single process (minutes)"
        self.params['process_time_type'] = "process"
        self.params['cool_time'] = 10
        self.params['cool_time_desc'] = "Time for a single cooldown (minutes)"
        self.params['cool_time_type'] = "process"

        self.params['runs_before_boatclean'] = 0
        self.params['runs_before_boatclean_desc'] = "Number of furnace process runs before boat needs to be cleaned (0 to disable function)"
        self.params['runs_before_boatclean_type'] = "downtime"
        self.params['coating_run_duration'] = 60
        self.params['coating_run_duration_desc'] = "Time for a single boat cleaning process (minutes)"
        self.params['coating_run_duration_type'] = "downtime"

        self.params['downtime_runs'] = 1000
        self.params['downtime_runs_desc'] = "Number of furnace processes before downtime of the whole tool (0 to disable function)"
        self.params['downtime_runs_type'] = "downtime"
        self.params['downtime_duration'] = 60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (minutes)"
        self.params['downtime_duration_type'] = "downtime"
        self.params['random_seed'] = 42        
        self.params['random_seed_type'] = "immutable"                     

        self.params['mtbf'] = 1000
        self.params['mtbf_desc'] = "Mean time between failures (hours) (0 to disable function)"
        self.params['mtbf_type'] = "downtime"
        self.params['mttr'] = 60
        self.params['mttr_desc'] = "Mean time to repair (minutes) (0 to disable function)"
        self.params['mttr_type'] = "downtime"
        
        self.params['no_of_processes'] = 5
        self.params['no_of_processes_desc'] = "Number of process locations in the tool"
        self.params['no_of_processes_type'] = "configuration"
        self.params['no_of_cooldowns'] = 4
        self.params['no_of_cooldowns_desc'] = "Number of cooldown locations in the tool"
        self.params['no_of_cooldowns_type'] = "configuration"
        
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        self.params['max_cassette_no_type'] = "configuration"
        
        self.params['no_of_boats'] = 7
        self.params['no_of_boats_desc'] = "Number of boats available"
        self.params['no_of_boats_type'] = "configuration"
        
        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = "Time for boat transfer from load-in to process tube (seconds)"
        self.params['transfer0_time_type'] = "automation"
        self.params['transfer1_time'] = 60
        self.params['transfer1_time_desc'] = "Time for boat transfer from process tube to cooldown (seconds)"
        self.params['transfer1_time_type'] = "automation"
        self.params['transfer2_time'] = 60
        self.params['transfer2_time_desc'] = "Time for boat transfer from cooldown to load-out (seconds)"
        self.params['transfer2_time_type'] = "automation"
        
        self.params['automation_loadsize'] = 50
        self.params['automation_loadsize_desc'] = "Number of units per loading/unloading automation cycle"
        self.params['automation_loadsize_type'] = "automation"
        self.params['automation_time'] = 10
        self.params['automation_time_desc'] = "Time for a single loading/unloading automation cycle (seconds)"
        self.params['automation_time_type'] = "automation"
        
        self.params['idle_boat_timeout'] = 300
        self.params['idle_boat_timeout_desc'] = "Time before idle boat in the loadstation is moved to furnace to enable continued load-out (seconds)"
        self.params['idle_boat_timeout_type'] = "automation"

        self.params['wait_time'] = 10
        self.params['wait_time_desc'] = "Wait period between boat transport attempts (seconds)"
        self.params['wait_time_type'] = "automation"
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        string = ""

        if self.output_text and self.params['cassette_size'] == -1:
            string += str(round(self.env.now,1)) + " [" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "Missing cassette loop information. "
        
        if self.params['cassette_size'] == -1:
            self.params['cassette_size'] = 100 

        if self.params['max_cassette_no'] < self.params['batch_size']:
            string += "[" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "WARNING: Input buffer is smaller than batch-size. Tool will not start. "

        if (not (self.output_text == None)) and (self.params['cassette_size'] % self.params['automation_loadsize']):
            string += "[" + self.params['type'] + "][" + self.params['name'] + "] "
            string += "WARNING: Automation loadsize is not a multiple of cassette size. Automation will not work. " 

        if len(string):
            self.output_text.sig.emit(string)

        self.transport_counter = 0
        self.batches_loaded = 0        
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.process_counter = 0      
        
        ### Add input and boat load/unload location ###        
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'])
        
        ### Add boats ###
        self.boat = [] # container for keeping tracking of wafer count
        self.boat_runs = [] # keep track of number of runs
        self.boat_status = [] # 0 is unprocessed; 1 is processed; 2 is cooled down
        for i in range(self.params['no_of_boats']):
            self.boat.append(BatchContainer(self.env,"boat",self.params['batch_size']*self.params['cassette_size'],1))
            self.boat_runs.append(0)
            self.boat_status.append(0)

        ### Add furnaces ###
        self.furnace = []
        self.furnace_status = []
        self.furnace_runs = []
        for i in range(self.params['no_of_processes']):
            self.furnace.append(-1) # -1 is empty; 0 and onwards is boat number
            self.furnace_status.append(0) # 0 is free; 1 is busy
            self.furnace_runs.append(0) # keep track of the number of runs performed in the furnace

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
        self.output = CassetteContainer(self.env,"output",self.params['max_cassette_no'])
     
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

        self.downtime_finished = None
        self.technician_resource = simpy.Resource(self.env,1)
        self.downtime_duration =  60*self.params['downtime_duration']
        self.maintenance_needed = False
        
        random.seed(self.params['random_seed'])
        
        self.mtbf_enable = False
        if (self.params['mtbf'] > 0) and (self.params['mttr'] > 0):
            self.next_failure = random.expovariate(1/(3600*self.params['mtbf']))
            self.mtbf_enable = True
        
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())
        self.env.process(self.run_transport()) # important not to trigger signal before starting load processes

    def report(self):        
        self.utilization.append(self.params['type'])
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport_counter
        production_hours = self.env.now/3600
        
        if (self.nominal_throughput() > 0) and (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput()))        
        else:
            self.utilization.append(0)            

        self.utilization.append(self.transport_counter)
        
        for i in range(self.params['no_of_processes']):
            util = 100*(self.furnace_runs[i]*60*self.params['process_time'])/self.env.now
            self.utilization.append(["Tube " + str(i),round(util)])

    def prod_volume(self):
        return self.transport_counter

    def run_cooldown(self,num):
        #print(str(self.env.now) + "- [" + self.params['type'] + "] Cooldown " + str(num) + " started on boat " + str(self.cooldown[num]))
        yield self.env.timeout(60*self.params['cool_time'])
        self.boat_status[self.cooldown[num]] = 2 # set status as cooled down
        self.cooldown_status[num] = 0 # set status as non-busy
        #print(str(self.env.now) + "- [" + self.params['type'] + "] Cooldown " + str(num) + " finished on boat " + str(self.cooldown[num]))

    def run_process(self,num,normal_process=True):
        #print(str(self.env.now) + "- [" + self.params['type'] + "] Process " + str(num) + " started on boat " + str(self.furnace[num]))

        if normal_process:
            yield self.env.timeout(60*self.params['process_time'])
            self.furnace_runs[num] += 1 # keep track of number of normal runs in this furnace
            self.process_counter += 1 # keep track of total number or process runs             
        else:
            yield self.env.timeout(60*self.params['coating_run_duration'])
  
        self.boat_runs[self.furnace[num]] += 1 # keep track of number of runs with this boat
        self.boat_status[self.furnace[num]] = 1 # set boat status as processed     
        self.furnace_status[num] = 0 # set status furnace as non-busy       
        #print(str(self.env.now) + "- [" + self.params['type'] + "] Process " + str(num) + " finished on boat " + str(self.furnace[num]))
        
    def run_transport(self):

        batch_size = self.params['batch_size']
        transfer0_time = self.params['transfer0_time']
        transfer1_time = self.params['transfer1_time']
        transfer2_time = self.params['transfer2_time']
        no_of_processes = self.params['no_of_processes']
        no_of_cooldowns = self.params['no_of_cooldowns']
        runs_before_boatclean = self.params['runs_before_boatclean']
        downtime_runs = self.params['downtime_runs']
        downtime_duration = self.params['downtime_duration']
        mtbf_enable = self.mtbf_enable
        if mtbf_enable:
            mtbf = 1/(3600*self.params['mtbf'])
            mttr = 1/(60*self.params['mttr'])
        wait_time = self.params['wait_time']
        idle_boat_timeout = self.params['idle_boat_timeout']
        idle_boat = 0

        while True:
            
            if (downtime_runs > 0) and (self.process_counter >= downtime_runs) and (self.batches_loaded == 0):
                # if downtime is needed and all batches have been unloaded, enter downtime
                #print(str(self.env.now) + "- [" + self.params['type'] + "] Run limit reached - Maintenance needed")
                self.downtime_duration = downtime_duration
                self.downtime_finished = self.env.event()
                self.maintenance_needed = True                    
                yield self.downtime_finished
                #print(str(self.env.now) + "- [" + self.params['type'] + "] Run limit reached - Maintenance finished")
                self.process_counter = 0 # reset total number of process runs
            
            if mtbf_enable and self.env.now >= self.next_failure:
                self.downtime_duration = random.expovariate(mttr)
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF set failure - maintenance needed for " + str(round(self.downtime_duration/60)) + " minutes")
                self.downtime_finished = self.env.event()
                self.maintenance_needed = True                    
                yield self.downtime_finished
                self.next_failure = self.env.now + random.expovariate(mtbf)
                #print(str(self.env.now) + "- [" + self.params['type'] + "] MTBF maintenance finished - next maintenance in " + str(round((self.next_failure - self.env.now)/3600)) + " hours")
            
            ### MOVE FROM FURNACE TO COOLDOWN ###
            for i in range(no_of_processes): # first check if we can move a full boat from tube to cooldown
                if (not self.furnace_status[i]) and (not (self.furnace[i] == -1)) and (self.boat[self.furnace[i]].container.level): # if full boat is available
                    for j in range(no_of_cooldowns): # check cooldown locations
                        if (not self.cooldown_status[j]) and (self.cooldown[j] == -1): # if empty
                            boat = self.furnace[i] # store boat number
                            #print(str(self.env.now) + "- [" + self.params['type'] + "] Move full boat " + str(boat) + " to cooldown " + str(j))
                            self.furnace[i] = -1 # empty the furnace
                            yield self.env.timeout(transfer1_time) # wait for transfer
                            self.cooldown[j] = boat # enter boat into cooldown
                            self.cooldown_status[j] = 1 # cooldown is busy status
                            self.env.process(self.run_cooldown(j)) # start process for cooldown
                            break # discontinue search for free cooldown locations for this boat

            for i in range(no_of_processes): # check if we can move an empty boat from tube to cooldown
                if (not self.furnace_status[i]) and (not (self.furnace[i] == -1)): # if boat is available
                    for j in range(no_of_cooldowns): # check cooldown locations
                        if (not self.cooldown_status[j]) and (self.cooldown[j] == -1): # if empty
                            boat = self.furnace[i] # store boat number
                            #print(str(self.env.now) + "- [" + self.params['type'] + "] Move empty boat " + str(boat) + " to cooldown " + str(j))
                            self.furnace[i] = -1 # empty the furnace
                            yield self.env.timeout(transfer1_time) # wait for transfer
                            self.cooldown[j] = boat # enter boat into cooldown
                            break # discontinue search for free cooldown locations for this boat

            ### MOVE FROM COOLDOWN TO LOADSTATION ###
            if (not self.loadstation_status) and (self.loadstation == -1) and (self.batches_loaded > 0): # if loadstation is not busy and empty and there are batches in the system
                # check if we can move a full boat from cooldown to loadstation; always proceed with load-out immediately after
                for i in range(no_of_cooldowns):
                    if (not self.cooldown_status[i]) and (not self.cooldown[i] == -1) and (self.boat[self.cooldown[i]].container.level):
                        boat = self.cooldown[i] # store boat number
                        #print(str(self.env.now) + "- [" + self.params['type'] + "] Move boat " + str(boat) + " to loadstation")
                        self.cooldown[i] = -1 # empty the cooldown
                        yield self.env.timeout(transfer2_time) # wait for transfer
                        self.loadstation = boat # enter boat into loadstation

                        #print(str(self.env.now) + "- [" + self.params['type'] + "] Ask for load-out for boat " + str(self.loadstation))                        
                        self.loadstation_status = 1 # set status as busy
                        yield self.load_out_start.succeed() # ask for load-out
                        self.load_out_start = self.env.event() # create new event
                        
                        break # stop search for available boat to put into loadstation
            
            if (not self.loadstation_status) and (self.loadstation == -1): # if loadstation is still not busy and empty
                # check if we can move an empty boat from cooldown to loadstation; do not proceed with load-in immediately after as there may be downtime planned
                for i in range(no_of_cooldowns): 
                    if (not self.cooldown_status[i]) and (not self.cooldown[i] == -1):
                        boat = self.cooldown[i] # store boat number
                        #print(str(self.env.now) + "- [" + self.params['type'] + "] Move boat " + str(boat) + " to loadstation")
                        self.cooldown[i] = -1 # empty the cooldown
                        yield self.env.timeout(transfer2_time) # wait for transfer
                        self.loadstation = boat # enter boat into loadstation                        
                        break # stop search for available boat to put into loadstation

            ### RUN LOAD-IN AND MOVE TO FURNACE ###
            if (not self.loadstation_status) and (not (self.loadstation == -1)): # if loadstation is not busy and contains boat 
                if (runs_before_boatclean > 0) and (self.boat_runs[self.loadstation] >= runs_before_boatclean): # if boat needs coating run
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            #print(str(self.env.now) + "- [" + self.params['type'] + "] Move boat " + str(boat) + " to furnace " + str(i) + " for cleaning run")
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.boat_runs[boat] = 0 # reset number of runs
                            self.env.process(self.run_process(i, False)) # start coating run for furnace
                            break # discontinue search for a free furnace for this boat                           
                elif (not self.boat[self.loadstation].container.level) and (len(self.input.input.items) >= batch_size) and ((downtime_runs == 0) or (self.process_counter <= downtime_runs)):
                    # if boat is empty and wafers are available ask for load-in, except if downtime is required
                    self.loadstation_status = 1 # set status as busy
                    #print(str(self.env.now) + "-" + "Ask for load-in for boat " + str(self.loadstation))
                    yield self.load_in_start.succeed()
                    self.load_in_start = self.env.event() # create new event                    
                elif (not self.boat[self.loadstation].container.level) and (self.batches_loaded > 0):
                    # if boat is empty and there are batches in the system check if the situation has been like this for a while; if so, try to move empty boat to furnace
                    if (idle_boat > 0) and ((self.env.now - idle_boat) >= idle_boat_timeout): # if we waited for new wafers for more than 5 minutes
                        #print(str(self.env.now) + "-" + "Try to move idle boat from loadstation to furnace")
                        for i in range(no_of_processes):
                            if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                                #print(str(self.env.now) + "- [" + self.params['type'] + "]Move idle boat " + str(self.loadstation) + " from loadstation to furnace " + str(i))                                
                                boat = self.loadstation # store boat number
                                self.loadstation = -1 # empty the loadstation                        
                                yield self.env.timeout(transfer0_time) # wait for transfer
                                self.furnace[i] = boat # put boat into furnace
                                break # discontinue search for a free furnace for this boat
                        idle_boat = 0
                    elif (idle_boat == 0):
                        #print(str(self.env.now) + "- [" + self.params['type'] + "]Boat "+ str(self.loadstation) + " is idle in loadstation")
                        idle_boat = self.env.now                        
                elif self.boat[self.loadstation].container.level and (not self.boat_status[self.loadstation]): # if boat is full and has not been processed then try to load to furnace
                    #print(str(self.env.now) + "- [" + self.params['type'] + "] Boat " + str(self.loadstation) + " in loadstation contains unprocessed wafers")
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            #print(str(self.env.now) + "-" + "Move boat " + str(boat) + " to furnace " + str(i))
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.env.process(self.run_process(i)) # start process for furnace
                            break # discontinue search for a free furnace for this boat
                                    
            yield self.env.timeout(wait_time)                        
            
    def run_load_in(self):
        cassette_size = self.params['cassette_size']
        no_loads = self.params['batch_size']*cassette_size // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
        wafer_counter = 0

        while True:
            yield self.load_in_start

            #print(str(self.env.now) + "- [" + self.params['type'] + "] Starting load-in")
            for i in range(no_loads):

                if not wafer_counter:

                    cassette = yield self.input.input.get()
                    wafer_counter = cassette_size
                    yield self.input.output.put(cassette)

                wafer_counter -= automation_loadsize                               
                yield self.env.timeout(automation_time)            
                yield self.boat[self.loadstation].container.put(automation_loadsize)                                        

            self.boat_status[self.loadstation] = 0 # set boat status to unprocessed
            self.batches_loaded += 1 # keep track of number of loads in the system
            self.loadstation_status = 0 # set loadstation status to non-busy
            #print(str(self.env.now) + "- [" + self.params['type'] + "] Finished load-in for boat " + str(self.loadstation))

    def run_load_out(self):
        cassette_size = self.params['cassette_size']
        no_loads = self.params['batch_size']*cassette_size // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']

        cassette = None
        wafer_counter = 0
        
        while True:
            yield self.load_out_start
            
            #print(str(self.env.now) + "- [" + self.params['type'] + "] Starting load-out")
            for i in range(no_loads):
                
                if not cassette:
                    cassette = yield self.output.input.get()
                    #print(self.params['type'] + " got new cassette")
                    
                yield self.boat[self.loadstation].container.get(automation_loadsize)
                wafer_counter += automation_loadsize
                yield self.env.timeout(automation_time)
                #print(self.params['type'] + " moved " + str(wafer_counter) + " wafers into cassette")
                
                if wafer_counter == cassette_size:
                    yield self.output.output.put(cassette)
                    cassette = None
                    wafer_counter = 0
                    self.transport_counter += cassette_size
            
            self.batches_loaded -= 1 # keep track of number of loads in the system
            self.loadstation_status = 0 # set loadstation status to non-busy
            #print(str(self.env.now) + "- [" + self.params['type'] + "] Finished load-out for boat " + str(self.loadstation))

    def nominal_throughput(self):
        batch_size = self.params['batch_size']
        cassette_size = self.params['cassette_size']
        no_of_processes = self.params['no_of_processes']
        no_of_cooldowns = self.params['no_of_cooldowns']
        process_time = self.params['process_time']
        cool_time = self.params['cool_time']
        
        throughputs = []        
        throughputs.append(batch_size*cassette_size*no_of_processes*3600/(60*process_time))
        throughputs.append(batch_size*cassette_size*no_of_cooldowns*3600/(60*cool_time))
        return min(throughputs)