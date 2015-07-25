# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
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
        self.params['specification'] = "BatchClean consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- First oxide etch baths\n"
        self.params['specification'] += "- Rinse baths\n"
        self.params['specification'] += "- Chemical oxidation baths\n"
        self.params['specification'] += "- Rinse baths\n"
        self.params['specification'] += "- Second oxide etch baths\n"
        self.params['specification'] += "- Rinse baths\n"
        self.params['specification'] += "- Dryers\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There are four batch transporters:\n"
        self.params['specification'] += "- Between input, first oxide etch and first rinse\n"
        self.params['specification'] += "- Between first rinse, chemical oxidation and second rinse\n"
        self.params['specification'] += "- Between second rinse, second oxide etch, third rinse and dryers\n"
        self.params['specification'] += "- Between dryers and output\n"
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = "Number of units in a single process batch"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        
        self.params['oxetch0_baths'] = 1
        self.params['oxetch0_baths_desc'] = "Number of baths for first oxide etch"
        self.params['oxetch0_time'] = 2*60
        self.params['oxetch0_time_desc'] = "Time for a single oxide etch process (seconds)"
        
        self.params['rinse0_baths'] = 1
        self.params['rinse0_baths_desc'] = "Number of rinse baths after first oxide etch"
        self.params['rinse0_time'] = 5*60
        self.params['rinse0_time_desc'] = "Time for a single rinse cycle after first oxide etch (seconds)"
        
        self.params['chemox_baths'] = 1
        self.params['chemox_baths_desc'] = "Number of baths for chemical oxidation"
        self.params['chemox_time'] = 5*60
        self.params['chemox_time_desc'] = "Time for a single chemical oxidation process (seconds)"
        
        self.params['rinse1_baths'] = 1
        self.params['rinse1_baths_desc'] = "Number of rinse baths after chemical oxidation"
        self.params['rinse1_time'] = 5*60
        self.params['rinse1_time_desc'] = "Time for a single rinse cycle after chemical oxidation (seconds)"
        
        self.params['oxetch1_baths'] = 1
        self.params['oxetch1_baths_desc'] = "Number of baths for second oxide etch"
        self.params['oxetch1_time'] = 2*60
        self.params['oxetch1_time_desc'] = "Time for a single oxide etch process (seconds)"

        self.params['rinse2_baths'] = 1
        self.params['rinse2_baths_desc'] = "Number of rinse baths after second oxide etch"
        self.params['rinse2_time'] = 5*60
        self.params['rinse2_time_desc'] = "Time for a single rinse cycle after second oxide etch (seconds)"

        self.params['dryer_count'] = 2
        self.params['dryer_count_desc'] = "Number of dryers"
        self.params['dry_time'] = 10*60
        self.params['dry_time_desc'] = "Time for a single dry cycle (seconds)"
        
        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = "Time for single transfer by transporter (seconds)"
        
        self.params['transfer1_time'] = 60
        self.params['transfer1_time_desc'] = "Time for single transfer by transporter (seconds)"

        self.params['transfer2_time'] = 60
        self.params['transfer2_time_desc'] = "Time for single transfer by transporter (seconds)"

        self.params['transfer3_time'] = 60
        self.params['transfer3_time_desc'] = "Time for single transfer by transporter (seconds)"
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
#        if (self.params['verbose']): #DEBUG
#            string = str(self.env.now) + " - [BatchClean][" + self.params['name'] + "] Added a batch cleaning machine" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        ### Add input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])        

        ### Create and add all batchprocesses to list and keep track of positions in list###
        self.batchprocesses = []
        for i in range(0,self.params['oxetch0_baths']):
            process_params = {}
            process_params['name'] = "h" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['oxetch0_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        first_rinse0 = self.params['oxetch0_baths']              
        for i in range(0,self.params['rinse0_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse0_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG         
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_chemox = first_rinse0 + self.params['rinse0_baths']
        for i in range(0,self.params['chemox_baths']):
            process_params = {}
            process_params['name'] = "o" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['chemox_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse1 = first_chemox + self.params['chemox_baths']
        for i in range(0,self.params['rinse1_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse1_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_oxetch1 = first_rinse1 + self.params['rinse1_baths']
        for i in range(0,self.params['oxetch1_baths']):
            process_params = {}
            process_params['name'] = "h" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['oxetch1_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse2 = first_oxetch1 + self.params['oxetch1_baths']            
        for i in range(0,self.params['rinse2_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse2_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG           
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_dryer = first_rinse2 + self.params['rinse2_baths'] 
        for i in range(0,self.params['dryer_count']):
            process_params = {}
            process_params['name'] = "d" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['dry_time']
#            process_params['verbose'] = self.params['verbose'] #DEBUG
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
#        transport_params['verbose'] = self.params['verbose'] #DEBUG      
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
#        transport_params['verbose'] = self.params['verbose'] #DEBUG        
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
#        transport_params['verbose'] = self.params['verbose'] #DEBUG        
        self.transport2 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

        ### Batch transporter between dryers and output ###
        # First check whether batch can be brought to output, because that has priority
        batchconnections = []

        for i in range(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer3_time']])    

        transport_params = {}
        transport_params['name'] = "cl3"
        transport_params['batch_size'] = self.params['batch_size']
#        transport_params['verbose'] = self.params['verbose'] #DEBUG
        self.transport3 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

    def report(self):
        string = "[BatchClean][" + self.params['name'] + "] Units processed: " + str(self.transport3.transport_counter)
        self.output_text.sig.emit(string)

        self.utilization.append("BatchClean")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport3.transport_counter
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600

        if (self.nominal_throughput() > 0) & (production_hours > 0):        
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        else:
            self.utilization.append(0)
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,round(self.batchprocesses[i].idle_time(),1)])                 

    def prod_volume(self):
        return self.transport3.transport_counter
            
    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['oxetch0_baths']*3600/self.params['oxetch0_time'])
        throughputs.append(self.params['batch_size']*self.params['rinse0_baths']*3600/self.params['rinse0_time'])
        throughputs.append(self.params['batch_size']*self.params['chemox_baths']*3600/self.params['chemox_time'])
        throughputs.append(self.params['batch_size']*self.params['rinse1_baths']*3600/self.params['rinse1_time'])
        throughputs.append(self.params['batch_size']*self.params['oxetch1_baths']*3600/self.params['oxetch1_time'])
        throughputs.append(self.params['batch_size']*self.params['rinse2_baths']*3600/self.params['rinse2_time'])
        throughputs.append(self.params['batch_size']*self.params['dryer_count']*3600/self.params['dry_time'])        
        return min(throughputs)            