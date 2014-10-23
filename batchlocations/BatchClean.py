# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 13:55:53 2014

@author: rnaber

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchTransport import BatchTransport
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer
import numpy as np

class BatchClean(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []        
        
        self.params = {}
        self.params['specification'] = self.tr("BatchClean consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- First oxide etch baths\n")
        self.params['specification'] += self.tr("- Rinse baths\n")
        self.params['specification'] += self.tr("- Chemical oxidation baths\n")
        self.params['specification'] += self.tr("- Rinse baths\n")
        self.params['specification'] += self.tr("- Second oxide etch baths\n")
        self.params['specification'] += self.tr("- Rinse baths\n")
        self.params['specification'] += self.tr("- Dryers\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There are four batch transporters:\n")        
        self.params['specification'] += self.tr("- Between input, first oxide etch and first rinse\n")
        self.params['specification'] += self.tr("- Between first rinse, chemical oxidation and second rinse\n")
        self.params['specification'] += self.tr("- Between second rinse, second oxide etch and third rinse\n")
        self.params['specification'] += self.tr("- Between third rinse, dryers and output")
        
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = self.tr("Number of units in a single process batch")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input and the same number at output")
        
        self.params['oxetch0_baths'] = 1
        self.params['oxetch0_baths_desc'] = self.tr("Number of baths for first oxide etch")         
        self.params['oxetch0_time'] = 2*60
        self.params['oxetch0_time_desc'] = self.tr("Time for a single oxide etch process (seconds)")
        
        self.params['rinse0_baths'] = 1
        self.params['rinse0_baths_desc'] = self.tr("Number of rinse baths after first oxide etch")
        self.params['rinse0_time'] = 5*60
        self.params['rinse0_time_desc'] = self.tr("Time for a single rinse cycle after first oxide etch (seconds)")        
        
        self.params['chemox_baths'] = 1
        self.params['chemox_baths_desc'] = self.tr("Number of baths for chemical oxidation")         
        self.params['chemox_time'] = 5*60
        self.params['chemox_time_desc'] = self.tr("Time for a single chemical oxidation process (seconds)")
        
        self.params['rinse1_baths'] = 1
        self.params['rinse1_baths_desc'] = self.tr("Number of rinse baths after chemical oxidation")        
        self.params['rinse1_time'] = 5*60
        self.params['rinse1_time_desc'] = self.tr("Time for a single rinse cycle after chemical oxidation (seconds)")
        
        self.params['oxetch1_baths'] = 1
        self.params['oxetch1_baths_desc'] = self.tr("Number of baths for second oxide etch")         
        self.params['oxetch1_time'] = 2*60
        self.params['oxetch1_time_desc'] = self.tr("Time for a single oxide etch process (seconds)")        

        self.params['rinse2_baths'] = 1
        self.params['rinse2_baths_desc'] = self.tr("Number of rinse baths after second oxide etch")        
        self.params['rinse2_time'] = 5*60
        self.params['rinse2_time_desc'] = self.tr("Time for a single rinse cycle after second oxide etch (seconds)")

        self.params['dryer_count'] = 2
        self.params['dryer_count_desc'] = self.tr("Number of dryers")        
        self.params['dry_time'] = 10*60
        self.params['dry_time_desc'] = self.tr("Time for a single dry cycle (seconds)")
        
        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")
        
        self.params['transfer1_time'] = 60
        self.params['transfer1_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")

        self.params['transfer2_time'] = 60
        self.params['transfer2_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")        

        self.params['transfer3_time'] = 60
        self.params['transfer3_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")        
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [BatchClean][" + self.params['name'] + "] Added a batch cleaning machine"
            self.output_text.sig.emit(string)
        
        ### Add input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])        

        ### Create and add all batchprocesses to list and keep track of positions in list###
        self.batchprocesses = []
        for i in np.arange(0,self.params['oxetch0_baths']):
            process_params = {}
            process_params['name'] = "h" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['oxetch0_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        first_rinse0 = self.params['oxetch0_baths']              
        for i in np.arange(0,self.params['rinse0_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse0_time']
            process_params['verbose'] = self.params['verbose']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_chemox = first_rinse0 + self.params['rinse0_baths']
        for i in np.arange(0,self.params['chemox_baths']):
            process_params = {}
            process_params['name'] = "o" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['chemox_time']
            process_params['verbose'] = self.params['verbose']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse1 = first_chemox + self.params['chemox_baths']
        for i in np.arange(0,self.params['rinse1_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse1_time']
            process_params['verbose'] = self.params['verbose']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_oxetch1 = first_rinse1 + self.params['rinse1_baths']
        for i in np.arange(0,self.params['oxetch1_baths']):
            process_params = {}
            process_params['name'] = "h" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['oxetch1_time']
            process_params['verbose'] = self.params['verbose']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_rinse2 = first_oxetch1 + self.params['oxetch1_baths']            
        for i in np.arange(0,self.params['rinse2_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse2_time']
            process_params['verbose'] = self.params['verbose']            
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        first_dryer = first_rinse2 + self.params['rinse2_baths'] 
        for i in np.arange(0,self.params['dryer_count']):
            process_params = {}
            process_params['name'] = "d" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['dry_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Batch transporter between input, first oxide etch and first rinse ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []
        
        for i in np.arange(0,self.params['oxetch0_baths']):
            for j in np.arange(first_rinse0,first_rinse0+self.params['rinse0_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer0_time']])
        
        for i in np.arange(0,self.params['oxetch0_baths']):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])

        transport_params = {}
        transport_params['name'] = "cl0"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']        
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between first rinse, chemical oxidation and second rinse ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []

        for i in np.arange(first_chemox,first_chemox+self.params['chemox_baths']):
            for j in np.arange(first_rinse1,first_rinse1+self.params['rinse1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in np.arange(first_rinse0,first_rinse0+self.params['rinse0_baths']):
            for j in np.arange(first_chemox,first_chemox+self.params['chemox_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])     

        transport_params = {}
        transport_params['name'] = "cl1"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']        
        self.transport1 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between second rinse, second oxide etch and third rinse ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []

        for i in np.arange(first_oxetch1,first_oxetch1+self.params['oxetch1_baths']):
            for j in np.arange(first_rinse2,first_rinse2+self.params['rinse2_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer2_time']])

        for i in np.arange(first_rinse1,first_rinse1+self.params['rinse1_baths']):
            for j in np.arange(first_oxetch1,first_oxetch1+self.params['oxetch1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer2_time']])     

        transport_params = {}
        transport_params['name'] = "cl2"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']         
        self.transport2 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

        ### Batch transporter between third rinse, dryers and output ###
        # First check whether batch can be brought to rinse/output, because that has priority
        batchconnections = []

        for i in np.arange(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer3_time']])

        for i in np.arange(first_rinse2,first_rinse2+self.params['rinse2_baths']):
            for j in np.arange(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer3_time']])    

        transport_params = {}
        transport_params['name'] = "cl3"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']
        self.transport3 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

    def report(self):
        string = "[BatchClean][" + self.params['name'] + "] Units processed: " + str(self.transport3.transport_counter - self.output.container.level)
        self.output_text.sig.emit(string)

        self.utilization.append("BatchClean")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        production_volume = self.transport3.transport_counter - self.output.container.level
        production_hours = (self.env.now - self.batchprocesses[0].start_time)/3600
        self.utilization.append(np.round(100*(production_volume/production_hours)/self.nominal_throughput(),1))
        
        for i in range(len(self.batchprocesses)):
            self.utilization.append([self.batchprocesses[i].name,np.round(self.batchprocesses[i].idle_time(),1)])                 
            
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