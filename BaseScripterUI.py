import sys
path = r'G:\My Drive\Maya\MyScripts\BaseScripter'
if path not in sys.path:
    sys.path.append(path)

import baseScripter
import maya.api.OpenMaya as om

reload(baseScripter)

bs= baseScripter.BaseScripter()
import sys

import sys
import pymel.core as pmc

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import * 
from PySide2.QtCore import Slot

titleStyles = """
            padding: 100px;
            padding-top:10px;
            padding-bottom:10px;
            font-size: 18px;"""

class AdvancedButton(QtWidgets.QPushButton):
    """
    Push button that supports multiple click types
    
    kwargs:
    tooltip: [String] tooltip text
    c: [Function] function to run onClick
    cC: [Function] function to run onClick [ctrl+click]
    sC: [Function] function to run onClick [shift+click]
    cSC: [Function] function to run onClick [strl+shift+click]

    """
    def __init__(self, *args, **kwargs):
        super(AdvancedButton, self).__init__(*args, **kwargs)
        self.clicked.connect(self.handleButton)
        self.__dict__.update(kwargs)


        
    def handleButton(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            print('Shift+Click')
            try:
                self.sC()
            except:
                pass
        elif modifiers == QtCore.Qt.ControlModifier:
            print('Control+Click')
            try:
                self.cC()
            except:
                pass
        elif modifiers == (QtCore.Qt.ControlModifier |
                            QtCore.Qt.ShiftModifier):
            print('Control+Shift+Click')
            try:
                self.cSC()
            except:
                pass
        else:
            try:
                self.c()
            except:
                pass
            print('Click')

class BulkEditWindow(QtWidgets.QWidget):
    """
    Bulk Edit Via Property Matrix

    This seeks to recreate some of the useful features of the UE5 tool of the same name

    Alpha draft will include the ability to connect a single driver output socket to multiple driven targets into the same socket. 
    It will also include the ability to edit the properties of multiple targets.

    3 Columns
    Driver | Driven | Settings


    """
    def __init__driver(self):
        container = QWidget()
        containerLayout = QVBoxLayout()
        container.setLayout(containerLayout)
        label = QLabel("Driver")
        label.setAlignment(QtCore.Qt.AlignCenter)
        containerLayout.addChildWidget(label)
        # containerLayout.addChildWidget(scroll)

        self.layoutBox.addWidget(container)
        container.setMinimumSize(500, 500)




    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        layoutBox = QVBoxLayout()
        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label = QLabel("Bulx Edit Via Property Matrix" )
        self.setLayout(layoutBox)
        root = QWidget()
        layoutBox.addWidget(self.label)
        layoutBox.addWidget(root)
        self.layoutBox = QHBoxLayout()
        root.setLayout(self.layoutBox)

        
        self.__init__driver()
        # self.__init__driven()
        # self.__init__properties()

class BaseScripterUI(QtWidgets.QWidget):

    def __openWindow(self):
        try:
            self.w.show()
        except:
            print("No window to show")
    def __closeWIndow(self):
        try:
            self.w.close()
        except:
            print("No window to close")
    def __setWindow(self, window):
        self.w = window
    
    def __setAndOpenWindow(self, window):
        self.__setWindow(window)
        self.__openWindow()

    def __init__(self, *args, **kwargs):
        self.w = None
        self.targets = pmc.ls(sl=1)
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        title = QtWidgets.QLabel("BaseScripter UI")
        title.setAlignment(QtCore.Qt.AlignHCenter)
        title.setStyleSheet(titleStyles)
        
        self.globalLayout = QtWidgets.QVBoxLayout(self)
        
        self.globalLayout.addWidget(title)
        # initialize all uis
        self.init__cc_colorPicker()
        self.init__historically_uninteresting()
        self.init__bulkEditPropertyMatrix()
        
    def init__bulkEditPropertyMatrix(self):
        button = QtWidgets.QPushButton("Bulk Edit Property Matrix")
        self.globalLayout.addWidget(button)

        window = BulkEditWindow()
        button.clicked.connect(lambda x : self.__setAndOpenWindow(window))

        
        

    #Make nodes historically uninteresting
    def init__historically_uninteresting(self):
        shiftButton = AdvancedButton('Historically Uninteresting')
        self.globalLayout.addWidget(shiftButton)
        shiftButton.setToolTip("Click to effect connections\nShift+Click to effect selected node")
        
        shiftButton.c = bs.setIHI(pmc.ls(sl=1), n=1)
        shiftButton.sC = bs.setIHI(pmc.ls(sl=1), n=0)

    # Recursively recolor nurbs curves selected
    def init__cc_colorPicker(self):
        button = QtWidgets.QPushButton("Recolor Nurbs")
        self.globalLayout.addWidget(button)
        button.clicked.connect(self.cc_colorPicker_open)

    def cc_colorPicker_change(self):
        targ = list(self.colour_chooser.currentColor().getRgb())
        print(targ[0:3])
        bs.colorCCs(pmc.listRelatives(self.targets, c=1), [targ[0]/float(255),targ[1]/float(255),targ[2]/float(255)
        ])
        pmc.refresh()

    def cc_colorPicker_close(self):
        pmc.select(self.targets)

    def cc_colorPicker_open(self):
        self.targets = pmc.ls(sl=1)
        pmc.select(cl=1)
        self.colour_chooser = QtWidgets.QColorDialog()
        self.colour_chooser.currentColorChanged.connect(self.cc_colorPicker_change)
        self.colour_chooser.colorSelected.connect(self.cc_colorPicker_close)
        # self.colour_chooser.blockSignals(True)
        self.colour_chooser.open()




w = BaseScripterUI()
w.show()

# https://www.pythonguis.com/tutorials/pyside-layouts/
# https://doc.qt.io/qtforpython-5/modules.html