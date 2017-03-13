# -*- coding: utf-8 -*-

    def report(self):        
        self.utilization.append("TubePECVD")
        self.utilization.append(self.params['name'])
        self.utilization.append(int(self.nominal_throughput()))
        production_volume = self.transport_counter
        production_hours = (self.env.now - self.furnace_start_time[0])/3600
        
        if (self.nominal_throughput() > 0) and (production_hours > 0):
            self.utilization.append(round(100*(production_volume/production_hours)/self.nominal_throughput(),1))        
        else:
            self.utilization.append(0)            

        self.utilization.append(self.transport_counter)
        
        for i in range(self.params['no_of_processes']):
            if ((self.env.now - self.furnace_start_time[0]) > 0):
                util = 100*(self.furnace_runs[i]*60*self.params['process_time'])/(self.env.now - self.furnace_start_time[0])
            else:
                util = 0
            self.utilization.append(["Tube " + str(i),round(util,1)])

    def prod_volume(self):
        return self.transport_counter

    def run_cooldown(self,num):
        print(str(self.env.now) + "-" + "Cooldown " + str(num) + " started on boat " + str(self.cooldown[num]))
        yield self.env.timeout(60*self.params['cool_time'])
        self.boat_status[self.cooldown[num]] = 2 # set status as cooled down
        self.cooldown_status[num] = 0 # set status as non-busy
        print(str(self.env.now) + "-" + "Cooldown " + str(num) + " finished on boat " + str(self.cooldown[num]))

    def run_process(self,num,normal_process=True):
        print(str(self.env.now) + "-" + "Process " + str(num) + " started on boat " + str(self.furnace[num]))
        if self.furnace_first_run[num]:
            self.furnace_start_time[num] = self.env.now
            self.furnace_first_run[num] = False
        
        if normal_process:
            yield self.env.timeout(60*self.params['process_time'])
            self.furnace_runs[num] += 1 # keep track of number of normal runs in this furnace
            self.process_counter += 1 # keep track of total number or process runs             
        else:
            yield self.env.timeout(60*self.params['coating_run_duration'])
        self.boat_runs[self.furnace[num]] += 1 # keep track of number of runs with this boat
        self.boat_status[self.furnace[num]] = 1 # set boat status as processed     
        self.furnace_status[num] = 0 # set status furnace as non-busy       
        print(str(self.env.now) + "-" + "Process " + str(num) + " finished on boat " + str(self.furnace[num]))
        
    def run_transport(self):

        batch_size = self.params['batch_size']
        transfer0_time = self.params['transfer0_time']
        transfer1_time = self.params['transfer1_time']
        transfer2_time = self.params['transfer2_time']
        no_of_processes = self.params['no_of_processes']
        no_of_cooldowns = self.params['no_of_cooldowns']
        runs_before_boatclean = self.params['runs_before_boatclean']
        downtime_runs = self.params['downtime_runs']
        downtime_duration = 60*self.params['downtime_duration']        
        wait_time = self.params['wait_time']
        idle_boat_timeout = self.params['idle_boat_timeout']
        idle_boat = 0

        while True:
            
            if (downtime_runs > 0) and (self.process_counter >= downtime_runs) and (self.batches_loaded == 0):
                    # if downtime is needed and all batches have been unloaded, enter downtime
                    yield self.env.timeout(downtime_duration) # stop automation during downtime
                    self.process_counter = 0 # reset total number of process runs
            
            ### MOVE FROM FURNACE TO COOLDOWN ###
            for i in range(no_of_processes): # first check if we can move a full boat from tube to cooldown
                if (not self.furnace_status[i]) and (not (self.furnace[i] == -1)) and (self.boat[self.furnace[i]].container.level): # if full boat is available
                    for j in range(no_of_cooldowns): # check cooldown locations
                        if (not self.cooldown_status[j]) and (self.cooldown[j] == -1): # if empty
                            boat = self.furnace[i] # store boat number
                            print(str(self.env.now) + "-" + "Move full boat " + str(boat) + " to cooldown " + str(j))                            
                            self.furnace[i] = -1 # empty the furnace
                            yield self.env.timeout(transfer1_time) # wait for transfer
                            self.cooldown[j] = boat # enter boat into cooldown
                            self.cooldown_status[j] = 1 # cooldown is busy status
                            self.env.process(self.run_cooldown(j)) # start process for cooldown
                            break # discontinue search for free cooldown locations for this boat

            for i in range(no_of_processes): # check if we can move any boat from tube to cooldown
                if (not self.furnace_status[i]) and (not (self.furnace[i] == -1)): # if boat is available
                    for j in range(no_of_cooldowns): # check cooldown locations
                        if (not self.cooldown_status[j]) and (self.cooldown[j] == -1): # if empty
                            boat = self.furnace[i] # store boat number
                            print(str(self.env.now) + "-" + "Move empty boat " + str(boat) + " to cooldown " + str(j))
                            self.furnace[i] = -1 # empty the furnace
                            yield self.env.timeout(transfer1_time) # wait for transfer
                            self.cooldown[j] = boat # enter boat into cooldown
                            self.cooldown_status[j] = 1 # cooldown is busy status
                            self.env.process(self.run_cooldown(j)) # start process for cooldown
                            break # discontinue search for free cooldown locations for this boat

            ### MOVE FROM COOLDOWN TO LOADSTATION ###
            if (not self.loadstation_status) and (self.loadstation == -1) and (self.batches_loaded > 0): # if loadstation is not busy and empty and there are batches in the system
                for i in range(no_of_cooldowns): # check if we can move a full boat from cooldown to loadstation; always proceed with load-out immediately after
                    if (not self.cooldown_status[i]) and (not self.cooldown[i] == -1) and (self.boat[self.cooldown[i]].container.level):
                        boat = self.cooldown[i] # store boat number
                        print(str(self.env.now) + "-" + "Move boat " + str(boat) + " to loadstation")
                        self.cooldown[i] = -1 # empty the cooldown
                        yield self.env.timeout(transfer2_time) # wait for transfer
                        self.loadstation = boat # enter boat into loadstation
                        
                        print(str(self.env.now) + "-" + "Ask for load-out for boat " + str(self.loadstation)) 
                        self.loadstation_status = 1 # set status as busy
                        yield self.load_out_start.succeed() # ask for load-out
                        self.load_out_start = self.env.event() # create new event
                        
                        break # stop search for available boat to put into loadstation
            
            if (not self.loadstation_status) and (self.loadstation == -1): # if loadstation is still not busy and empty
                for i in range(no_of_cooldowns): # check if we can move an empty boat from cooldown to loadstation; do not proceed with load-in immediately after as there may be downtime planned
                    if (not self.cooldown_status[i]) and (not self.cooldown[i] == -1):
                        boat = self.cooldown[i] # store boat number
                        print(str(self.env.now) + "-" + "Move boat " + str(boat) + " to loadstation")
                        self.cooldown[i] = -1 # empty the cooldown
                        yield self.env.timeout(transfer2_time) # wait for transfer
                        self.loadstation = boat # enter boat into loadstation                        
                        break # stop search for available boat to put into loadstation

            ### RUN LOAD-IN AND MOVE TO FURNACE ###
            if (not self.loadstation_status) and (not (self.loadstation == -1)): # if loadstation is not busy and contains boat 
                if (runs_before_boatclean > 0) and (self.boat_runs[self.loadstation] >= runs_before_boatclean): # if boat needs coating run
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            print(str(self.env.now) + "-" + "Move boat " + str(boat) + " to furnace " + str(i) + " for coating run")
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.boat_runs[boat] = 0 # reset number of runs
                            self.env.process(self.run_process(i, False)) # start coating run for furnace
                            break # discontinue search for a free furnace for this boat                           
                elif (not self.boat[self.loadstation].container.level) and (len(self.input.input.items) >= batch_size) and ((downtime_runs == 0) or (self.process_counter <= downtime_runs)):
                    # if boat is empty and wafers are available ask for load-in, except if downtime is required
                    self.loadstation_status = 1 # set status as busy
                    print(str(self.env.now) + "-" + "Ask for load-in for boat " + str(self.loadstation))
                    yield self.load_in_start.succeed()
                    self.load_in_start = self.env.event() # create new event
                elif (not self.boat[self.loadstation].container.level) and (self.batches_loaded > 0):
                    # if boat is empty and there are batches in the system check if the situation has been like this for a while; if so, try to move empty boat to furnace
                    if (idle_boat > 0) and ((self.env.now - idle_boat) >= idle_boat_timeout): # if we waited for new wafers for more than 5 minutes
                        print(str(self.env.now) + "-" + "Try to move idle boat from loadstation to furnace")
                        for i in range(no_of_processes):
                            if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                                print(str(self.env.now) + "-" + "Move idle boat " + str(self.loadstation) + " from loadstation to furnace " + str(i)) 
                                boat = self.loadstation # store boat number
                                self.loadstation = -1 # empty the loadstation                        
                                yield self.env.timeout(transfer0_time) # wait for transfer
                                self.furnace[i] = boat # put boat into furnace
                                break # discontinue search for a free furnace for this boat
                        idle_boat = 0
                    elif (idle_boat == 0):
                        print(str(self.env.now) + "-" + "Boat "+ str(self.loadstation) + " is idle in loadstation")
                        idle_boat = self.env.now
                elif self.boat[self.loadstation].container.level and (not self.boat_status[self.loadstation]): # if boat is full and has not been processed then try to load to furnace
                    print("Boat " + str(self.loadstation) + " in loadstation contains unprocessed wafers")
                    for i in range(no_of_processes):
                        if (not self.furnace_status[i]) and (self.furnace[i] == -1): # if furnace is free
                            boat = self.loadstation # store boat number
                            print(str(self.env.now) + "-" + "Move boat " + str(boat) + " to furnace " + str(i))
                            self.loadstation = -1 # empty the loadstation                        
                            yield self.env.timeout(transfer0_time) # wait for transfer
                            self.furnace[i] = boat # put boat into furnace
                            self.furnace_status[i] = 1 # furnace is busy status
                            self.env.process(self.run_process(i)) # start process for furnace
                            break # discontinue search for a free furnace for this boat
                                    
            yield self.env.timeout(wait_time)                        
            
    def run_load_in(self):
        cassette_size = self.params['cassette_size']
        no_loads = self.params['batch_size']*cassette_size // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
        loop_end = self.loop_end
        
        wafer_counter = 0
        
        while True:
            yield self.load_in_start

            print(str(self.env.now) + "-" + "Starting load-in")
            for i in range(no_loads):
                
                if not wafer_counter:

                    cassette = yield self.input.input.get()
                    wafer_counter = cassette_size                    
                    
                    if loop_end:
                        yield self.input.output.put(cassette)
                    else:
                        yield self.empty_cassette_buffer.input.put(cassette)                        

                wafer_counter -= automation_loadsize                               
                yield self.env.timeout(automation_time)            
                yield self.boat[self.loadstation].container.put(automation_loadsize)                                        

            self.boat_status[self.loadstation] = 0 # set boat status to unprocessed
            self.batches_loaded += 1 # keep track of number of loads in the system
            self.loadstation_status = 0 # set loadstation status to non-busy
            print(str(self.env.now) + "-" + "Finished load-in for boat " + str(self.loadstation))

    def run_load_out(self):
        cassette_size = self.params['cassette_size']
        no_loads = self.params['batch_size']*cassette_size // self.params['automation_loadsize']
        automation_loadsize = self.params['automation_loadsize']
        automation_time = self.params['automation_time']
        loop_begin = self.loop_begin

        cassette = None
        wafer_counter = 0
        
        while True:
            yield self.load_out_start
            
            print(str(self.env.now) + "-" + "Starting load-out")
            for i in range(no_loads):
                
                if not cassette:
                    if loop_begin:
                        cassette = yield self.output.input.get()
                    else:
                        cassette = yield self.empty_cassette_buffer.output.get()
                    
                yield self.boat[self.loadstation].container.get(automation_loadsize)
                wafer_counter += automation_loadsize
                yield self.env.timeout(automation_time)
                
                if wafer_counter == cassette_size:
                    yield self.output.output.put(cassette)
                    cassette = None
                    wafer_counter = 0
                    self.transport_counter += cassette_size
            
            self.batches_loaded -= 1 # keep track of number of loads in the system
            self.loadstation_status = 0 # set loadstation status to non-busy
            print(str(self.env.now) + "-" + "Finished load-out for boat " + str(self.loadstation))

    def nominal_throughput(self):
        throughputs = []        
        throughputs.append(self.params['batch_size']*self.params['no_of_processes']*3600/(60*self.params['process_time']))
        throughputs.append(self.params['batch_size']*self.params['no_of_cooldowns']*3600/(60*self.params['cool_time']))
        return min(throughputs)