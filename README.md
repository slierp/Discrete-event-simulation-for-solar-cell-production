Discrete-event-simulation-for-solar-cell-production
===================================================

<b>This program is not yet ready for use.</b>

The intention for this program is to become a utility for analyzing silicon solar cell production lines.
It uses Simpy package for its discrete event simulation capability.

<b>Sought after features</b>
- A set of production tools to select and configure into a production line
- A set operators can be defined that transport wafers between tools
- A set of time-related parameters such as run-time, maintenance schedule etc.
- Analysis results include production volume, throughput per hour, idle time for each tool etc.
- Graphical user interface including tool, operator and time-related settings

<b>Example applications</b>
- In the research phase of any new solar cell technology it is often the question whether the cost of an added step outways the efficiency benefits. To make a better estimate of the cost of an added step it is interesting to simulate a production line with and without the added step.
- When running a production line it can be of interest to fine-tune a model that exactly represents the line itself, so one can run a lot of 'what-if' scenarios, such as unscheduled down-time for certain tools
