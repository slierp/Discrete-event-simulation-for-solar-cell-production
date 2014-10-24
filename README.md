Discrete-event-simulation-for-solar-cell-production
===================================================

The goal of this Python program is to be a platform for the simulation of the logistic aspects of (silicon) solar cell production lines. It is based on the Python package SimPy that enables discrete event simulation. The program can simulate every wafer movement within a production line with this technique.

<b>Features</b>
- Graphical user interface to define production lines 
- Production tools (such as furnaces and printers) can be put into any line configuration
- All automation and process-related events inside the tools are included
- Dynamic effects such as planned downtime are included
- Transport between tools and buffers is performed by operators
- Each tool, operator and tool-to-tool connection can be configured individually or as a group
- Simulation results include production volume, throughput and utility rate for each individual tool
- Cross-platform - tested on Windows; should also be compatible with Linux and Mac OS

<b>Example applications</b>
- Line matching. To assess the cost-of-ownership of a new solar cell technology one needs to know how good the utilization of each tool is when put in a line. Dynamic effects such as maintenance schedules can be included.
- Production optimization. One can make a virtual production line that represents an existing line, in order to test all kinds of changes and to see whether they are an improvement or not.

<b>Install</b>

To install you can choose between these methods:
- Go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the setup file and install it (Windows only)
- Go to the same link, download the zip file and manually run the exe file after unzipping
- Download the <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/archive/master.zip">source code</a> and use it in combination with a python distribution installation (e.g. Python(x,y), Anaconda, Enthought on Windows)

<b>Using the program</b>

On start-up the program loads a default configuration that represents a p-type monocrystalline silicon solar cell production line. The 'batch locations' panel can be used to change the list of tools, the production flow and the settings of the tools. Tools are always defined as part a group, so that the production can automatically flow from group to group along the list. The add and remove buttons can be used to modify the list. The tool settings can be accessed by double-clicking on an item in the list or by selecting an item and clicking the edit button. If all the tools within a group are of the same type then it is possible to double-click on the group name to alter all the tools at the same time. The production flow makes no distinction between tools within a group. The name of the group is automatically set to the name of the first production tool in that group.

The 'operators' panel can be used to change the list of operators, the tool-to-tool transport connections that they are responsible for and to change a number of settings that affect the operators and the connections. The list of available connections is automatically set by the information in the 'batch locations' panel. The add, remove and edit functions work in the same way as in the 'batch locations' panel. The 'import locations' automatically creates a default list of operators, one for each group-to-group connection.

The toolbar buttons can be used to load and save production line configurations, start and stop the simulation and to set the simulation time limit. The lower area contains an 'Activity log' tab that gives some standard information while running the simulation. More detailed information coming from a particular tool or operator can be enabled by setting its 'verbose' option. At the end of a simulation the 'Utilization' tab will contain a table that includes information about the utilization rate of whole tools and the idle time of individual processes within the tools. The 'nominal' column gives the nominal throughput value for the tools. This value is the maximum throughput of all the processes within the tool and does not include automation.

<b>Help wanted</b>

Defining how production tools function internally and how they are used and operated in a production line is a complicated task, so a program like this needs to be continuously under development. To reach and maintain an optimal implementation of the algorithms it is beneficial to have as much input as possible from real-world production tools and lines. Interested parties are encouraged to help the continued development of this program by submitting information of the way their production tools or lines function (automation, processes, maintenance cycles etc), so that the required tools and settings can be included in the program. The settings themselves do not have to be disclosed; the only requirement is to know which functions and settings are necessary to simulate the given tool or line. Another way to contribute is to do detailed checks of how the simulation results compare to the real world situation, to see whether the available settings are adequate or incomplete.