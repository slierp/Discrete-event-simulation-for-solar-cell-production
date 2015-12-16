# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui
from dialogs.PlotSettingsDialog import PlotSettingsDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

font = {'family' : 'sans-serif',
        'size'   : 14}

plt.rc('font', **font)

class MultiPlot(QtGui.QMainWindow):
    
    def __init__(self, _parent):
        
        QtGui.QMainWindow.__init__(self, _parent)

        self.fig = None
        self.canvas = None
        self.parent = _parent
        self.prod_rates_df = _parent.simulation_thread.prod_rates_df         
        self.create_menu()
        self.create_main_frame()
        self.setWindowTitle("Production rates")       
        self.on_draw()        

    def create_menu(self):

        self.file_menu = self.menuBar().addMenu("File")
        quit_action = QtGui.QAction("Quit", self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close) 
        quit_action.setToolTip("Quit")
        quit_action.setStatusTip("Quit")
        quit_action.setShortcut('Ctrl+Q')
       
        self.file_menu.addAction(quit_action) 

    def create_main_frame(self):
        
        self.main_frame = QtGui.QWidget()
        
        # Create the mpl Figure and FigCanvas objects
        self.dpi = 100
        
        self.fig = Figure((10.0, 10.0), dpi=self.dpi, facecolor='White')        
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)       
 
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        show_button = QtGui.QPushButton()
        show_button.clicked.connect(self.plot_settings_view)
        show_button.setIcon(QtGui.QIcon(":gear.png"))
        show_button.setToolTip("Edit settings")
        show_button.setStatusTip("Edit settings")

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(show_button, QtGui.QDialogButtonBox.ActionRole)               

        self.mpl_toolbar.addWidget(show_button)                      
                                
        vbox = QtGui.QVBoxLayout()        
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        self.status_text = QtGui.QLabel("")        
        self.statusBar().addWidget(self.status_text,1)

    def plot_settings_view(self):
        settings_dialog = PlotSettingsDialog(self)
        settings_dialog.setModal(True)
        settings_dialog.show()
        
    def on_draw(self):

        cl = ['#4F81BD', '#C0504D', '#9BBB59','#F79646','#8064A2','#4BACC6','0','0.5'] # colour

        # add subplot purely for the axis labels
        axes = self.fig.add_subplot(111)  
        axes.spines['top'].set_color('none')
        axes.spines['bottom'].set_color('none')
        axes.spines['left'].set_color('none')
        axes.spines['right'].set_color('none')
        axes.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
        axes.set_xlabel(r'$\mathrm{\mathsf{Time\ [hours]}}$', fontsize=24, weight='black')
        axes.set_ylabel(r'$\mathrm{\mathsf{Production\ rate\ [a.u.]}}$', fontsize=24, weight='black')

        # define grid for all the subplots
        gs = gridspec.GridSpec(len(self.parent.plot_selection),1)
        gs.update(wspace=0, hspace=0) # set the spacing between the plots to zero

        num0 = 0 # for all data sets
        num1 = 0 # for selected data sets
        for i in self.prod_rates_df.columns:

            if num0 in self.parent.plot_selection:
                
                axes = self.fig.add_subplot(gs[num1])
                axes.plot(self.prod_rates_df.index, self.prod_rates_df.iloc[:,num0], c=cl[num1 % len(cl)]) # need iloc to avoid columns with the same name
                axes.text(0.01,0.5,i, horizontalalignment='left', verticalalignment='center', transform=axes.transAxes)
                axes.title.set_visible(False)               
                axes.set_yticklabels(())
                if (not num0 == self.parent.plot_selection[-1]):
                    axes.set_xticklabels(()) 
                num1 += 1

            num0 += 1

        self.canvas.draw()    
        
    def on_redraw(self):
        
        self.parent.plot_production_rates()
        self.close()    
                