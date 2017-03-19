# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchContainer import BatchContainer
from batchlocations.CassetteContainer import CassetteContainer
from batchlocations.TubeFurnace import TubeFurnace

"""

TODO

"""

class TubePECVD(TubeFurnace):
        
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
        self.params['specification'] = """
<h3>General description</h3>
A TubePECVD serves to deposit dielectric layers on wafers.
Wafers are first loaded into boats in the loadstation and then transferred to the process tubes where the deposition are performed.
When the processes are finished the boats are transferred to a cooldown shelf and then back to the loadstation for wafer load-out.
There is a downtime procedure in light of the required boat cleaning after using it for a defined number of depositions.
The cleaning itself is done externally but the boats need to undergo a coating run before re-using them.
There is also a downtime procedure available for preventive maintenance after a set number of process runs, but this is not enabled by default.
<h3>Description of the algorithm</h3>
The main loop is primarily concerned with the boat transport inside the tool, as described in the list below:
<ol>
<li>Go into downtime mode if a set number of processes has been run and all wafers were loaded out</li>
<li>Try to move boat from furnace to cooldown; try full boats first</li>
<li>Try to move boat from cooldown to loadstation; try full boats first</li>
<li>Perform action on boat in loadstation depending on state of boat and wafers:</li>
<ol>
<li>Perform coating run on empty boat if boat has been used for a set number of times</li>
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
        self.params['batch_size'] = 4
        self.params['batch_size_desc'] = "Number of cassettes in a single process batch"
        self.params['batch_size_type'] = "configuration"
        self.params['process_time'] = 30
        self.params['process_time_desc'] = "Time for a single process (minutes)"
        self.params['process_time_type'] = "process"
        self.params['cool_time'] = 10
        self.params['cool_time_desc'] = "Time for a single cooldown (minutes)"
        self.params['cool_time_type'] = "process"

        self.params['runs_before_boatclean'] = 100
        self.params['runs_before_boatclean_desc'] = "Number of PECVD processes before boat needs to be cleaned (0 to disable function)"
        self.params['runs_before_boatclean_type'] = "downtime"
        self.params['coating_run_duration'] = 75
        self.params['coating_run_duration_desc'] = "Time for a single PECVD coating run (minutes)"
        self.params['coating_run_duration_type'] = "downtime"

        self.params['downtime_runs'] = 0
        self.params['downtime_runs_desc'] = "Number of PECVD processes before downtime of the whole tool (0 to disable function)"
        self.params['downtime_runs_type'] = "downtime"
        self.params['downtime_duration'] = 60
        self.params['downtime_duration_desc'] = "Time for a single tool downtime cycle (minutes)"
        self.params['downtime_duration_type'] = "downtime"
        
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
        
        self.params['automation_loadsize'] = 25
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

        self.params['loop_begin'] = False
        self.params['loop_begin_type'] = "immutable"
        self.params['loop_end'] = False
        self.params['loop_end_type'] = "immutable"       
        
        self.params['cassette_size'] = -1
        self.params['cassette_size_type'] = "immutable"

        self.params.update(_params)

        if self.output_text and self.params['cassette_size'] == -1:
            string = str(round(self.env.now,1)) + " [TubePECVD][" + self.params['name'] + "] "
            string += "Missing cassette loop information"
            self.output_text.sig.emit(string)

        if self.params['cassette_size'] == -1:
            self.params['cassette_size'] = 100

        self.loop_begin = self.params['loop_begin']
        self.loop_end = self.params['loop_end']

        if not self.loop_begin == self.loop_end:
            string = "[TubeFurnace][" + self.params['name'] + "] WARNING: Cassette loop definition is not consistent for in- and output."
            self.output_text.sig.emit(string) 

        self.transport_counter = 0
        self.batches_loaded = 0        
        self.load_in_start = self.env.event()
        self.load_out_start = self.env.event()
        self.process_counter = 0
        
        ### Check automation loadsize ###
        if (not (self.output_text == None)) and (self.params['cassette_size'] % self.params['automation_loadsize']):
            string = "[TubePECVD][" + self.params['name'] + "] WARNING: Automation loadsize is not a multiple of cassette size. Automation will not work."
            self.output_text.sig.emit(string)        
        
        ### Add input and boat load/unload location ###
        self.input = CassetteContainer(self.env,"input",self.params['max_cassette_no'],not self.loop_end)

        if not self.loop_end:
            buffer_size = self.params['batch_size']*(self.params['no_of_processes']+self.params['no_of_cooldowns'])
            self.empty_cassette_buffer = CassetteContainer(self.env,"buffer",buffer_size,True)
        
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
        self.furnace_first_run = []
        self.furnace_start_time = []
        self.furnace_runs = []
        for i in range(self.params['no_of_processes']):
            self.furnace.append(-1) # -1 is empty; 0 and onwards is boat number
            self.furnace_status.append(0) # 0 is free; 1 is busy
            self.furnace_first_run.append(True) # keep track of first run
            self.furnace_start_time.append(0) # keep track of when first run started
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
        self.output = CassetteContainer(self.env,"output",self.params['max_cassette_no'],not self.loop_begin)        
     
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
     
        self.env.process(self.run_load_in())
        self.env.process(self.run_load_out())
        self.env.process(self.run_transport()) # important not to trigger signal before starting load processes 