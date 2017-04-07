# -*- coding: utf-8 -*-
from batchlocations.WaferSource import WaferSource
from batchlocations.WaferStacker import WaferStacker
from batchlocations.WaferUnstacker import WaferUnstacker
from batchlocations.Operator import Operator
from batchlocations.WaferBin import WaferBin
from batchlocations.BatchTex import BatchTex
from batchlocations.BatchClean import BatchClean
from batchlocations.TubeFurnace import TubeFurnace
from batchlocations.SingleSideEtch import SingleSideEtch
from batchlocations.TubePECVD import TubePECVD
from batchlocations.PrintLine import PrintLine
from batchlocations.Buffer import Buffer
from batchlocations.IonImplanter import IonImplanter
from batchlocations.SpatialALD import SpatialALD
from batchlocations.InlinePECVD import InlinePECVD
from batchlocations.PlasmaEtcher import PlasmaEtcher
import simpy
from PyQt5 import QtCore
import pandas as pd
#from random import shuffle
import time

class StringSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class ListSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(list)
        
class RunSimulationThread(QtCore.QObject):
    
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        
        self.stop_simulation = False        
        self.signal = StringSignal()        
        self.output = StringSignal()
        self.util = ListSignal()
        self.prod_rates_df = pd.DataFrame() # for storing production rates

    def replace_for_real_instances(self):

        ### Replace string elements in production line definition for real class instances ###
        for i, value in enumerate(self.batchlocations):
            # replace class names for real class instances in the same list
            # simpy env, message output link, settings dictionary
            if (self.batchlocations[i][0] == "WaferSource"):
                self.batchlocations[i] = WaferSource(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "WaferStacker"):
                self.batchlocations[i] = WaferStacker(self.env,self.output,self.batchlocations[i][1])                
            elif (self.batchlocations[i][0] == "WaferUnstacker"):
                self.batchlocations[i] = WaferUnstacker(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchTex"):
                self.batchlocations[i] = BatchTex(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchClean"):
                self.batchlocations[i] = BatchClean(self.env,self.output,self.batchlocations[i][1])                
            elif (self.batchlocations[i][0] == "TubeFurnace"):
                self.batchlocations[i] = TubeFurnace(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "SingleSideEtch"):
                self.batchlocations[i] = SingleSideEtch(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "TubePECVD"):
                self.batchlocations[i] = TubePECVD(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "PrintLine"):
                self.batchlocations[i] = PrintLine(self.env,self.output,self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "WaferBin"):
                self.batchlocations[i] = WaferBin(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "Buffer"):
                self.batchlocations[i] = Buffer(self.env,self.output,self.batchlocations[i][1])                 
            elif (self.batchlocations[i][0] == "IonImplanter"):
                self.batchlocations[i] = IonImplanter(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "SpatialALD"):
                self.batchlocations[i] = SpatialALD(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "InlinePECVD"):
                self.batchlocations[i] = InlinePECVD(self.env,self.output,self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "PlasmaEtcher"):
                self.batchlocations[i] = PlasmaEtcher(self.env,self.output,self.batchlocations[i][1])

        for i, value in enumerate(self.locationgroups):
            # replace batchlocation number indicators for references to real class instances
            for j in range(len(self.locationgroups[i])):
                self.locationgroups[i][j] = self.batchlocations[self.locationgroups[i][j]]           

        for i, value in enumerate(self.batchconnections):
            # replace locationgroup number indicators for references to real class instances
            self.batchconnections[i][0] = self.locationgroups[self.batchconnections[i][0][0]][self.batchconnections[i][0][1]]
            self.batchconnections[i][1] = self.locationgroups[self.batchconnections[i][1][0]][self.batchconnections[i][1][1]]

        for i, value in enumerate(self.operators):
            # replace batchconnection number indicators for references to real class instances
            # also replace operator list elements for new class instances
            tmp_batchconnections = {}
        
            for j in range(len(self.operators[i][0])):
                tmp_batchconnections[j] = self.batchconnections[self.operators[i][0][j]]

            self.operators[i] = Operator(self.env,tmp_batchconnections,self.output,self.operators[i][1])

        # Add all the cassettes to the source batchlocations
        source_group = len(self.locationgroups)-1
        
        for i in range(len(self.cassette_loops)):          
            for j in range(self.cassette_loops[i][2]):
                self.locationgroups[source_group][i].input.input.put(j)

#        print(self.batchlocations)
#        print(self.locationgroups)
#        print(self.batchconnections)
#        print(self.operators)
#        print(self.cassette_loops)

    def add_cassette_loops(self):
        # tell all tools in each cassette loop what cassette size they have and whether they
        # are the begin or end of a loop
        
        for i in range(len(self.cassette_loops)):

            for j in range(self.cassette_loops[i][0],self.cassette_loops[i][1]+1):
                for k in self.locationgroups[j]:                    
                    self.batchlocations[k][1]['cassette_size'] = self.cassette_loops[i][3]
            
            for l in self.locationgroups[self.cassette_loops[i][0]]:
                self.batchlocations[l][1]['loop_begin'] = True

            for m in self.locationgroups[self.cassette_loops[i][1]]:
                self.batchlocations[m][1]['loop_end'] = True                                   

        # generate cassette sources
        first_source_location = len(self.batchlocations)
        source_group = len(self.locationgroups)
        self.locationgroups.append([])
                                
        for i in range(len(self.cassette_loops)):
            self.batchlocations.append(["Buffer", {'max_cassette_no' : self.cassette_loops[i][2], 'name' : str(i)}])
            self.locationgroups[source_group].append(first_source_location+i)
        
        first_source_batchconnection = len(self.batchconnections)

#        print(self.batchlocations)
#        print(self.locationgroups)

        # add connections from and to sources
        for i in range(len(self.cassette_loops)):
            transport_time = self.cassette_loops[i][4]
            time_per_unit = self.cassette_loops[i][5]
            min_units = self.cassette_loops[i][6]
            max_units = self.cassette_loops[i][7]
            return_conn = True

            # add connections from cassette sources to loop beginning
            for j in range(len(self.locationgroups[self.cassette_loops[i][0]])):
                self.batchconnections.append([[source_group,i],[self.cassette_loops[i][0],j],
                                              transport_time,time_per_unit,min_units,max_units,return_conn])

            # add connections from loop endings to cassette sources
            for k in range(len(self.locationgroups[self.cassette_loops[i][1]])):
                self.batchconnections.append([[self.cassette_loops[i][1],k],[source_group,i],
                                              transport_time,time_per_unit,min_units,max_units,return_conn])
        
        # add source connections to operators that are already responsible for the same tools
        for i in range(first_source_batchconnection,len(self.batchconnections)):
            if self.batchconnections[i][0][0] == source_group: # if it is source > tool connection
                for j in range(len(self.operators)):
                    for k in self.operators[j][0]:
                        if self.batchconnections[k][0] == self.batchconnections[i][1]:
                            self.operators[j][0].append(i) # add multiple times to increase priority

            else: # if it is tool > source connection
                for j in range(len(self.operators)):
                    for k in self.operators[j][0]:
                        if self.batchconnections[k][1] == self.batchconnections[i][0]:
                            self.operators[j][0].append(i)                          
        
        for i in range(len(self.operators)):
            self.operators[i][0] = sorted(list(set(self.operators[i][0]))) # make connection lists unique

#        print(self.batchconnections)
#        print(self.operators)

    def sanity_check(self):
        
        not_approved = False
        
        for i in range(len(self.locationgroups[-1])):
            location = self.locationgroups[-1][i]

            if (self.batchlocations[location][0] == "PrintLine"):
                continue
            
            if self.batchlocations[location][0] == "WaferBin":
                continue
            
            not_approved = True
        
        return not_approved

    @QtCore.pyqtSlot()
    def run(self):
        profiling_mode = self.params['profiling_mode']
        time_limit = self.params['time_limit']

        if profiling_mode and (time_limit < 3601):
            self.output.sig.emit("Profiling mode requires longer simulation duration.")
            self.signal.sig.emit('Simulation aborted')
            return

        if self.sanity_check():
            self.output.sig.emit("Production line needs to end with printlines and/or waferbins.")
            self.signal.sig.emit('Simulation aborted')          
            return

        if len(self.cassette_loops) == 0:
            self.output.sig.emit("Production line requires at least one cassette loop.")
            self.signal.sig.emit('Simulation aborted')          
            return            

        self.env = simpy.Environment() # do not put in init; need a new one for every simulation    
        
        self.add_cassette_loops()         
        self.replace_for_real_instances()
            
        start_time = time.clock()
    
        if profiling_mode: # prepare production data storage entities
            
            columns = []
            for i in range(len(self.batchlocations)):
                columns.append("[" + str(self.batchlocations[i].__class__.__name__) + "][" + str(self.batchlocations[i].params['name']) + "]")           

            self.prod_rates_df = pd.DataFrame(columns=columns)
            
            prev_prod_volumes = []
            for i in range(len(self.batchlocations)):
                prev_prod_volumes.append(0)            

        ### Calculate time steps needed ###
        no_hourly_updates = time_limit // (60*60)
        hourly_updates = []
        for i in range(0,no_hourly_updates):
            hourly_updates.append((i+1)*60*60)
                
        percentage_updates = []
        for i in range(0,10):
            percentage_updates.append(round((i+1) * time_limit / 10))
                
        updates_list = hourly_updates + percentage_updates
        updates_list = set(updates_list)
        updates_list = sorted(updates_list)
        hourly_updates = set(hourly_updates)
        percentage_updates = set(percentage_updates)

        ### Run simulation ###

        string = "Simulation started "
        if profiling_mode:
            string += "in profiling mode "
        string += "with " + str(time_limit // (60*60)) + " hour duration"
        self.output.sig.emit(string)

        prev_production_volume_update = 0
        prev_percentage_time = self.env.now

        for i in updates_list:
            
            if(self.stop_simulation):
                string = "Stopped at "  + str(int(self.env.now // 3600)) + " hours"
                self.output.sig.emit(string) 
                break

            #try:
            self.env.run(until=i)
            #except Exception as inst:
            #    print(inst)

            if (i == time_limit):                
                string = "Finished at "  + str(int(self.env.now // 3600)) + " hours"
                self.output.sig.emit(string)
                break

            if (i in percentage_updates):

                l_loc = len(self.locationgroups)-2 # second to last locationgroup

                percentage_production_volume_update = 0
                for j in range(len(self.locationgroups[l_loc])):
                    percentage_production_volume_update += self.locationgroups[l_loc][j].output.container.level
   
                percentage_wph_update = (percentage_production_volume_update - prev_production_volume_update)
                percentage_wph_update = 3600 * percentage_wph_update / (self.env.now - prev_percentage_time)                

                # float needed for very large integer division                
                string = str(round(100*float(i)/time_limit)) + "% progress - " + str(round(i/3600,1)) + " hours / "
                string += str(percentage_production_volume_update) + " produced (" + str(int(percentage_wph_update)) + " wph)"
                self.output.sig.emit(string)

                prev_percentage_time = self.env.now
                prev_production_volume_update = percentage_production_volume_update

            if profiling_mode and (i in hourly_updates):

                prod_volumes = []                
                for i in range(len(self.batchlocations)):
                    prod_volumes.append(self.batchlocations[i].prod_volume())

                prod_rates = []
                for i in range(len(self.batchlocations)):
                    if not isinstance(self.batchlocations[i],Buffer):
                        prod_rates.append(prod_volumes[i]-prev_prod_volumes[i])
                    else:
                        # not really a production rate; just current buffer volume
                        prod_rates.append(prod_volumes[i])

                self.prod_rates_df.loc[len(self.prod_rates_df)] = prod_rates

                prev_prod_volumes = prod_volumes

        end_time = time.clock()
        
        if profiling_mode:
            self.prod_rates_df.index += 1
            # set index name to time in hours; has to be after changing index values
            self.prod_rates_df.index.name = "Time [hours]" 

        ### Generate summary output in log tab ###
        for i, value in enumerate(self.batchlocations):
            self.batchlocations[i].report()

        for i, value in enumerate(self.operators):
            self.operators[i].report()

        ### Generate utilization output for special tab ###
        utilization_list = []
        for i, value in enumerate(self.batchlocations):
            if len(self.batchlocations[i].utilization):
                utilization_list.append(self.batchlocations[i].utilization)
                
        for i, value in enumerate(self.operators):
            if len(self.operators[i].utilization):
                utilization_list.append(self.operators[i].utilization)
                
        self.util.sig.emit(utilization_list)

        ### Calculate sum of all produced cells ###
        prod_vol = 0
        l_loc = len(self.locationgroups)-2
        for i in range(len(self.locationgroups[l_loc])): # second to last locationgroup
            prod_vol += self.locationgroups[l_loc][i].output.container.level

        self.output.sig.emit("Production volume: " + str(prod_vol))
        self.output.sig.emit("Average throughput (WPH): " + str(int(3600*prod_vol/self.env.now)))

        for i in range(len(self.locationgroups[-1])): # last locationgroup
            buffer_content = len(self.locationgroups[-1][i].input.input.items)
            self.output.sig.emit("Cassette source buffer content for loop " + str(i) + ": " + str(buffer_content))
        
        sim_time = end_time-start_time
        if sim_time < 60:            
            self.output.sig.emit("Simulation time: " + str(round(sim_time,1)) + " seconds")
        elif sim_time < 3600:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//60)) + " minutes " + str(int(sim_time%60)) + " seconds")
        else:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//3600)) + " hours "+ str(int(sim_time%3600//60)) + " minutes " + str(int(sim_time%3600%60)) + " seconds")
        
        self.signal.sig.emit('Simulation finished')      