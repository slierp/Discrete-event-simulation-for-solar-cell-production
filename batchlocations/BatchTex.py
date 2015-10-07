# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchTransport import BatchTransport
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class BatchTex(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        self.utilization = []
        self.diagram = """blockdiag {      
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       A [label = "Input"];
                       B [label = "Alkaline texture", stacked];
                       C [label = "Rinse0", stacked];
                       D [label = "Neutralization", stacked];
                       E [label = "Rinse1", stacked];
                       F [label = "Dry", stacked];
                       G [label = "Output"];
                       A -> B -> C -> D -> E -> F -> G;
                       D -> E [folded];                       
                       } """
        
        self.params = {}
        
        self.params['specification'] = """
<h3>General description</h3>
A batch texture is used for etching wafers to create a surface texture.
The wafers are loaded into special cassettes that can withstand harsh chemicals.
There is a downtime procedure defined for the texturing baths, during which the texturing solution is replaced.\n
<h3>Description of the algorithm</h3>
TO BE ADDED\n
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
        
        self.params['tex_baths'] = 3
        self.params['tex_baths_desc'] = "Number of baths for alkaline texture"
        self.params['tex_baths_type'] = "configuration"
        self.params['tex_time'] = 15
        self.params['tex_time_desc'] = "Time for a single alkaline texturing process (minutes)"
        self.params['tex_time_type'] = "process"
        
        self.params['tex_downtime_runs'] = 80
        self.params['tex_downtime_runs_desc'] = "Number of texturing processes before downtime"
        self.params['tex_downtime_runs_type'] = "downtime"
        self.params['tex_downtime_duration'] = 60
        self.params['tex_downtime_duration_desc'] = "Time for a single texturing process downtime cycle (minutes)"
        self.params['tex_downtime_duration_type'] = "downtime"

        self.params['rinse0_baths'] = 1
        self.params['rinse0_baths_desc'] = "Number of rinse baths after texture"
        self.params['rinse0_baths_type'] = "configuration"
        self.params['rinse0_time'] = 5
        self.params['rinse0_time_desc'] = "Time for a single rinse cycle after texture (minutes)"
        self.params['rinse0_time_type'] = "process"

        self.params['neutr_baths'] = 1
        self.params['neutr_baths_desc'] = "Number of baths for HCl neutralization"
        self.params['neutr_baths_type'] = "configuration"
        self.params['neutr_time'] = 5
        self.params['neutr_time_desc'] = "Time for a single HCl neutralization process (minutes)"
        self.params['neutr_time_type'] = "process"

        self.params['rinse1_baths'] = 1
        self.params['rinse1_baths_desc'] = "Number of rinse baths after neutralization"
        self.params['rinse1_baths_type'] = "configuration"
        self.params['rinse1_time'] = 5
        self.params['rinse1_time_desc'] = "Time for a single rinse cycle after neutralization (minutes)"
        self.params['rinse1_time_type'] = "process"

        self.params['dryer_count'] = 3
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
        
        self.params.update(_params)        
        
        ### Add input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        self.batchprocesses = []

        ### Texturing baths ###
        for i in range(0,self.params['tex_baths']):
            process_params = {}
            process_params['name'] = "t" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['tex_time']
            process_params['downtime_runs'] = self.params['tex_downtime_runs']
            process_params['downtime_duration'] = 60*self.params['tex_downtime_duration']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### First rinse baths ###
        first_rinse0 = self.params['tex_baths'] 
        for i in range(0,self.params['rinse0_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['rinse0_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Neutralization baths ###
        first_neutr = first_rinse0 + self.params['rinse0_baths'] 
        for i in range(0,self.params['neutr_baths']):
            process_params = {}
            process_params['name'] = "n" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['neutr_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Second rinse baths ###
        first_rinse1 = first_neutr + self.params['neutr_baths'] 
        for i in range(0,self.params['rinse1_baths']):       
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['rinse1_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))        

        ### Dryers ### 
        first_dryer = first_rinse1 + self.params['rinse1_baths']       
        for i in range(0,self.params['dryer_count']):
            process_params = {}
            process_params['name'] = "d" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 60*self.params['dry_time']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Batch transporter between input, texture baths and first rinse ###
        # First check whether batch can be brought to rinse, because that has priority
        batchconnections = []

        for i in range(0,self.params['tex_baths']):
            for j in range(first_rinse0,first_rinse0+self.params['rinse0_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer0_time']])
        
        for i in range(0,self.params['tex_baths']):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])

        transport_params = {}
        transport_params['name'] = "tex0"
        transport_params['batch_size'] = self.params['batch_size']     
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between first rinse, neutralization, second rinse  and dryers ###
        # First check whether batch can be brought to rinse or dry, because that has priority
        batchconnections = []

        for i in range(first_rinse1,first_rinse1+self.params['rinse1_baths']):
            for j in range(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in range(first_neutr,first_neutr+self.params['neutr_baths']):
            for j in range(first_rinse1,first_rinse1+self.params['rinse1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in range(first_rinse0,first_rinse0+self.params['rinse0_baths']):
            for j in range(first_neutr,first_neutr+self.params['neutr_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        transport_params = {}
        transport_params['name'] = "tex1"
        transport_params['batch_size'] = self.params['batch_size']       
        self.transport1 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

        ### Batch transporter between dryers and output ###
        batchconnections = []

        for i in range(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer2_time']])

        transport_params = {}
        transport_params['name'] = "tex2"
        transport_params['batch_size'] = self.params['batch_size']     
        self.transport2 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)          

    def report(self):
        string = "[BatchTex][" + self.params['name'] + "] Units processed: " + str(self.transport2.transport_counter)
        self.output_text.sig.emit(string)        

        self.utilization.append("BatchTex")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport2.transport_counter
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
        
        if (self.nominal_throughput() > 0) & (production_hours > 0): 
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,round(self.batchprocesses[i].idle_time(),1)])

    def prod_volume(self):
        return self.transport2.transport_counter
        
    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['tex_baths']*3600/(60*self.params['tex_time']))
        throughputs.append(self.params['batch_size']*self.params['rinse0_baths']*3600/(60*self.params['rinse0_time']))
        throughputs.append(self.params['batch_size']*self.params['neutr_baths']*3600/(60*self.params['neutr_time']))
        throughputs.append(self.params['batch_size']*self.params['rinse1_baths']*3600/(60*self.params['rinse1_time']))
        throughputs.append(self.params['batch_size']*self.params['dryer_count']*3600/(60*self.params['dry_time']))
        return min(throughputs)        
        
        