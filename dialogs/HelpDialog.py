# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui

help_text = """
<html>
<head><head/>
<body>
<h1>DescPro</h1>

* <a href="#general">Introduction</a><br>
* <a href="#quick">Quick-start</a><br>
* <a href="#example">Simulation definition example</a><br> 

<p><h2><a name="general">Introduction</a></h2></p>
<p>The aim of the DescPro program is to try to capture the dynamics of modern solar cell production lines using discrete event simulation techniques.
All process and transportation events within the whole line can in principle be included in the simulations, which gives the advantage
that dynamic aspects such as planned maintenance and random micro-stops can easily be taken into account.
Some of the potential uses of the technique are as follows:<br>
- Improve utilization rate and long-term production throughput of existing lines by identifying bottlenecks and alleviating them<br>
- Compare the performance of new production line concepts and its effects on the cost-of-ownership<br>
- Improve product delivery time predictions which should then allow for lower product inventory</p>

<p>The program interface allows the user to define production lines in a highly flexible way and to define operators that run the line.
It is possible to place the tools in groups in order to distribute the wafers over several tools that typically perform a single type of process.
The available production tools are also highly flexible and have settings such as:<br>
- Size or quantity of tool elements (e.g. number of print steps)<br>
- Process parameters (e.g. diffusion cycle time)<br>
- Load-unload automation parameters (e.g. load time per cassette)<br>
- Downtime parameters (e.g. chemical bath replacement)</p>

<p>The information that is produced from the simulations includes:<br>
- Hourly and total production throughput<br>
- Utilization of each tool<br>
- Utilization of individual tool components<br>
- Comparison to nominal throughput</p>

<p><h2><a name="quick">Quick-start</a></h2></p>
<p>TO BE ADDED</p>

<p><h2><a name="example">Simulation definition example</a></h2></p>
<p>As an example we try to define a line that consists of a single tool, which is a tube furnace.</p>
<p>Step 1: Remove the default production that is loaded at program start-up.
Click on the 'remove' button underneath the batchlocations window.<br>
Step 2: Add wafer source. Click on 'Add batchlocation' and select 'WaferSource'.<br>
Step 3: Add tube furnace. Click on 'Add batchlocation' and select 'TubeFurnace'.<br>
Step 4: Add wafer bin. Click on 'Add batchlocation' and select 'WaferBin'.<br>
Step 5: Automatically add one operator for each tool connection.
Click on 'Import locations' underneath the operators window.<br>
Step 6: Make sure that the batch sizes are equal for each tool connection.
Double-click on the added WaferSource and go to Settings. Change 'Number of units in a single batch' to 100.</p>
<p>Now you can click on 'Run simulation' in the top buttonbar to start the simulation.
The simulation progress and some of the results are shown in the 'Activity' tab.
Utilization results will be shown in the corresponding tab.</p>

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