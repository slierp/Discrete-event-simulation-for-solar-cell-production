Discrete-event-simulation-for-solar-cell-production
===================================================

The Python program is to a utility for simulating and analyzing the logistics of (silicon) solar cell production lines. It uses the Simpy package for its discrete event simulation capability.

<b>Features</b>
- Graphical user interface with which one can define an arbitrary production line
- Including tool, operator and time-related settings
- A set of production tools to select and configure into a production line
- A set operators can be defined that transport wafers between tools
- A set of time-related parameters such as run-time, maintenance schedule etc.
- Analysis results include production volume, throughput per hour, idle time for each tool etc.

- Cross-platform - tested on Windows; should also be compatible with Linux and Mac OS

<b>Example applications</b>
- In the research phase of any new solar cell technology it is often the question whether the cost of an added step outways the efficiency benefits. To make a better estimate of the cost of an added step it is interesting to simulate a production line with and without the added step.
- When running a production line it can be of interest to fine-tune a model that exactly represents the line itself, so one can run a lot of 'what-if' scenarios, such as unscheduled down-time for certain tools.

<b>Install</b>
To install you can choose between these methods:
- download the <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/archive/master.zip">source code</a> and use it in combination with a python distribution installation (e.g. Python(x,y), Anaconda, Enthought on Windows)
- go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the zip file and manually run the exe file after unzipping
- go to <a href="https://github.com/slierp/Discrete-event-simulation-for-solar-cell-production/releases">releases</a>, download the setup file and install it (Windows only)

<b>Using the program</b>
