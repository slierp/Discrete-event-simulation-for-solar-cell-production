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

class BatchTex(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        
        self.params = {}
        self.params['specification'] = self.tr("BatchTex consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- Texturing baths\n")
        self.params['specification'] += self.tr("- Rinse baths\n")
        self.params['specification'] += self.tr("- Neutralization baths\n")
        self.params['specification'] += self.tr("- Rinse baths\n")
        self.params['specification'] += self.tr("- Dryers\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There are three batch transporters:\n")        
        self.params['specification'] += self.tr("- Between input, texture and first rinse\n")
        self.params['specification'] += self.tr("- Between first rinse, neutralization, second rinse and the dryers\n")
        self.params['specification'] += self.tr("- Between dryers and output")        

        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['batch_size'] = 400
        self.params['batch_size_desc'] = self.tr("Number of units in a single process batch")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input and the same number at output")
        
        self.params['tex_baths'] = 3
        self.params['tex_baths_desc'] = self.tr("Number of baths for alkaline texture")         
        self.params['tex_time'] = 20*60
        self.params['tex_time_desc'] = self.tr("Time for a single alkaline texturing process (seconds)")        

        self.params['rinse0_baths'] = 1
        self.params['rinse0_baths_desc'] = self.tr("Number of rinse baths after texture")
        self.params['rinse0_time'] = 5*60
        self.params['rinse0_time_desc'] = self.tr("Time for a single rinse cycle after texture (seconds)") 

        self.params['neutr_baths'] = 1
        self.params['neutr_baths_desc'] = self.tr("Number of baths for HCl neutralization")         
        self.params['neutr_time'] = 5*60
        self.params['neutr_time_desc'] = self.tr("Time for a single HCl neutralization process (seconds)") 

        self.params['rinse1_baths'] = 1
        self.params['rinse1_baths_desc'] = self.tr("Number of rinse baths after neutralization")
        self.params['rinse1_time'] = 5*60
        self.params['rinse1_time_desc'] = self.tr("Time for a single rinse cycle after neutralization (seconds)")

        self.params['dryer_count'] = 3
        self.params['dryer_count_desc'] = self.tr("Number of dryers")        
        self.params['dry_time'] = 20*60
        self.params['dry_time_desc'] = self.tr("Time for a single dry cycle (seconds)")

        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")
        
        self.params['transfer1_time'] = 60
        self.params['transfer1_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")

        self.params['transfer2_time'] = 60
        self.params['transfer2_time_desc'] = self.tr("Time for single transfer by transporter (seconds)")
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)        
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [BatchTex][" + self.params['name'] + "] Added a batch texture machine"
            self.output_text.sig.emit(string)
        
        ### Add input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])

        self.batchprocesses = []

        ### Texturing baths ###
        for i in np.arange(0,self.params['tex_baths']):
            process_params = {}
            process_params['name'] = "t" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['tex_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### First rinse baths ###
        first_rinse0 = self.params['tex_baths'] 
        for i in np.arange(0,self.params['rinse0_baths']):
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse0_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Neutralization baths ###
        first_neutr = first_rinse0 + self.params['rinse0_baths'] 
        for i in np.arange(0,self.params['neutr_baths']):
            process_params = {}
            process_params['name'] = "n" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['neutr_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Second rinse baths ###
        first_rinse1 = first_neutr + self.params['neutr_baths'] 
        for i in np.arange(0,self.params['rinse1_baths']):       
            process_params = {}
            process_params['name'] = "r" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['rinse1_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))        

        ### Dryers ### 
        first_dryer = first_rinse1 + self.params['rinse1_baths']       
        for i in np.arange(0,self.params['dryer_count']):
            process_params = {}
            process_params['name'] = "d" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = self.params['dry_time']
            process_params['verbose'] = self.params['verbose']
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))
        
        ### Add output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Batch transporter between input, texture baths and first rinse ###
        # First check whether batch can be brought to rinse, because that has priority
        batchconnections = []

        for i in np.arange(0,self.params['tex_baths']):
            for j in np.arange(first_rinse0,first_rinse0+self.params['rinse0_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer0_time']])
        
        for i in np.arange(0,self.params['tex_baths']):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])

        transport_params = {}
        transport_params['name'] = "[" + self.params['name'] + "][tex0]"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']        
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)

        ### Batch transporter between first rinse, neutralization, second rinse  and dryers ###
        # First check whether batch can be brought to rinse or dry, because that has priority
        batchconnections = []

        for i in np.arange(first_rinse1,first_rinse1+self.params['rinse1_baths']):
            for j in np.arange(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in np.arange(first_neutr,first_neutr+self.params['neutr_baths']):
            for j in np.arange(first_rinse1,first_rinse1+self.params['rinse1_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        for i in np.arange(first_rinse0,first_rinse0+self.params['rinse0_baths']):
            for j in np.arange(first_neutr,first_neutr+self.params['neutr_baths']):
                batchconnections.append([self.batchprocesses[i],self.batchprocesses[j],self.params['transfer1_time']])

        transport_params = {}
        transport_params['name'] = "[" + self.params['name'] + "][tex1]"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']        
        self.transport1 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

        ### Batch transporter between dryers and output ###
        batchconnections = []

        for i in np.arange(first_dryer,first_dryer+self.params['dryer_count']):
                batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer2_time']])

        transport_params = {}
        transport_params['name'] = "[" + self.params['name'] + "][tex2]"
        transport_params['batch_size'] = self.params['batch_size']
        transport_params['verbose'] = self.params['verbose']        
        self.transport2 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)          

    def report(self):
        string = "[BatchTex][" + self.params['name'] + "] Units processed: " + str(self.transport2.transport_counter - self.output.container.level)
        self.output_text.sig.emit(string)        

        idle_item = []
        idle_item.append("BatchTex")
        idle_item.append(self.params['name'])
        for i in range(len(self.batchprocesses)):
            idle_item.append([self.batchprocesses[i].name,np.round(self.batchprocesses[i].idle_time(),1)])
        self.idle_times.append(idle_item)                 