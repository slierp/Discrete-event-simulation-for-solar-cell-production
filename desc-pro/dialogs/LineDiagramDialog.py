# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtSvg, QtGui
from blockdiag import parser, builder, drawer
from blockdiag.imagedraw import svg # needed for pyinstaller
from blockdiag.noderenderer import roundedbox # needed for pyinstaller

class LineDiagramDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        
        self.parent = parent
        
        self.clip = QtWidgets.QApplication.clipboard()

        svg.setup(svg) # needed for pyinstaller
        roundedbox.setup(roundedbox) # needed for pyinstaller

        self.setWindowTitle(self.tr("Production line diagram"))
        vbox = QtWidgets.QVBoxLayout()

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
        #QtGui.QImageReader.supportedImageFormats()        
        self.svg_widget = QtSvg.QSvgWidget()            
        self.svg_widget.load(str(svg_string).encode('latin-1'))               

        ### Add SVG widget ###
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.addWidget(self.svg_widget)
        vbox.addLayout(hbox)

        ### Add ok button for closing the dialog ###
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)

        copy_button = QtWidgets.QPushButton()
        copy_button.setText('Copy to clipboard')
        copy_button.clicked.connect(self.copy_to_clipboard)
        copy_button.setShortcut('Ctrl-C')        
        
        hbox.addWidget(buttonbox)
        hbox.addWidget(copy_button)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)
        vbox.addLayout(hbox)

        self.setLayout(vbox)        

    def copy_to_clipboard(self):

        image = QtGui.QImage(self.svg_widget.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter()
        painter.begin(image)        
        self.svg_widget.render(painter)
        painter.end()
        
        self.clip.setImage(image)        
        
    def closeEvent(self, event):
        # make sure to empty clipboard to avoid delay after program was exited
        self.clip.clear()
        event.accept() 