# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 08:38:24 2014

@author: rnaber

TODO

Implement shift changes, breaks, factory shut-downs...

"""

from __future__ import division
from PyQt4 import QtCore
import numpy as np

class Operator(QtCore.QObject):
    #Operator checks regularly whether he/she can perform a batch transfer action and then carries it out
        
    def __init__(self, _env, _batchconnections = None, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.batchconnections = _batchconnections

        self.params = {}
        self.params['specification'] = self.tr("An operator instance functions only as the transporter between batch locations. ")
        self.params['specification'] += self.tr("Each time interval it will try to do a transport between two locations that were assigned. ")
        self.params['specification'] += self.tr("If no transport was possible then it will wait a set amount of time before trying again.")
        
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual operator")        
        self.params['min_units'] = 1
        self.params['min_units_desc'] = self.tr("Not yet implemented")        
        self.params['wait_time'] = 60
        self.params['wait_time_desc'] = self.tr("Wait period between transport attempts (seconds)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on all actions of the operator")        
        self.params.update(_params)
        
        self.transport_counter = 0
        self.start_time = self.env.now
        self.idle_time = 0
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [Operator][" + self.params['name'] + "] Added an operator"
            self.output_text.sig.emit(string)
            
        self.env.process(self.run())        

    def run(self):
        continue_loop = False
        
        while True:
            for i in self.batchconnections:
                units_needed = self.batchconnections[i][1].input.buffer_size - self.batchconnections[i][1].input.container.level
                units_available = self.batchconnections[i][0].output.container.level
                
                if (units_needed >= units_available):
                    units_for_transport = units_available
                else:
                    units_for_transport = units_needed
                
                if (units_for_transport >= self.batchconnections[i][0].output.batch_size):
                    no_batches_for_transport = units_for_transport // self.batchconnections[i][0].output.batch_size
                    yield self.batchconnections[i][0].output.container.get(no_batches_for_transport*self.batchconnections[i][0].output.batch_size)
                    yield self.env.timeout(self.batchconnections[i][2] + self.batchconnections[i][3]*no_batches_for_transport)
                    self.transport_counter += no_batches_for_transport*self.batchconnections[i][0].output.batch_size
                    yield self.batchconnections[i][1].input.container.put(no_batches_for_transport*self.batchconnections[i][0].output.batch_size)
                    continue_loop = True

                    if (self.params['verbose']):
                        string = str(self.env.now) + " - [Operator][" + self.params['name'] + "] Batches transported: "
                        string += str(no_batches_for_transport)
                        self.output_text.sig.emit(string)                              

            if (continue_loop):
                continue_loop = False
                continue
            
            yield self.env.timeout(self.params['wait_time'])
            self.idle_time += self.params['wait_time']

    def report(self):        
        string = "[Operator][" + self.params['name'] + "] Units transported: " + str(self.transport_counter)
        self.output_text.sig.emit(string)
        
        if (self.params['verbose']):
            string = "[Operator][" + self.params['name'] + "] Transport time: " + str(np.round(100-100*self.idle_time/(self.env.now-self.start_time),1)) + " %"
            self.output_text.sig.emit(string)