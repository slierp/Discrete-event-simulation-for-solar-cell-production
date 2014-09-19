Discrete-event-simulation-for-solar-cell-production
===================================================

The goal of this Python program is to be a platform for simulating and analyzing the logistics of (silicon) solar cell production lines. It is based on the Simpy package that performs discrete event simulation. With this technique, the program can in principle simulate every wafer movement within production tools and between tools, buffers and operators.

<b>Features</b>
- Graphical user interface with which one can define any arbitrary production line
- A set of production tools to choose from with a wide range of available settings
- A set of operators that can be automatically generated or manually defined, that take care of transport wafers between 'batch locations' (production tools, buffers or wafer sources/bins)
- Each tool instance, each operator and each tool-to-tool connection can be individually configured
- Analysis results include production volume, throughput per hour, idle time for each tool etc.
- Cross-platform - tested on Windows; should also be compatible with Linux and Mac OS

Please see the TODO document for a list of future additions.

<b>Example applications</b>
- To calculate the cost-of-ownership of a particular solar cell technology, the amount of cells that are produced with the selected tool setup in a given time period are paramount. One can make estimates using the process that has the lowest effective throughput, but reality is more complicated because different tools have different down-time behaviour, such as in their maintenance schedules. Discrete event simulation can in principle take all those things into account.
- Espeically in the research phase of any new solar cell technology it is often the question whether the cost of an added step outways the efficiency benefits. To make a better estimate of the cost of an added step it is interesting to simulate a production line with and without the added step.
- When running a production line it can be of interest to fine-tune a model that exactly represents the line itself, so one can run a lot of 'what-if' scenarios, such as unscheduled down-time for certain tools.

<b>Install</b>

To install you can choose between these methods:
- go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the setup file and install it (Windows only)
- - go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the zip file and manually run the exe file after unzipping
- download the <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/archive/master.zip">source code</a> and use it in combination with a python distribution installation (e.g. Python(x,y), Anaconda, Enthought on Windows)

<b>Using the program</b>

On startup the program loads in a default production line that mimics a p-type monocrystalline silicon solar cell production line. In the left panel one can define and alter 'batch locations' (tools, buffers, sources and bins) and the way they are interconnected. In the right panel one can define and alter operators that take care of a certain set of tool-to-tool connections. The list of available connections is defined by the information in the left panel. Double-clicking on any item opens a settings dialog. The plus and minus buttons can be used to add and remove items, within the context of what has been selected inside the panel.

In the toolbar one can load and save production line definitions, start and stop the simulation and set the simulation time limit. The text box below contains the output, which includes some standard information. The amount of information output from a particular tool or operator can be increased in the settings.
