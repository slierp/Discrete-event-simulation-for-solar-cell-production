# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO
Add IV measurement automation

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
#import simpyx as simpy
import simpy
import numpy as np

class PrintLine(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        self.idle_times = []
        
        self.params = {}
        self.params['specification'] = self.tr("PrintLine consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- Print and dry stations\n")
        self.params['specification'] += self.tr("- Firing furnace\n")
        self.params['specification'] += self.tr("- Output container (infinite)\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("The machine accepts cassettes which are unloaded one unit at a time. ")
        self.params['specification'] += self.tr("Each wafer then travels to a number of printers and dryers, ")
        self.params['specification'] += self.tr("before entering a firing furnace. ")
        self.params['specification'] += self.tr("Lastly, all units are placed in an infinitely sized container.")
        
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input")
        self.params['units_on_belt_input'] = 8
        self.params['units_on_belt_input_desc'] = self.tr("Number of units that fit on the belt between wafer source and printer")
        
        self.params['time_step'] = 1.0
        self.params['time_step_desc'] = self.tr("Time for one unit to progress one position (seconds)")
        self.params['time_cassette_to_belt'] = 1.0
        self.params['time_cassette_to_belt_desc'] = self.tr("Time for placing one unit onto the first belt (seconds)")
        self.params['time_print'] = 2.0
        self.params['time_print_desc'] = self.tr("Time to print one wafer (seconds)")
        self.params['time_dry'] = 90
        self.params['time_dry_desc'] = self.tr("Time for one wafer to go from printer to dryer and ")
        self.params['time_dry_desc'] += self.tr("to next input (printing or firing) (seconds)")
        
        self.params['no_print_steps'] = 3
        self.params['no_print_steps_desc'] = self.tr("Number of print and dry stations")
        
        self.params['firing_tool_length'] = 7.0
        self.params['firing_tool_length_desc'] = self.tr("Distance between firing furnace input and output (meters)")
        self.params['firing_belt_speed'] = 5.0 # 5 is roughly 200 ipm
        self.params['firing_belt_speed_desc'] = self.tr("Speed at which all units travel (meters per minute)")
        self.params['firing_unit_distance'] = 0.2
        self.params['firing_unit_distance_desc'] = self.tr("Minimal distance between wafers (meters)")
        
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)
        
        if (self.params['verbose']):               
            string = str(self.env.now) + " - [PrintLine][" + self.params['name'] + "] Added a print line"
            self.output_text.sig.emit(string)

        ### Input ###
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        
        ### Array of zeroes represents dryers ###
        self.dryers = np.zeros((self.params['no_print_steps'],self.params['time_dry']))

        ### List represents single lane firing furnace ###
        self.firing_lane = np.zeros((1,self.params['firing_tool_length']//self.params['firing_unit_distance']))
        
        ### Infinite output container ###
        self.output = InfiniteContainer(self.env,"output")

        self.start_time = []
        self.first_run = []
        self.idle_times_internal = []
        for i in np.arange(self.params['no_print_steps']+1): # plus one for the firing furnace
            self.idle_times_internal.append(0)
            self.first_run.append(True)
            self.start_time.append(0)

        self.next_step = {} # trigger events
        self.belts = {} # belts preceeding printers
        self.inputs = {} # cassette-like input before belts

        for i in np.arange(self.params['no_print_steps']):
            self.next_step[i] = self.env.event()
            self.belts[i] = BatchContainer(self.env,"belt_input",self.params['units_on_belt_input'],1)
            self.inputs[i] = BatchContainer(self.env,"input",self.params['cassette_size'],1) # buffer inside printer line            
            self.env.process(self.run_belt(i))
            self.env.process(self.run_printer(i))

        self.env.process(self.run_dryers())
        self.env.process(self.run_dryer_load_out())
        
        self.env.process(self.run_firing_lane())
        self.env.process(self.run_firing_load_out())

    def report(self):
        string = "[PrintLine][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)
        self.output_text.sig.emit(string)
        
        idle_item = []
        idle_item.append("PrintLine")
        idle_item.append(self.params['name'])
        for i in range(len(self.idle_times_internal)):
            if self.first_run[i]:
                idle_time = 100.0
            else:
                idle_time = 100.0*self.idle_times_internal[i]/(self.env.now-self.start_time[i])
            idle_item.append(["p" + str(i),np.round(idle_time,1)])
        
        idle_item[len(idle_item)-1][0] = "f0"
        self.idle_times.append(idle_item) 

    def run_belt(self, num):        
        while True:
            yield self.next_step[num]
                        
            if (num):
                yield self.inputs[num].container.get(1)
            else:                
                yield self.input.container.get(1)
                
            yield self.env.timeout(self.params['time_cassette_to_belt']) 
            yield self.belts[num].container.put(1)
            
            if (self.params['verbose']):
                string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Put wafer on printer belt " + str(num)
                self.output_text.sig.emit(string)
            
    def run_printer(self, num):        
        while True:
            if (not num):
                input_check = (self.input.container.level > 0)
            else:
                input_check = (self.inputs[num].container.level > 0)
            
            if (self.belts[num].space_available(1)) & (input_check):
                yield self.next_step[num].succeed()
                self.next_step[num] = self.env.event() # make new event

            if (not self.belts[num].space_available(1)) | ((not input_check) & (self.belts[num].container.level > 0)):
                # if belt is fully loaded print one
                # else if input is empty but still wafers present on belt, continue printing until empty
            
                if self.first_run[num]:
                    self.start_time[num] = self.env.now
                    self.first_run[num] = False            
            
                yield self.belts[num].container.get(1)
                yield self.env.timeout(self.params['time_print'])
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Printed a wafer on printer " + str(num)
                    self.output_text.sig.emit(string)
                    
                #self.dryers[num].insert(0,0)
                self.dryers[num][0] = 1
                
            else:
                # if not printing, delay for time needed to load one wafer
                yield self.env.timeout(self.params['time_step'])
                
                if not self.first_run[num]:
                    self.idle_times_internal[num] += self.params['time_step']

    def run_dryers(self):
        # Updates drying time for all wafers in dryers
        while True:            
            self.dryers = np.roll(self.dryers,1)
            yield self.env.timeout(1)              

    def run_dryer_load_out(self):
        # Places wafers into output when they have reached drying time
        while True:
            for i,row in enumerate(self.dryers):
                if row[-1]:
                    row[-1] = 0

                    if (i < (self.params['no_print_steps']-1)):
                        #go to next printer
                        yield self.inputs[i+1].container.put(1)
                    else:
                        # go to firing furnace
                        self.firing_lane[0][0] = 1
                        # yield time out to prevent loading wafers on top of each other?
                        
                    if (self.params['verbose']):
                        string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Dried a wafer on dryer " + str(i)
                        self.output_text.sig.emit(string)                        

            yield self.env.timeout(1)

    def run_firing_lane(self):
        # Updates position for all wafers in firing lane
        while True:                    
            self.firing_lane = np.roll(self.firing_lane,1)
            yield self.env.timeout(60*self.params['firing_unit_distance']/self.params['firing_belt_speed'])            

    def run_firing_load_out(self):
        # Places wafers into output when they have reached tool length
        while True:            
            if self.firing_lane[0][-1]:        
                self.firing_lane[0][-1] = 0
                yield self.output.container.put(1)
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Fired a wafer"
                    self.output_text.sig.emit(string)   
                
            yield self.env.timeout(1) #60*self.params['firing_unit_distance']/self.params['firing_belt_speed'])        
            
class InfiniteContainer(object):
    
    def __init__(self, env, name=""):        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)