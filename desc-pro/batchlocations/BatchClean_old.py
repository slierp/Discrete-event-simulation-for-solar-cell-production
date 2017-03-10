# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from batchlocations.BatchTransport import BatchTransport
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class BatchClean(QtCore.QObject):
    
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        
        self.env = _env
        self.output_text = _output
        self.utilization = []
        self.diagram = """blockdiag {    
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Oxide etch0", stacked];
                       C [label = "Rinse0", stacked];
                       D [label = "Chemical oxidation", stacked];
                       E [label = "Rinse1", stacked];
                       F [label = "Oxide etch1", stacked];
                       G [label = "Rinse2", stacked];                       
                       H [label = "Dry", stacked];
                       I [label = "Output"];
                       A -> B -> C -> D -> E -> F -> G -> H -> I;
                       D -> E [folded];
                       H -> I [folded];  
                       } """        
        
        self.params = {}

        self.params['specification'] = """
<h3>General description</h3>
<p>A batch clean tool is used for cleaning wafers by creating a chemical oxide and then removing it.
The first step is an HF dip to remove any existing oxide layer and it is followed by chemical oxidation, a second HF dip and a drying step.
The user can configure the tool by setting the number of baths for each process step and for the rinsing steps in between.
It is also possible to configure the transportation time for each of the four transport machines inside the machine.</p>
There are four fixed transport machines inside the machine:
<ul>
<li>Transporter between input, first HF dip and first rinse</li>
<li>Transporter between first rinse, chemical oxidation and second rinse</li>
<li>Transporter between second rinse, second HF dip, third rinse and dryers</li>
<li>Transporter between dryers and output</li>
</ul>
There is currently no downtime procedure available for this tool.
\n
<h3>Description of the algorithm</h3>
The programming code that is specific to the cleaning machine only defines the process baths and the transport connections between them.
The actual processes and transport actions are then performed by generic algorithms.
The main functions inside the process algorithm are:
<ul>
<li>Simulate processes by holding the wafers for a set amount of time.
It places a resource lock onto itself during that time, to prevent any transporter from accessing the process bath.</li>
<li>Checking for the need for downtime procedures</li>
<li>Starting downtime procedures including a resource lock onto itself</li>
</ul>
All these functions in the process algorithm are triggered by the transport algorithm.
This algorithm consists of a single loop that looks at the list of tool connections and checks if any of three actions are possible.
The three possible actions depend on the type of toolconnection:
<ol>
<li>Toolconnection is from container to process chamber: Try to perform transport and start process</li>
<li>Toolconnection is from process chamber to container: Try to perform transport and check if chamber requires downtime</li>
<li>Toolconnection is process chamber to process chamber: Try to perform transport, check downtime and start new process</li>
</ol>
All transport actions include a set delay to simulate the time needed for the transport.
If any action was possible while going over toolconnections list then the loop will restart with going over the list to search for possible actions.
If no action was possible it will wait for a set amount of time (60 seconds by default) before trying again.
\n
        """
        
        self.params['name'] = ""
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = "Number of units in a single process batch"
        self.params['batch_size_type'] = "configuration"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['cassette_size_type'] = "configuration"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        self.params['max_cassette_no_type'] = "configuration"
        
        self.params['oxetch0_baths'] = 1
        self.params['oxetch0_baths_desc'] = "Number of baths for first oxide etch"
        self.params['oxetch0_baths_type'] = "configuration"
        self.params['oxetch0_time'] = 2
        self.params['oxetch0_time_desc'] = "Time for a single oxide etch process in the first bath (minutes)"
        self.params['oxetch0_time_type'] = "process"
        
        self.params['rinse0_baths'] = 1
        self.params['rinse0_baths_desc'] = "Number of rinse baths after first oxide etch"
        self.params['rinse0_baths_type'] = "configuration"
        self.params['rinse0_time'] = 5
        self.params['rinse0_time_desc'] = "Time for a single rinse cycle after first oxide etch (minutes)"
        self.params['rinse0_time_type'] = "process"
        
        self.params['chemox_baths'] = 1
        self.params['chemox_baths_desc'] = "Number of baths for chemical oxidation"
        self.params['chemox_baths_type'] = "configuration"
        self.params['chemox_time'] = 5
        self.params['chemox_time_desc'] = "Time for a single chemical oxidation process (minutes)"
        self.params['chemox_time_type'] = "process"
        
        self.params['rinse1_baths'] = 1
        self.params['rinse1_baths_desc'] = "Number of rinse baths after chemical oxidation"
        self.params['rinse1_baths_type'] = "configuration"
        self.params['rinse1_time'] = 5
        self.params['rinse1_time_desc'] = "Time for a single rinse cycle after chemical oxidation (minutes)"
        self.params['rinse1_time_type'] = "process"
        
        self.params['oxetch1_baths'] = 1
        self.params['oxetch1_baths_desc'] = "Number of baths for second oxide etch"
        self.params['oxetch1_baths_type'] = "configuration"
        self.params['oxetch1_time'] = 2
        self.params['oxetch1_time_desc'] = "Time for a single oxide etch process in the second bath (minutes)"
        self.params['oxetch1_time_type'] = "process"

        self.params['rinse2_baths'] = 1
        self.params['rinse2_baths_desc'] = "Number of rinse baths after second oxide etch"
        self.params['rinse2_baths_type'] = "configuration"
        self.params['rinse2_time'] = 5
        self.params['rinse2_time_desc'] = "Time for a single rinse cycle after second oxide etch (minutes)"
        self.params['rinse2_time_type'] = "process"

        self.params['dryer_count'] = 2
        self.params['dryer_count_desc'] = "Number of dryers"
        self.params['dryer_count_type'] = "configuration"
        self.params['dry_time'] = 10
        self.params['dry_time_desc'] = "Time for a single dry cycle (minutes)"
        self.params['dry_time_type'] = "process"
        
        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = "Time for single transfer by transporter 0 (seconds)"
        self.params['transfer0_time_type'] = "automation"
        
        self.params['transfer1_time'] = 60
        self.params['transfer1_time_desc'] = "Time for single transfer by transporter 1 (seconds)"
        self.params['transfer1_time_type'] = "automation"

        self.params['transfer2_time'] = 60
        self.params['transfer2_time_desc'] = "Time for single transfer by transporter 2 (seconds)"
        self.params['transfer2_time_type'] = "automation"

        self.params['transfer3_time'] = 60
        self.params['transfer3_time_desc'] = "Time for single transfer by transporter 3 (seconds)"
        self.params['transfer3_time_type'] = "automation"
        
        self.params.update(_params)
        
        ### Add input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])        

        ### Create and add all batchprocesses to list and keep track of positions in list###
        self.batchprocesses = []
        for i in range(0,self.params['oxetch0_baths']):
            process_params = {}
            process_params['name'] = "HF " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['oxetch0_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        first_rinse0 = self.params['oxetch0_baths']              
        for i in range(0,self.params['rinse0_baths']):
            process_params = {}
            process_params['name'] = "Rinse " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['rinse0_time']       
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_chemox = first_rinse0 + self.params['rinse0_baths']
        for i in range(0,self.params['chemox_baths']):
            process_params = {}
            process_params['name'] = "Oxid " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['chemox_time']         
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse1 = first_chemox + self.params['chemox_baths']
        for i in range(0,self.params['rinse1_baths']):
            process_params = {}
            process_params['name'] = "Rinse " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['rinse1_time']          
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_oxetch1 = first_rinse1 + self.params['rinse1_baths']
        for i in range(0,self.params['oxetch1_baths']):
            process_params = {}
            process_params['name'] = "HF " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['oxetch1_time']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse2 = first_oxetch1 + self.params['oxetch1_baths']            
        for i in range(0,self.params['rinse2_baths']):
            process_params = {}
            process_params['name'] = "Rinse " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['rinse2_time']          
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_dryer = first_rinse2 + self.params['rinse2_baths'] 
        for i in range(0,self.params['dryer_count']):
            process_params = {}
            process_params['name'] = "Dry " + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['dry_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Batch transporter between input, first oxide etch and first rinse ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []
        
        for i in range(0,self.params['oxetch0_baths']):
            for j in range(first_rinse0,first_rinse0+self.params['rinse0_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer0_time']])
        
        for i in range(0,self.params['oxetch0_baths']):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])

        transport_params = {}
        transport_params['name'] = "cl0"
        transport_params['batch_size'] = self.params['batch_size']      
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between first rinse, chemical oxidation and second rinse ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []

        for i in range(first_chemox,first_chemox+self.params['chemox_baths']):
            for j in range(first_rinse1,first_rinse1+self.params['rinse1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in range(first_rinse0,first_rinse0+self.params['rinse0_baths']):
            for j in range(first_chemox,first_chemox+self.params['chemox_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])     

        transport_params = {}
        transport_params['name'] = "cl1"
        transport_params['batch_size'] = self.params['batch_size']        
        self.transport1 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between second rinse, second oxide etch, third rinse and dryers ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []

        for i in range(first_rinse2,first_rinse2+self.params['rinse2_baths']):
            for j in range(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer2_time']])

        for i in range(first_oxetch1,first_oxetch1+self.params['oxetch1_baths']):
            for j in range(first_rinse2,first_rinse2+self.params['rinse2_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer2_time']])

        for i in range(first_rinse1,first_rinse1+self.params['rinse1_baths']):
            for j in range(first_oxetch1,first_oxetch1+self.params['oxetch1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer2_time']])     

        transport_params = {}
        transport_params['name'] = "cl2"
        transport_params['batch_size'] = self.params['batch_size']        
        self.transport2 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

        ### Batch transporter between dryers and output ###
        # First check whether batch can be brought to output, because that has priority
        batchconnections = []

        for i in range(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer3_time']])    

        transport_params = {}
        transport_params['name'] = "cl3"
        transport_params['batch_size'] = self.params['batch_size']
        self.transport3 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

    def report(self):
        self.utilization.append("BatchClean")
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport3.transport_counter
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600

        if (self.nominal_throughput() > 0) & (production_hours > 0):        
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)

        self.utilization.append(self.transport3.transport_counter)
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,round(100-self.batchprocesses[i].idle_time(),1)])

    def prod_volume(self):
        return self.transport3.transport_counter
            
    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['oxetch0_baths']*3600/(60*self.params['oxetch0_time']))
        throughputs.append(self.params['batch_size']*self.params['rinse0_baths']*3600/(60*self.params['rinse0_time']))
        throughputs.append(self.params['batch_size']*self.params['chemox_baths']*3600/(60*self.params['chemox_time']))
        throughputs.append(self.params['batch_size']*self.params['rinse1_baths']*3600/(60*self.params['rinse1_time']))
        throughputs.append(self.params['batch_size']*self.params['oxetch1_baths']*3600/(60*self.params['oxetch1_time']))
        throughputs.append(self.params['batch_size']*self.params['rinse2_baths']*3600/(60*self.params['rinse2_time']))
        throughputs.append(self.params['batch_size']*self.params['dryer_count']*3600/(60*self.params['dry_time']))
        return min(throughputs)