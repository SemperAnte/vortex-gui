# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Tue May 26 12:50:53 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:

DESCRIPTION:
    Utility
"""
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from PyQt5 import QtSerialPort as qtsp
   
def getComPortList() -> list:
    '''Return a sorted list with names of available COM ports.'''
    comName = qtsp.QSerialPortInfo.availablePorts()  
    if comName:
        comName = [x.portName() for x in comName]
        comName.sort()
    return comName

def alignLabelWidth(layout):      
    ''' Align width of labels at nested QFormLayouts (writed for connectionWidget).
        Find max width and then set it to all labels.'''
    SHOW_DEBUG_MESSAGE = False
    
    def findMaxWidth(layout):            
        maxWidth = 0
        if isinstance(layout, qtw.QFormLayout):
            # iterate through widgets at QFormLayout
            for idxForm in range(layout.count()):
                _, role = layout.getItemPosition(idxForm)
                widget = layout.itemAt(idxForm).widget()
                if role == qtw.QFormLayout.LabelRole:
                    widgetWidth = widget.minimumSizeHint().width()                    
                    if SHOW_DEBUG_MESSAGE:                        
                        print(f'Label {widget.text(): <15s}: width {widgetWidth}.')
                    if widgetWidth > maxWidth:
                        maxWidth = widgetWidth
                elif role == qtw.QFormLayout.SpanningRole: 
                    if isinstance(widget, qtw.QStackedWidget):
                        # iterate through pages of QStackedWidget
                        for idxStack in range(layout.itemAt(idxForm).widget().count()):
                            widgetWidth = findMaxWidth(widget.widget(idxStack).layout())
                            if widgetWidth > maxWidth:
                                maxWidth = widgetWidth
        return maxWidth
        
    def setLabelWidth(layout, width):
        if isinstance(layout, qtw.QFormLayout):
            # iterate through widgets at QFormLayout
            for idxForm in range(layout.count()):
                _, role = layout.getItemPosition(idxForm)
                widget = layout.itemAt(idxForm).widget()
                if role == qtw.QFormLayout.LabelRole:
                    widget.setMinimumWidth(width)
                elif role == qtw.QFormLayout.SpanningRole: 
                    if isinstance(widget, qtw.QStackedWidget):
                        # iterate through pages of QStackedWidget
                        for idxStack in range(layout.itemAt(idxForm).widget().count()):
                            setLabelWidth(widget.widget(idxStack).layout(), width)
                                
    maxWidth = findMaxWidth(layout)  
    if SHOW_DEBUG_MESSAGE:
        print(f'Max label width {maxWidth}.')
    setLabelWidth(layout, maxWidth)
    
class IpAdrValidator(qtg.QValidator):
    '''Validate ip address'''

    def validate(self, strInput, pos):
        octets = strInput.split('.')
        if len(octets) > 4:
            state = qtg.QValidator.Invalid
        elif not all([x.isdigit() for x in octets if x != '']):
            state = qtg.QValidator.Invalid
        elif not all([0 <= int(x) <= 255 for x in octets if x != '']):
            state = qtg.QValidator.Invalid
        elif len(octets) < 4:
            state = qtg.QValidator.Intermediate
        elif any([x == '' for x in octets]):
            state = qtg.QValidator.Intermediate
        else:
            state = qtg.QValidator.Acceptable
        return (state, strInput, pos)
    
def changeRelativePath(classWidget): 
    '''Using for testing'''
           
    SEARCH_SUBSTRING = 'res\\'    
    APPEND_SUBSTING = '..\\'        
    for key, name in classWidget.__dict__.items():
        if (isinstance(name, str)):
            if name.startswith(SEARCH_SUBSTRING):
                setattr(classWidget, key, APPEND_SUBSTING + name)
                
def runManualTest(testClass):
    import sys
        
    class MainWindow(qtw.QMainWindow):
        
        def __init__(self):
            super().__init__()
            
            changeRelativePath(testClass)
            self.setCentralWidget(testClass())
            
            self.show()

    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
    