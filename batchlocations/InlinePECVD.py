# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import collections

"""
TODO

Make separate versions of this tool:
- InlinePECVD for single ARC
- InlinePECVD (DS) for double-sided nitride
- InlinePECVD (PERC) for AlOx plus double-sided nitride

"""

class InlinePECVD(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.utilization = []
        self.diagram = """blockdiag {} """          
        
        self.params = {}
        self.params['specification'] = "InlinePECVD consists of:\n"
        self.params['specification'] += "- Input container\n"
        self.params['specification'] += "- Load-in conveyor\n"
        self.params['specification'] += "- Tray load/unload position\n"
        self.params['specification'] += "- Loadlock chamber for load-in\n"
        self.params['specification'] += "- Buffer for pre-heating\n"
        self.params['specification'] += "- One process chamber\n"
        self.params['specification'] += "- Buffer for cool-down\n"
        self.params['specification'] += "- Loadlock chamber for load-out\n"       
        self.params['specification'] += "- Load-out conveyor\n"        
        self.params['specification'] += "- Output container\n"
        self.params['specification'] += "\n"
        self.params['specification'] += "The machine accepts cassettes which are unloaded one wafer at a time onto a belt. "
        self.params['specification'] += "The tray is loaded one belt row at a time. The tray subsequently goes through the machine. "
        self.params['specification'] += "After the deposition(s) the tray is returned to the original position. "
        self.params['specification'] += "Wafers are unloaded one row at a time onto the load-out conveyor and then "
        self.params['specification'] += "placed back into cassettes.\n"
        
        self.params['name'] = ""
        self.params['name_desc'] = "Name of the individual batch location"
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = "Number of units in a single cassette"
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = "Number of cassette positions at input and output"
        self.params['time_new_cassette'] = 10
        self.params['time_new_cassette_desc'] = "Time for putting an empty cassette into a loading position (seconds)"

        self.params['no_trays'] = 4
        self.params['no_trays_desc'] = "Number of trays that cycle through the system"
        self.params['no_tray_rows'] = 6
        self.params['no_tray_rows_desc'] = "Number of units in one row in the tray (equal to number of units on conveyors)"
        self.params['no_tray_columns'] = 4
        self.params['no_tray_columns_desc'] = "Number of units in one column in the tray"
        self.params['tray_length'] = 1.1
        self.params['tray_length_desc'] = "Length of tray (meters)"        
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = "Time for one wafer to progress one unit distance on main conveyor (seconds)"

        self.params['buffer_length'] = 1.0
        self.params['buffer_length_desc'] = "Length of each pre-heat and cool-down buffer (meters)"  
        self.params['deposition_unit_length'] = 2.0
        self.params['deposition_unit_length_desc'] = "Length of each deposition unit (meters)" 
        self.params['loadlock_length'] = 1.0
        self.params['loadlock_length_desc'] = "Length of each load lock (meters)"       

        self.params['chamber_speed'] = 5.0
        self.params['chamber_speed_desc'] = "Tray speed in process chamber (meters per minute)"     
        
#        self.params['verbose'] = False #DEBUG
#        self.params['verbose_desc'] = "Enable to get updates on various functions within the tool" #DEBUG
        self.params.update(_params)
        
        self.time_step = self.params['time_step']
        self.transport_counter = 0
        
#        if (self.params['verbose']): #DEBUG     
#            string = str(self.env.now) + " - [InlinePECVD][" + self.params['name'] + "] Added an inline PECVD tool" #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ### Conveyors ###
        self.input_conveyor = collections.deque([False for rows in range(self.params['no_tray_rows'])])
        self.output_conveyor = collections.deque([False for rows in range(self.params['no_tray_rows'])])
        
        ### Trays ###
        trays = []
        for i in range(self.params['no_trays']):
            trays.append(BatchContainer(self.env,"tray" + str(i),self.params['no_tray_rows']*self.params['no_tray_columns'],1))
        
        ### Output ###
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])

        ### Start processes ###
        self.env.process(self.run_load_in_conveyor())
        self.env.process(self.run_load_out_conveyor())

    def report(self):
        string = "[InlinePECVD][" + self.params['name'] + "] Units processed: " + str(self.transport_counter)
        self.output_text.sig.emit(string)         

    def prod_volume(self):
        return self.transport_counter
        
    def run_load_in_conveyor(self):
        wafer_counter = 0
        restart = True # start with new cassette
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        time_step = self.params['time_step']
        wafer_available = False
#        verbose = self.params['verbose'] #DEBUG
        
        while True:
            
            if (not wafer_available): # if we don't already have a wafer in position try to get one
                yield self.input.container.get(1)
                wafer_available = True

            if (restart):
                #time delay for loading new cassette if input had been completely empty
                yield self.env.timeout(time_new_cassette - time_step)
                restart = False            
            
            if (not self.input_conveyor[0]):                 
                self.input_conveyor[0] = True
                wafer_available = False
                wafer_counter += 1

                if(not self.input_conveyor[-1]):
                    self.input_conveyor.rotate(1)                                
                
#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Put wafer from cassette on load-in conveyor" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
                    
            if (wafer_counter == cassette_size):
                # if current cassette is empty then delay to load a new cassette                                   
                wafer_counter = 0                
                restart = True
                
            yield self.env.timeout(time_step)                

    def run_tray_load_in(self):
        return
        current_tray = 0

        while True:

            self.trays[current_tray].container.request()
            
            if(self.input_conveyor[-1]): # if input belt is full
            
                return
                
            current_tray += 1
            
            
    def run_load_out_conveyor(self):
        wafer_counter = 0
        restart = True # start with new cassette
        time_new_cassette = self.params['time_new_cassette']
        cassette_size = self.params['cassette_size']
        time_step = self.params['time_step']
#        verbose = self.params['verbose'] #DEBUG
        
        while True:            

            if (restart):
                # time delay for loading new cassette if output cassette had been full
                yield self.env.timeout(time_new_cassette - time_step)
                restart = False 
            
            if (self.output_conveyor[0]): 
                self.output_conveyor[0] = False               
                yield self.output.container.put(1)
                wafer_counter += 1

#                if (verbose): #DEBUG
#                    string = str(self.env.now) + " [InlinePECVD][" + self.params['name'] + "] Put wafer from load-out conveyor into cassette" #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG                
                
            else:               
                self.output_conveyor.rotate(-1)                                              
                    
            if (wafer_counter == cassette_size):
                # if current cassette is full then delay to load a new cassette                                   
                wafer_counter = 0                
                restart = True                            

            yield self.env.timeout(time_step)