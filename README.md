Discrete-event-simulation-for-solar-cell-production
===================================================

The Python program is to a utility for simulating and analyzing the logistics of (silicon) solar cell production lines. It uses the Simpy package for its discrete event simulation capability. The program simulates the movement of wafers within production tools and between tools, buffers and operators.

<b>Features</b>
- Graphical user interface with which one can define any arbitrary production line
- A set of production tools to choose from with a wide range of available settings
- A set of operators can be generated or defined, that take care of transport wafers between tools
- Each tool instance, each operator and each tool-to-tool connection can be individually configured
- Analysis results include production volume, throughput per hour, idle time for each tool etc.
- Cross-platform - tested on Windows; should also be compatible with Linux and Mac OS

Please see the TODO document for a list of future additions

<b>Example applications</b>
- In the research phase of any new solar cell technology it is often the question whether the cost of an added step outways the efficiency benefits. To make a better estimate of the cost of an added step it is interesting to simulate a production line with and without the added step.
- When running a production line it can be of interest to fine-tune a model that exactly represents the line itself, so one can run a lot of 'what-if' scenarios, such as unscheduled down-time for certain tools.

<b>Install</b>

To install you can choose between these methods:
- download the <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/archive/master.zip">source code</a> and use it in combination with a python distribution installation (e.g. Python(x,y), Anaconda, Enthought on Windows)
- go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the zip file and manually run the exe file after unzipping
- go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the setup file and install it (Windows only)

<b>Using the program</b>

On startup the program loads in a default production line that mimics a p-type monocrystalline silicon solar cell production line. In the left panel one can define and alter 'batch locations' (tools, buffers, sources or bins) and the way they are interconnected. On the right panel one can define and alter operators that take care of a certain set of connections. These connections are defined by the information in the left panel.

In the toolbar one can load and save production line definitions, start and stop the simulation and set the simulation time limit. The text box below contains the output, which includes some standard information. The amount of information output from a particular tool or operator can be increased in the settings.
