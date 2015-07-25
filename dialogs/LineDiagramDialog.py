# -*- coding: utf-8 -*-
from __future__ import division
from PyQt4 import QtGui, QtCore, QtSvg
from blockdiag import parser, builder, drawer
from blockdiag.imagedraw import svg # needed for pyinstaller
from blockdiag.noderenderer import roundedbox # needed for pyinstaller

class LineDiagramDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(QtGui.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent   


        svg.setup(svg) # needed for pyinstaller
        roundedbox.setup(roundedbox) # needed for pyinstaller

        self.setWindowTitle(self.tr("Production line diagram"))
        vbox = QtGui.QVBoxLayout()

        ### Generate diagram definition ###
        diagram = """blockdiag {
                       shadow_style = 'none';                      
                       default_shape = 'roundedbox';                       
                       default_group_color = "#CCCCCC"
                       """
        
        for i, value in enumerate(self.parent.batchlocations):
            diagram += str(i) + " [label = " + str(value[0]) + "];\n"
            
        for i in range(len(self.parent.locationgroups)-1):
            if ((i+1) % 4):
                diagram += str(self.parent.locationgroups[i][0]) + " -> " + str(self.parent.locationgroups[i+1][0]) + ";\n"
            else:
                diagram += str(self.parent.locationgroups[i][0]) + " -> " + str(self.parent.locationgroups[i+1][0]) + " [folded];\n"
          
        for i, value in enumerate(self.parent.locationgroups):
            if(len(value) > 1):
                diagram += "group { "
                for i in value:
                    diagram += str(i) + ";"
                diagram += "}\n"
          
        diagram += "}"

        ### Generate SVG picture ###
        tree = parser.parse_string(diagram)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = drawer.DiagramDraw('SVG', diagram, filename="", noviewbox=True)
        draw.draw()
        svg_string = draw.save()
        
        ### Convert to PyQt supported format ###
        QtGui.QImageReader.supportedImageFormats()
        svg_widget = QtSvg.QSvgWidget()
        svg_widget.load(QtCore.QString(svg_string).toLocal8Bit())

        ### Add SVG widget ###
        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.addWidget(svg_widget)
        vbox.addLayout(hbox)

        ### Add ok button for closing the dialog ###
        hbox = QtGui.QHBoxLayout()
        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)
        vbox.addLayout(hbox)

        self.setLayout(vbox)