# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
import ntpath
from dialogs.PlotSettingsDialog import PlotSettingsDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

font = {'family' : 'sans-serif',
        'size'   : 14}

plt.rc('font', **font)

class MultiPlot(QtWidgets.QMainWindow):
    
    def __init__(self, _parent):
        
        QtWidgets.QMainWindow.__init__(self, _parent)
        self.setWindowTitle("Production rates")
        self.resize(1020, 752)
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        
        self.fig = None
        self.canvas = None
        self.parent = _parent
        self.prod_rates_df = _parent.simulation_thread.prod_rates_df
        self.prev_dir_path = ""
        self.create_menu()
        self.create_main_frame()       
        self.on_draw()        

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("File")
        quit_action = QtWidgets.QAction("Quit", self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close) 
        quit_action.setToolTip("Quit")
        quit_action.setStatusTip("Quit")
        quit_action.setShortcut('Ctrl+Q')
       
        self.file_menu.addAction(quit_action)

    def create_main_frame(self):
        self.main_frame = QtWidgets.QWidget()
        
        # Create the mpl Figure and FigCanvas objects
        self.dpi = 100
        
        self.fig = Figure((10.0, 10.0), dpi=self.dpi, facecolor='White')        

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)       
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        save_button = QtWidgets.QPushButton()
        save_button.clicked.connect(self.save_production_data)
        save_button.setIcon(QtGui.QIcon(":save.png"))
        save_button.setToolTip("Save production data")
        save_button.setStatusTip("Save production data")
        
        show_button = QtWidgets.QPushButton()
        show_button.clicked.connect(self.plot_settings_view)
        show_button.setIcon(QtGui.QIcon(":gear.png"))
        show_button.setToolTip("Edit settings")
        show_button.setStatusTip("Edit settings")

        buttonbox0 = QtWidgets.QDialogButtonBox()
        buttonbox0.addButton(save_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(show_button, QtWidgets.QDialogButtonBox.ActionRole)

        self.mpl_toolbar.addWidget(buttonbox0)                      
                                
        vbox = QtWidgets.QVBoxLayout()        
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        self.status_text = QtWidgets.QLabel("")        
        self.statusBar().addWidget(self.status_text,1)

    def save_production_data(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self,self.tr("Save file"), self.prev_dir_path, "CSV files (*.csv)")
        filename = filename[0]
        
        if not filename:
            return

        self.prev_dir_path = ntpath.dirname(filename[0])
        self.prod_rates_df.to_csv(filename)        
        self.statusBar().showMessage("File saved")

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
        
        self.parent.plot_selection.sort() # sort to be sure we make axes for only the last element
        
        for i in self.prod_rates_df.columns:

            if num0 in self.parent.plot_selection:
                
                axes = self.fig.add_subplot(gs[num1])
                axes.plot(self.prod_rates_df.index, self.prod_rates_df.iloc[:,num0], c=cl[num1 % len(cl)]) # need iloc to avoid columns with the same name
                axes.text(0.01,0.5,i, horizontalalignment='left', verticalalignment='center', transform=axes.transAxes)
                axes.title.set_visible(False)               
                axes.set_yticklabels(())
                if (not num0 == self.parent.plot_selection[-1]):
                    axes.set_xticklabels(()) 
                axes.tick_params(pad=8)
                num1 += 1

            num0 += 1

        self.canvas.draw()    
        
    def on_redraw(self):
        
        self.parent.plot_production_rates()
        self.close()    
                