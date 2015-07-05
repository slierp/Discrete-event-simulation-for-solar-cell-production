# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchTransport import BatchTransport
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

"""

    Input buffer - tuneable size but default 8 cassettes
    Two loadlocks for two cassettes each
    Two processing belts
    Two buffer cassettes
    Output buffer - the same size as the input buffer
    One set of automation moves cassettes between the buffers and the loadlocks.
    Another set of automation puts and removes wafers from the belt (this probably doesn't exist in the real tool)

"""

class IonImplanter(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):    
        QtCore.QObject.__init__(self)
     
        self.env = _env
        self.output_text = _output
        self.idle_times = []        
        self.utilization = []       
        
        self.params = {}
        self.params['specification'] = "DO NOT USE\n"
        self.params['specification'] += "IonImplanter consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Two loadlocks for two cassettes each\n"
        self.params['specification'] += "- Two processing belts\n"
        self.params['specification'] += "- Two buffer cassettes\n"
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "Cassettes are loaded into the loadlocks, which are "
        self.params['specification'] += "then held for a set time (for evacuation). Subsequently, the "
        self.params['specification'] += "wafers are processed on belts and enter into buffer cassettes. "
        self.params['specification'] += "When the buffer cassette is full, the wafers return on the same belt "
        self.params['specification'] += "to the loadlock. After a set time (for repressurization) the cassettes "
        self.params['specification'] += "are placed in the output buffer.\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "There is a downtime procedure defined for the whole tool, during which "
        self.params['specification'] += "maintenance is performed."

        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual tool"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"       
        self.params['max_cassette_no'] = 5
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and the same number at output"
        self.params['batch_size'] = 100
        self.params['batch_size_desc'] = "Number of units in a single process batch"         
        self.params['transfer0_time'] = 60
        self.params['transfer0_time_desc'] = "Time for single transfer by transporter (seconds)"        
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)         
        
        #self.transport_counter = 0
        #self.start_time = self.env.now
        #self.first_run = True
        #self.process_counter = 0      
        
#        #if (self.params['verbose']): #DEBUG
#        #    string = str(self.env.now) + " [IonImplanter][" + self.params['name'] + "] Added an ion implanter" #DEBUG
#        #    self.output_text.sig.emit(string) #DEBUG
        
        ### Input buffer ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ## Load locks ##
        self.batchprocesses = []
        for i in range(0,1):
            process_params = {}
            process_params['name'] = "ll" + str(i)
            process_params['batch_size'] = self.params['batch_size']
            process_params['process_time'] = 120
#            process_params['verbose'] = self.params['verbose'] #DEBUG
            self.batchprocesses.append(BatchProcess(self.env,self.output_text,process_params))

        ### Output buffer ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Load-in transport ###
        batchconnections = []

        for i in range(0,1):
            batchconnections.append([self.input,self.batchprocesses[i],self.params['transfer0_time']])
        
        for i in range(0,1):
            batchconnections.append([self.batchprocesses[i],self.output,self.params['transfer0_time']])

        transport_params = {}
        transport_params['name'] = "ll0"
        transport_params['batch_size'] = self.params['batch_size']
#        transport_params['verbose'] = self.params['verbose'] #DEBUG      
        self.transport0 = BatchTransport(self.env,batchconnections,self.output_text,transport_params)        

    def report(self):
        #string = "[IonImplanter][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        #self.output_text.sig.emit(string)

        self.utilization.append("IonImplanter")
        self.utilization.append(self.params['name'])
        self.utilization.append(self.nominal_throughput())
        #production_volume = self.transport_counter - self.output.container.level
        #production_hours = (self.env.now - self.start_time)/3600
        #self.utilization.append(100*(production_volume/production_hours)/self.nominal_throughput())               

        #for i in range(len(self.idle_times_internal)):
        #    if self.first_run:
        #        idle_time = 100.0
        #    else:
        #        idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time)
        #    self.utilization.append(["l" + str(i),round(idle_time,1)])

    def run_loadlock_load_in(self):
        return

    def run_loadlock_load_out(self):
        return

    def nominal_throughput(self):       
        return 0