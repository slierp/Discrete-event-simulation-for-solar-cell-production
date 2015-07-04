# -*- coding: utf-8 -*-
from __future__ import division
from batchlocations.WaferSource import WaferSource
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
import simpy
import pickle

class RunSimulation(object):
    
    def __init__(self,filename,time_limit=1):
        
        with open(filename) as f: # Pickle imports numpy so not compatible with PyPy and ShedSkin
            self.batchlocations,self.locationgroups,self.batchconnections,self.operators = pickle.load(f)

        #self.batchlocations = [] #tool class name, no of tools, dict with settings         
        #self.locationgroups = []
        #self.batchconnections = [] #[machine1,machine2,transport_time,time_per_unit]        
        #self.operators = []
        
        self.params = {}
        self.params['time_limit'] = time_limit*3600
        self.hourly_updates = []
        self.percentage_updates = []        
        self.updates_list = []
        
        self.env = simpy.Environment()
         
        #self.define_simulation()
        self.copy_definition()
        self.calculate_timesteps()
    
    """
    def define_simulation(self): # not used at the moment
        self.batchlocations.append(["WaferSource", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker", {'name' : '0'}])
        self.batchlocations.append(["WaferUnstacker",{'name' : '1'}])
        self.batchlocations.append(["BatchTex", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '0'}])
        self.batchlocations.append(["TubeFurnace", {'name' : '1'}])
        self.batchlocations.append(["Buffer", {'name' : '0'}])
        self.batchlocations.append(["SingleSideEtch", {'name' : '0'}])
        self.batchlocations.append(["TubePECVD", {'name' : '0'}])
        self.batchlocations.append(["TubePECVD", {'name' : '1'}])
        self.batchlocations.append(["PrintLine", {'name' : '0'}])
        self.batchlocations.append(["PrintLine", {'name' : '1'}])

        self.locationgroups.append([0])
        self.locationgroups.append([1, 2])
        self.locationgroups.append([3])
        self.locationgroups.append([4, 5])
        self.locationgroups.append([6])
        self.locationgroups.append([7])
        self.locationgroups.append([8, 9])
        self.locationgroups.append([10, 11])

        transport_time = 90 # time for actual transport of one or more units
        time_per_unit = 20 # added time per unit for loading/unloading on the machines (combined value for input and output stations)

        self.batchconnections.append([[0,0],[1,0],transport_time,time_per_unit])
        self.batchconnections.append([[0,0],[1,1],transport_time,time_per_unit])

        self.batchconnections.append([[1,0],[2,0],transport_time,time_per_unit])
        self.batchconnections.append([[1,1],[2,0],transport_time,time_per_unit])

        self.batchconnections.append([[2,0],[3,0],transport_time,time_per_unit])
        self.batchconnections.append([[2,0],[3,1],transport_time,time_per_unit])

        self.batchconnections.append([[3,0],[4,0],transport_time,time_per_unit])
        self.batchconnections.append([[3,1],[4,0],transport_time,time_per_unit])

        self.batchconnections.append([[4,0],[5,0],transport_time,time_per_unit])
    
        self.batchconnections.append([[5,0],[6,0],transport_time,time_per_unit])
        self.batchconnections.append([[5,0],[6,1],transport_time,time_per_unit])

        self.batchconnections.append([[6,0],[7,0],transport_time,time_per_unit])
        self.batchconnections.append([[6,0],[7,1],transport_time,time_per_unit])
        self.batchconnections.append([[6,1],[7,0],transport_time,time_per_unit])
        self.batchconnections.append([[6,1],[7,1],transport_time,time_per_unit])

        self.operators.append([[0,1],{'name' : '0'}])
        self.operators.append([[2,3],{'name' : '1'}])
        self.operators.append([[4,5],{'name' : '2'}])
        self.operators.append([[6,7],{'name' : '3'}])
        self.operators.append([[8],{'name' : '4'}])
        self.operators.append([[9,10],{'name' : '4'}])
        self.operators.append([[11,12,13,14],{'name' : '5'}])
    """

    def make_unique(self,nonunique):
        unique = []
        for x in nonunique:
            if x not in unique:
                unique.append(x)
        unique.sort()
        return unique

    def copy_definition(self):        

        ### Replace string elements in production line definition for real class instances ###
        for i, value in enumerate(self.batchlocations):
            # replace class names for real class instances in the same list
            if (self.batchlocations[i][0] == "WaferSource"):
                self.batchlocations[i] = WaferSource(self.env,"",self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "WaferUnstacker"):
                self.batchlocations[i] = WaferUnstacker(self.env,"",self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchTex"):
                self.batchlocations[i] = BatchTex(self.env,"",self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "BatchClean"):
                self.batchlocations[i] = BatchClean(self.env,"",self.batchlocations[i][1])                
            elif (self.batchlocations[i][0] == "TubeFurnace"):
                self.batchlocations[i] = TubeFurnace(self.env,"",self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "SingleSideEtch"):
                self.batchlocations[i] = SingleSideEtch(self.env,"",self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "TubePECVD"):
                self.batchlocations[i] = TubePECVD(self.env,"",self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "PrintLine"):
                self.batchlocations[i] = PrintLine(self.env,"",self.batchlocations[i][1]) 
            elif (self.batchlocations[i][0] == "WaferBin"):
                self.batchlocations[i] = WaferBin(self.env,"",self.batchlocations[i][1])
            elif (self.batchlocations[i][0] == "Buffer"):
                self.batchlocations[i] = Buffer(self.env,"",self.batchlocations[i][1])                 

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
        
            self.operators[i] = Operator(self.env,tmp_batchconnections,self.operators[i][1])   

    def calculate_timesteps(self):

        ### Calculate time steps needed ###
        no_hourly_updates = self.params['time_limit'] // (60*60)
        for i in range(0,no_hourly_updates):
            self.hourly_updates.append((i+1)*60*60)            
                    

        for i in range(0,10):
            self.percentage_updates.append((i+1) * self.params['time_limit'] / 10)    
                            
        self.updates_list = self.hourly_updates + self.percentage_updates
        self.updates_list = self.make_unique(self.updates_list)        

    def run(self):
        print "0% progress: 0 hours / 0 produced"
                    
        ### Run simulation ###
        prev_production_volume_update = 0
        prev_percentage_time = self.env.now
        for i in self.updates_list:
            #if(self.stop_simulation):
                #string = "Stopped at "  + str(np.round(self.env.now/3600,1)) + " hours"
                #self.output.sig.emit(string) 
                #break
            
            self.env.run(until=i)
                        
            if (i == self.params['time_limit']):                
                print "Finished at "  + str(round(self.env.now/3600,1)) + " hours"
            elif i in self.percentage_updates: #% (self.params['time_limit'] // 10) == 0):
                l_loc = len(self.locationgroups)
                percentage_production_volume_update = 0
                for j in range(len(self.locationgroups[l_loc-1])):
                    percentage_production_volume_update += self.locationgroups[l_loc-1][j].output.container.level
                                
                percentage_wph_update = (percentage_production_volume_update - prev_production_volume_update)
                percentage_wph_update = 3600 * percentage_wph_update / (self.env.now - prev_percentage_time)                
                            
                # float needed for very large integer division                
                string = str(round(100*float(i)/self.params['time_limit'])) + "% progress: " + str(round(i/3600,1)) + " hours / "
                string += str(percentage_production_volume_update) + " produced (" + str(int(percentage_wph_update)) + " wph)"
                print string
            
                prev_percentage_time = self.env.now
                prev_production_volume_update = percentage_production_volume_update

        ### Calculate sum of all produced cells ###
        prod_vol = 0
        l_loc = len(self.locationgroups)
        for i in range(len(self.locationgroups[l_loc-1])):
            prod_vol += self.locationgroups[l_loc-1][i].output.container.level
            
        print "Production volume: " + str(prod_vol)
        print "Average throughput (WPH): " + str(round(3600*prod_vol/self.params['time_limit']))
        print "Simulation finished"
