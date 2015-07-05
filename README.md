Discrete-event-simulation-for-solar-cell-production
===================================================

The goal of this Python program is to be a platform for the simulation of the logistic aspects of (silicon) solar cell production lines. It is based on the Python package SimPy that enables discrete event simulation. The program can simulate every automation, process or transport event within a production line.

<b>Features</b>
- Graphical user interface to define production lines and run simulations
- Option to run simulations in commandline mode (e.g. for running multiple simulations simultaneously)
- Production tools and material flow between them can be put into any line configuration
- Detailed production tool and material flow simulation:
  - Most automation and process-related events inside the tools are included
  - Dynamic effects such as planned downtime are included
  - Transport between tools and buffers is performed by operators
  - Each tool, operator and tool-to-tool connection can be configured individually or as a group
- Simulation results include production volume, throughput and utilization rate for each individual tool
- Cross-platform - tested on Windows and linux; should be compatible with Mac OS

<b>Example applications</b>
- Line matching. For new solar cell technologies it is important to assess the utilization of a particular tool set as it affects the overall cost-of-ownership. Dynamic effects such as maintenance schedules can be included.
- Production optimization. One can make a representation of an existing line in order to test all kinds of changes and to see whether they are an improvement or not.
- Delivery predictions. If a production line is run on incoming order basis then a representation of the line could be helpful in predicting the delivery date of a certain amount of product.

<b>Install</b>

To install you can choose between these methods:
- Go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the setup file and install it (Windows only)
- Go to the same link, download the zip file and manually run the exe file after unzipping
- Download the <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/archive/master.zip">source code</a> and use it in combination with a python distribution installation (e.g. Python(x,y), Anaconda, Enthought on Windows)

<b>Using the program</b>

By default the program will start the graphical user interface. For commandline mode you have to add arguments, for example: python Main.py <simulation definition file> <duration in hours>

On start-up the program loads a default configuration that represents a p-type monocrystalline silicon solar cell production line. The 'batch locations' panel can be used to change the list of tools, the production flow and the settings of the tools. Tools are always defined as part a group, so that the production can automatically flow from group to group along the list. The add and remove buttons can be used to modify the list. The tool settings can be accessed by double-clicking on an item in the list or by selecting an item and clicking the edit button. If all the tools within a group are of the same type then it is possible to double-click on the group name to alter all the tools at the same time. The production flow makes no distinction between tools within a group. The name of the group is automatically set to the name of the first production tool in that group.

The 'operators' panel can be used to change the list of operators, the tool-to-tool transport connections that they are responsible for and to change a number of settings that affect the operators and the connections. The list of available connections is automatically set by the information in the 'batch locations' panel. The add, remove and edit functions work in the same way as in the 'batch locations' panel. The 'import locations' automatically creates a default list of operators, one for each group-to-group connection.

The toolbar buttons can be used to load and save production line configurations, start and stop the simulation and to set the simulation time limit. The lower area contains an 'Activity log' tab that gives some standard information while running the simulation. More detailed information coming from a particular tool or operator can be enabled by setting its 'verbose' option. At the end of a simulation the 'Utilization' tab will contain a table that includes information about the utilization rate of whole tools and the idle time of individual processes within the tools. The 'nominal' column gives the nominal throughput value for the tools. This value is the maximum throughput of all the processes within the tool and does not include automation.
