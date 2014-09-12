# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 13:55:53 2014

@author: rnaber

"""

from __future__ import division
from BatchTransport import BatchTransport
from BatchProcess import BatchProcess
from BatchContainer import BatchContainer
import numpy as np

class BatchTex(object):
        
    def __init__(self, env, _params = {}):   
        
        self.env = env
        
        self.params = {}
        self.params['name'] = ""
        self.params['batch_size'] = 400
        self.params['cassette_size'] = 100
        self.params['max_cassette_no'] = 8 # max number of cassettes in the input and output buffers
        self.params['process_time'] = 20*60
        self.params['rinse_time'] = 5*60
        self.params['neutr_time'] = 5*60
        self.params['dry_time'] = 20*60
        self.params['transfer_time'] = 60 # transport from location to location (baths, input and output)
        self.params['verbose'] = False
        self.params.update(_params)        
        
        if (self.params['verbose']):
            print str(self.env.now) + " - [BatchTex][" + self.params['name'] + "] Added a batch texture machine"
        
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

    def report(self,output):
        string = "[BatchTex][" + self.params['name'] + "] Units processed: " + str(self.transport2.transport_counter - self.output.container.level)
        output.sig.emit(string)
        
        for i in self.batchprocesses:
            string = "[BatchTex][" + self.params['name'] + "][" + self.batchprocesses[i].name + "] Idle time: " + str(np.round(self.batchprocesses[i].idle_time(),1)) + " %"
            output.sig.emit(string)