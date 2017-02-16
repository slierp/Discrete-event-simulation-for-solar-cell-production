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

    def make_unique(self,nonunique):
        unique = []
        for x in nonunique:
            if x not in unique:
                unique.append(x)
        unique.sort()
        return unique

    def replace_for_real_instances(self):        
   
        ### Replace string elements in production line definition for real class instances ###
        for i, value in enumerate(self.batchlocations):
            # replace class names for real class instances in the same list
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

    @QtCore.pyqtSlot()
    def run(self):
        
        start_time = time.clock()
                
        self.env = simpy.Environment()
        self.replace_for_real_instances() 

        ### Calculate time steps needed ###
        no_hourly_updates = self.params['time_limit'] // (60*60)
        hourly_updates = []
        for i in range(0,no_hourly_updates):
            hourly_updates.append((i+1)*60*60)
        
        percentage_updates = []
        for i in range(0,10):
            percentage_updates.append((i+1) * self.params['time_limit'] / 10)    
                
        updates_list = hourly_updates + percentage_updates
        updates_list = self.make_unique(updates_list)

        self.output.sig.emit("Simulation started with " + str(self.params['time_limit'] // (60*60)) + " hour duration")

        ### Run simulation ###
        prev_production_volume_update = 0
        prev_percentage_time = self.env.now
        
        for i in updates_list:
            if(self.stop_simulation):
                string = "Stopped at "  + str(int(self.env.now // 3600)) + " hours"
                self.output.sig.emit(string) 
                break

            self.env.run(until=i)
            
            if (i == self.params['time_limit']):                
                string = "Finished at "  + str(int(self.env.now // 3600)) + " hours"
                self.output.sig.emit(string)                            
            elif i in percentage_updates:
                
                l_loc = len(self.locationgroups)
                percentage_production_volume_update = 0
                for j in range(len(self.locationgroups[l_loc-1])):
                    percentage_production_volume_update += self.locationgroups[l_loc-1][j].output.container.level
                    
                percentage_wph_update = (percentage_production_volume_update - prev_production_volume_update)
                percentage_wph_update = 3600 * percentage_wph_update / (self.env.now - prev_percentage_time)                
                
                # float needed for very large integer division                
                string = str(round(100*float(i)/self.params['time_limit'])) + "% progress - " + str(round(i/3600,1)) + " hours / "
                string += str(percentage_production_volume_update) + " produced (" + str(int(percentage_wph_update)) + " wph)"
                self.output.sig.emit(string)

                prev_percentage_time = self.env.now
                prev_production_volume_update = percentage_production_volume_update

        end_time = time.clock()

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
        l_loc = len(self.locationgroups)
        for i in range(len(self.locationgroups[l_loc-1])):
            prod_vol += self.locationgroups[l_loc-1][i].output.container.level

        self.output.sig.emit("Production volume: " + str(prod_vol))
        self.output.sig.emit("Average throughput (WPH): " + str(int(3600*prod_vol/self.env.now)))
        
        sim_time = end_time-start_time
        if sim_time < 60:            
            self.output.sig.emit("Simulation time: " + str(round(sim_time,1)) + " seconds")
        elif sim_time < 3600:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//60)) + " minutes " + str(int(sim_time%60)) + " seconds")
        else:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//3600)) + " hours "+ str(int(sim_time%3600//60)) + " minutes " + str(int(sim_time%3600%60)) + " seconds")
        
        self.signal.sig.emit('Simulation finished')
    
    @QtCore.pyqtSlot()
    def run_with_profiling(self):
        
        if (self.params['time_limit'] < 3601):
            self.output.sig.emit("Profiling mode requires longer simulation duration.")
            self.signal.sig.emit('Simulation aborted')
            return

        start_time = time.clock()
        
        self.env = simpy.Environment()        
        self.replace_for_real_instances()
        curr_time = 0

        columns = []
        for i in range(len(self.batchlocations)):
            columns.append("[" + str(self.batchlocations[i].__class__.__name__) + "][" + str(self.batchlocations[i].params['name']) + "]")

        self.prod_rates_df = pd.DataFrame(columns=columns)

        prev_prod_volumes = []
        for i in range(len(self.batchlocations)):
            prev_prod_volumes.append(0)
        
        ### Run simulation ###
        self.output.sig.emit("Simulation started in profiling mode with " + str(self.params['time_limit'] // (60*60)) + " hour duration")

        prev_production_volume_update = 0
        prev_time = self.env.now

        while True:
            if(self.stop_simulation):
                string = "Stopped at "  + str(int(self.env.now // 3600)) + " hours"
                self.output.sig.emit(string) 
                break                
            
            curr_time += 3600            
            self.env.run(curr_time)

            if ((curr_time % 36000) == 0):                
                l_loc = len(self.locationgroups)
                production_volume_update = 0
                for j in range(len(self.locationgroups[l_loc-1])):
                    production_volume_update += self.locationgroups[l_loc-1][j].output.container.level
                    
                wph_update = (production_volume_update - prev_production_volume_update)
                wph_update = 3600 * wph_update / (self.env.now - prev_time)                
                
                # float needed for very large integer division                
                string = str(int(self.env.now // 3600)) + " hours progress - "
                string += str(production_volume_update) + " produced (" + str(int(wph_update)) + " wph)"
                self.output.sig.emit(string)

                prev_time = self.env.now
                prev_production_volume_update = production_volume_update                
                        
            prod_volumes = []
            for i in range(len(self.batchlocations)):
                prod_volumes.append(self.batchlocations[i].prod_volume())

            prod_rates = []
            for i in range(len(self.batchlocations)):
                 prod_rates.append((prod_volumes[i]-prev_prod_volumes[i])/3600)
                 
            self.prod_rates_df.loc[len(self.prod_rates_df)] = prod_rates
            
            prev_prod_volumes = prod_volumes
            
            if (self.env.now >= self.params['time_limit']):
                break

        end_time = time.clock()

        self.prod_rates_df.index += 1
        self.prod_rates_df.index.name = "Time [hours]" # set index name to time in hours; has to be after changing index values

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
        l_loc = len(self.locationgroups)
        for i in range(len(self.locationgroups[l_loc-1])):
            prod_vol += self.locationgroups[l_loc-1][i].output.container.level
        
        self.output.sig.emit("Production volume: " + str(prod_vol))
        self.output.sig.emit("Average throughput (WPH): " + str(int(3600*prod_vol/self.env.now)))        

        sim_time = end_time-start_time
        if sim_time < 60:            
            self.output.sig.emit("Simulation time: " + str(round(sim_time,1)) + " seconds")
        elif sim_time < 3600:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//60)) + " minutes " + str(int(sim_time%60)) + " seconds")
        else:
            self.output.sig.emit("Simulation time: " + str(int(sim_time//3600)) + " hours "+ str(int(sim_time%3600//60)) + " minutes " + str(int(sim_time%3600%60)) + " seconds")
        
        self.signal.sig.emit('Simulation finished')        