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
        self.params['specification'] += self.tr("- Texturing baths (currently 3)\n")
        self.params['specification'] += self.tr("- Rinse baths (currently 1)\n")
        self.params['specification'] += self.tr("- Neutralization baths (currently 1)\n")
        self.params['specification'] += self.tr("- Rinse baths (currently 1)\n")
        self.params['specification'] += self.tr("- Dryers (currently 3)\n")
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
        self.params['process_time'] = 20*60
        self.params['process_time_desc'] = self.tr("Time for a single texture process (seconds)")
        self.params['rinse_time'] = 5*60
        self.params['rinse_time_desc'] = self.tr("Time for a single rinse cycle (seconds)")
        self.params['neutr_time'] = 5*60
        self.params['neutr_time_desc'] = self.tr("Time for a single neutralizatin process (seconds)")
        self.params['dry_time'] = 20*60
        self.params['dry_time_desc'] = self.tr("Time for a single dry cycle (seconds)")
        self.params['transfer_time'] = 60
        self.params['transfer_time_desc'] = self.tr("Time for cassette transfer between any two locations (baths, input and output) (seconds)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)        
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [BatchTex][" + self.params['name'] + "] Added a batch texture machine"
            self.output_text.sig.emit(string)
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])        

        self.batchprocesses = {}
        self.batchprocesses[0] = BatchProcess(self.env,"tex0",self.params['batch_size'],self.params['process_time'])
        self.batchprocesses[1] = BatchProcess(self.env,"tex1",self.params['batch_size'],self.params['process_time'])
        self.batchprocesses[2] = BatchProcess(self.env,"tex2",self.params['batch_size'],self.params['process_time'])
        self.batchprocesses[3] = BatchProcess(self.env,"rinse0",self.params['batch_size'],self.params['rinse_time'])
        self.batchprocesses[4] = BatchProcess(self.env,"neutr",self.params['batch_size'],self.params['neutr_time'])
        self.batchprocesses[5] = BatchProcess(self.env,"rinse1",self.params['batch_size'],self.params['rinse_time'])
        self.batchprocesses[6] = BatchProcess(self.env,"dry0",self.params['batch_size'],self.params['dry_time'])
        self.batchprocesses[7] = BatchProcess(self.env,"dry1",self.params['batch_size'],self.params['dry_time'])
        self.batchprocesses[8] = BatchProcess(self.env,"dry2",self.params['batch_size'],self.params['dry_time'])
        
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        batchconnections = {}
        # First check whether batch can be brought to rinse, because that has priority
        batchconnections[0] = [self.batchprocesses[0],self.batchprocesses[3],self.params['transfer_time']]
        batchconnections[1] = [self.batchprocesses[1],self.batchprocesses[3],self.params['transfer_time']]
        batchconnections[2] = [self.batchprocesses[2],self.batchprocesses[3],self.params['transfer_time']]
        batchconnections[3] = [self.input,self.batchprocesses[0],self.params['transfer_time']]
        batchconnections[4] = [self.input,self.batchprocesses[1],self.params['transfer_time']]
        batchconnections[5] = [self.input,self.batchprocesses[2],self.params['transfer_time']]
        self.transport0 = BatchTransport(self.env,batchconnections,"[" + self.params['name'] + "][tex0]",self.params['batch_size'],self.params['verbose'])

        batchconnections = {}
        # First check whether batch can be brought to rinse or output, because that has priority
        batchconnections[0] = [self.batchprocesses[4],self.batchprocesses[5],self.params['transfer_time']]
        batchconnections[1] = [self.batchprocesses[3],self.batchprocesses[4],self.params['transfer_time']]
        batchconnections[2] = [self.batchprocesses[5],self.batchprocesses[6],self.params['transfer_time']]
        batchconnections[3] = [self.batchprocesses[5],self.batchprocesses[7],self.params['transfer_time']]       
        batchconnections[4] = [self.batchprocesses[5],self.batchprocesses[8],self.params['transfer_time']]
        self.transport1 = BatchTransport(self.env,batchconnections,"[" + self.params['name'] + "][tex1]",self.params['batch_size'],self.params['verbose'])

        batchconnections = {}
        batchconnections[0] = [self.batchprocesses[6],self.output,self.params['transfer_time']]
        batchconnections[1] = [self.batchprocesses[7],self.output,self.params['transfer_time']]
        batchconnections[2] = [self.batchprocesses[8],self.output,self.params['transfer_time']]
        self.transport2 = BatchTransport(self.env,batchconnections,"[" + self.params['name'] + "][tex2]",self.params['batch_size'],self.params['verbose'])

    def report(self):
        string = "[BatchTex][" + self.params['name'] + "] Units processed: " + str(self.transport2.transport_counter - self.output.container.level)
        self.output_text.sig.emit(string)
        
        if (self.params['verbose']):
            for i in self.batchprocesses:
                string = "[BatchTex][" + self.params['name'] + "][" + self.batchprocesses[i].name + "] Idle time: " + str(np.round(self.batchprocesses[i].idle_time(),1)) + " %"
                self.output_text.sig.emit(string)