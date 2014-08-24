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

    def __init__(self, env, name="", process_batch_size=400, cassette_size=100, max_cassette_no=8, process_time=20*60,
                 rinse_time=5*60, neutr_time=5*60, dry_time=20*60):    
        
        self.env = env
        self.name = name
        self.process_batch_size = process_batch_size
        self.cassette_size = cassette_size
        self.max_cassette_no = max_cassette_no
        self.process_time = process_time
        self.rinse_time = rinse_time
        self.neutr_time = neutr_time
        self.dry_time = dry_time
        self.transfer_time = 60
        print str(self.env.now) + " - [BatchTex][" + self.name + "] Added a batch texture machine"
        
        self.input = BatchContainer(self.env,"input",self.cassette_size,self.max_cassette_no)
        
        self.batchprocesses = {}
        self.batchprocesses[0] = BatchProcess(self.env,"tex0",self.process_batch_size,self.process_time)
        self.batchprocesses[1] = BatchProcess(self.env,"tex1",self.process_batch_size,self.process_time)
        self.batchprocesses[2] = BatchProcess(self.env,"tex2",self.process_batch_size,self.process_time)
        self.batchprocesses[3] = BatchProcess(self.env,"rinse0",self.process_batch_size,self.rinse_time)
        self.batchprocesses[4] = BatchProcess(self.env,"neutr",self.process_batch_size,self.neutr_time)
        self.batchprocesses[5] = BatchProcess(self.env,"rinse1",self.process_batch_size,self.rinse_time)
        self.batchprocesses[6] = BatchProcess(self.env,"dry0",self.process_batch_size,self.dry_time)
        self.batchprocesses[7] = BatchProcess(self.env,"dry1",self.process_batch_size,self.dry_time)
        self.batchprocesses[8] = BatchProcess(self.env,"dry2",self.process_batch_size,self.dry_time)
        
        self.output = BatchContainer(self.env,"output",self.cassette_size,self.max_cassette_no)

        batchconnections = {}
        # First check whether batch can be brought to rinse, because that has priority
        batchconnections[0] = [self.batchprocesses[0],self.batchprocesses[3],self.transfer_time]
        batchconnections[1] = [self.batchprocesses[1],self.batchprocesses[3],self.transfer_time]
        batchconnections[2] = [self.batchprocesses[2],self.batchprocesses[3],self.transfer_time]
        batchconnections[3] = [self.input,self.batchprocesses[0],self.transfer_time]
        batchconnections[4] = [self.input,self.batchprocesses[1],self.transfer_time]
        batchconnections[5] = [self.input,self.batchprocesses[2],self.transfer_time]
        self.transport0 = BatchTransport(self.env,batchconnections,"transport0",self.process_batch_size)

        batchconnections = {}
        # First check whether batch can be brought to rinse or output, because that has priority
        batchconnections[0] = [self.batchprocesses[4],self.batchprocesses[5],self.transfer_time]
        batchconnections[1] = [self.batchprocesses[3],self.batchprocesses[4],self.transfer_time]
        batchconnections[2] = [self.batchprocesses[5],self.batchprocesses[6],self.transfer_time]
        batchconnections[3] = [self.batchprocesses[5],self.batchprocesses[7],self.transfer_time]       
        batchconnections[4] = [self.batchprocesses[5],self.batchprocesses[8],self.transfer_time]  
        self.transport1 = BatchTransport(self.env,batchconnections,"transport1",self.process_batch_size)

        batchconnections = {}
        batchconnections[0] = [self.batchprocesses[6],self.output,self.transfer_time]
        batchconnections[1] = [self.batchprocesses[7],self.output,self.transfer_time]
        batchconnections[2] = [self.batchprocesses[8],self.output,self.transfer_time]
        self.transport2 = BatchTransport(self.env,batchconnections,"transport2",self.process_batch_size)

    def report(self):
        print "[BatchTex][" + self.name + "] Units processed: " + str(self.transport2.transport_counter - self.output.container.level)
        
        for i in self.batchprocesses:
            print "[BatchTex][" + self.name + "][" + self.batchprocesses[i].name + "] Idle time: " + str(np.round(self.batchprocesses[i].idle_time(),1)) + " %"        