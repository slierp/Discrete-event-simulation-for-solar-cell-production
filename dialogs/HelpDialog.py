# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

help_text = """
<html>
<head><head/>
<body>
<h1>DescPro</h1>

<ul>
<li><a href="#general">Introduction</a></li>
<li><a href="#quick">How to define and run simulations</a></li>
<li><a href="#example">Simulation definition example</a></li>
<li><a href="#commandline">Running simulations on the commandline</a></li>
</ul>

<p><h2><a name="general">Introduction</a></h2></p>
<p>The aim of the DescPro program is to try to capture the dynamics of modern solar cell production lines using discrete event simulation techniques.
All process and transportation events within the whole line can in principle be included in the simulations, which gives the advantage
that dynamic aspects such as planned maintenance and random micro-stops can easily be taken into account.
Some of the potential uses of the technique are as follows:</p>

<ul>
<li>Improve utilization rate and long-term production throughput of existing lines by identifying bottlenecks and alleviating them</li>
<li>Compare the performance of new production line concepts and its effects on the cost-of-ownership</li>
<li>Improve product delivery time predictions which should then allow for lower product inventory</li>
</ul>

<p>The program interface allows the user to define production lines in a highly flexible way and to define operators that run the line.
It is possible to place the tools in groups in order to distribute the wafers over several tools that typically perform a single type of process.
The available production tools are also highly flexible and have settings such as:</p>

<ul>
<li>Size or quantity of tool elements (e.g. number of print steps)</li>
<li>Process parameters (e.g. diffusion cycle time)</li>
<li>Load-unload automation parameters (e.g. load time per cassette)</li>
<li>Downtime parameters (e.g. chemical bath replacement)</li>
</ul>

<p>The information that is produced from the simulations includes:</p>
<ul>
<li>Hourly and total production throughput</li>
<li>Utilization of each tool</li>
<li>Utilization of individual tool components</li>
<li>Comparison to nominal throughput</li>
</ul>

<p><h2><a name="quick">How to define and run simulations</a></h2></p>
<p><b>Using the 'Tools' window</b></p>
<p>
The 'Tools' window contains a list through which the wafers will flow from top to bottom.
Each item in the list represents a tool group so that tools can form clusters that process the incoming wafers simultaneously, but a tool group can also consist of one tool only.
To view the contents of any tool group the user can click on the '+' symbol next to each item.
</p>
<p>
To add or remove tools the user can click on the corresponding icons underneath the tools window.
New tools are added at the bottom of the list by default, but the user can also select a location in the list before adding the tool.
If the selected tool is a tool group then a new tool group will be added with a newly generated tool inside, but if a tool inside a tool group is selected then the tool is added to that group.
</p>
<p>
To edit the settings of a tool the user can double-click on that tool or select it and click on the 'Edit settings' icon.
The dialog that appears will contain further information on the functionality of the tool and the available settings.
If all the tools in a particular group are of the same type then it is possible to change the settings for all the tools in that group simultaneously.
</p>

<p><b>Using the 'Operators' window</b></p>
<p>
The 'Operators' window contains a list of operators that run the production line.
A set of operators can be generated automatically if there is a production line defined in the 'tools' window by clicking on the 'Import tools' icon.
This function will generate one operator for each tool group connection.
The settings of an operator can be changed by double-clicking or by selecting an operator and clicking on the 'Edit settings' icon.
By clicking on the '+' symbol next to an operator one can see which connections the operator will take care of.
The operator settings and the connections that they are responsible for will affect the simulation, but the order in which the operators are listed does not.
</p>
<p>
To add or remove operators the user can click on the corresponding icons below the 'Operators' window.
A new operator is added to the bottom of the list by default, but the user can also select a position before adding the operator.
Each new operator will have one connection by default, which is the connection between the first two tool groups.
To add or remove connections the user needs to select an existing connection and click on 'Add' or 'Remove'.
The settings of a particular connection can be changed by double-clicking or by using the 'Edit settings' icon.
</p>
It is important to keep in mind that if a tool group is removed in the 'Tools' window that the program will try to remove any references to that tool group in the 'Operators' window.
If all the tool groups are removed then all references become invalid, so it will be necessary to rebuild the connections list when new tools are added again.
The quickest way to do this is to use the 'Import tools' icon.
</p>

<p><b>Running simulations</b></p>
<p>
To run simulations the user can select a simulation time period in the top buttonbar and then click on 'Run simulation'.
To stop a simulation prematurely there is a stop button available as well.
There will a slight delay before the simulation actually stops because it needs to reach one of its pre-defined algorithm interruptions.
Once completed the program will generate simulation results that are presented in the 'Activity' and 'Utilization' tabs.
</p>
<p><b>Profiling mode</b></p>
<p>
The top buttonbar contains a checkbox that turns the profiling mode on or off.
In this mode the simulation will generate hourly production rate information.
The reason for having a separate profiling mode option is because the frequent interruptions will prolong the required calculation time.
</p>
<p>
After running the simulation in profiling mode and clicking on the chart icon a new window will open with the generated data.
The chart contains the production rate for each tool in the production line that is calculated as the number of wafers put into its output chamber in the last hour.
In case of a buffer the data represents any change in the number of wafers stored in the buffer in the last hour.
The picture can be useful especially to see how the downtime procedures of several different tools can affect the whole line.
There may be some smaller scatter in the data due to the fact that the tool output may not align well with the hourly repetition rate, so that an extra cassette is added every second hour for example.
In the chart window there is a buttonbar for selecting or deselecting data to show, various icons to change things like the axes and there is an icon for saving the image.
</p>
<p><b>Speeding up simulations</b></p>
<p>
Discrete event simulations in principle cannot run across multiple CPU threads, so it not possible to speed up a simulation in this way.
However, it is possible to run multiple simulations at the same time by running multiple instances of the DescPro program.
Depending on the system configuration and the number of simulations the calculation time can be the same as when running a single simulation.
</p>
<p>
If one is familiar with Python and is using the DescPro program from source code then the recommendation for speeding up simulations is by using Cython on the SimPy library or by using PyPy.
Both techniques can give rather significant speed-ups of 25-50%.
SimPy is the Python package used by DescPro to facilitate the discrete event simulation functionality.
There are scripts available in the cython-simpy_scripts directory in the source code for transforming the SimPy library using Cython.
</p>

<p><h2><a name="example">Simulation definition example</a></h2></p>
<p>As an example we try to define a line that consists of a single tool, which is a tube furnace.</p>
<p><img src="dialogs/example.png" alt="" height="120" width="640"></p>
<ol>
<li>Remove the default production line that is loaded at program start-up.
Click on the 'remove' button underneath the 'Tools' window.</li>
<li>Add wafer source. Click on 'Add' and select 'WaferSource'.</li>
<li>Add tube furnace. Click on 'Add' and select 'TubeFurnace'.</li>
<li>Add wafer bin. Click on 'Add' and select 'WaferBin'.</li>
<li>Automatically add one operator for each tool connection.
Click on 'Import tools' underneath the operators window.</li>
<li>Make sure that the batch sizes are equal for each tool connection.
Double-click on the added WaferSource and go to Settings. Change 'Number of units in a single stack' to 100.</li>
</ol>

<p>Now you can click on 'Run simulation' in the top buttonbar to start the simulation.
The simulation progress and some of the results are shown in the 'Activity' tab.
Utilization results will be shown in the corresponding tab.</p>

<p><h2><a name="commandline">Running simulations on the commandline</a></h2></p>
<p>
If the program is given commandline arguments then it will run without opening the user interface.
There is a '-h' or '--help' commandline argument available that will print some usage information.
The two main arguments are the input filename that contains the simulation definition and the simulation duration in hours.
The filename should be a .DESC file which was saved to file using the user interface.
There is a '-p' or '--profile' option to turn on the profiling mode.
On the commandline the profiling mode will generate a CSV file called output.csv that contains the hourly production rate results for each tool.
</p>

</body>
</html>
"""

class HelpDialog(QtGui.QDialog):
    # Generates help document browser    
    
    def __init__(self, parent):
        super(QtGui.QDialog, self).__init__(parent)
        
        self.parent = parent       
        
        self.setWindowTitle(self.tr("Help"))
        vbox = QtGui.QVBoxLayout()

        browser = QtGui.QTextBrowser()
        browser.insertHtml(help_text)
        browser.moveCursor(QtGui.QTextCursor.Start)

        vbox.addWidget(browser)

        ### Buttonbox for ok ###
        hbox = QtGui.QHBoxLayout()
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumHeight(576)
        self.setMinimumWidth(1024)