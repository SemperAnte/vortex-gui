# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Tue May 26 19:02:30 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    [ ] validator for 'name' edit line (no spaces and special chars)

DESCRIPTION:
    Modem Widget
"""
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class ModemWidget(qtw.QGroupBox):
    
    parameterChanged = qtc.pyqtSignal(dict)
    
    WIDGET_TITLE = 'Modem options'
    DEFAULT_ID = 0
    MIN_ID = 0
    MAX_ID = 2 ** 8 - 1    
    DEFAULT_NAME = 'A'        
    MIN_BLOCK_SIZE = 10
    MAX_BLOCK_SIZE = 400    
    DEFAULT_BLOCK_SIZE = 40    
    MIN_TRANS_SIZE = 1
    MAX_TRANS_SIZE = 100
    DEFAULT_TRANS_SIZE = 10
    MIN_POWER_LEVEL = 0
    MAX_POWER_LEVEL = 100
    DEFAULT_POWER_LEVEL = 100
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self._setupUi()
        
    def _setupUi(self):  
        self.setTitle(self.WIDGET_TITLE)
        
        self.id = qtw.QSpinBox()
        self.id.setMinimum(self.MIN_ID)
        self.id.setMaximum(self.MAX_ID)
        self.id.setValue(self.DEFAULT_ID)
        self.name = qtw.QLineEdit()
        self.name.setText(self.DEFAULT_NAME)
        self.mode = qtw.QComboBox()
        self.mode.addItems(['Auto', 'Manual'])
        self.rob = qtw.QComboBox()
        self.rob.addItems(['D', 'C', 'B'])
        self.mdl = qtw.QComboBox()
        self.mdl.addItems(['QPSK', 'QAM16'])
        self.rate = qtw.QComboBox()
        self.rate.addItems(['1/3', '1/2', '2/3'])        
        self.blockSize = qtw.QSpinBox()
        self.blockSize.setMinimum(self.MIN_BLOCK_SIZE)
        self.blockSize.setMaximum(self.MAX_BLOCK_SIZE)
        self.blockSize.setValue(self.DEFAULT_BLOCK_SIZE)
        self.transSize = qtw.QSpinBox()
        self.transSize.setMinimum(self.MIN_TRANS_SIZE)
        self.transSize.setMaximum(self.MAX_TRANS_SIZE)
        self.transSize.setValue(self.DEFAULT_TRANS_SIZE)
        self.powerLevel = qtw.QSpinBox()
        self.powerLevel.setMinimum(self.MIN_POWER_LEVEL)
        self.powerLevel.setMaximum(self.MAX_POWER_LEVEL)
        self.powerLevel.setValue(self.DEFAULT_POWER_LEVEL)
        
        self._enableModeChoice(self.mode.currentText())        
        
        self.setLayout(qtw.QFormLayout())        
        self.layout().addRow('ID', self.id)
        self.layout().addRow('Name', self.name)
        self.layout().addRow('Mode', self.mode)
        self.layout().addRow('Robustness', self.rob)
        self.layout().addRow('Modulation', self.mdl)
        self.layout().addRow('Code Rate', self.rate)
        self.layout().addRow('Block Size', self.blockSize)
        self.layout().addRow('Transfer Size', self.transSize)
        self.layout().addRow('Power Level', self.powerLevel)
        
        # signal-slot connections
        self.mode.currentTextChanged.connect(self._enableModeChoice)
        self.id.valueChanged.connect(lambda x: self.parameterChanged.emit({'id': x}))
        self.name.textChanged.connect(lambda x: self.parameterChanged.emit({'name': x}))
        self.mode.currentTextChanged.connect(lambda x: self.parameterChanged.emit({'mode': x}))
        self.rob.currentTextChanged.connect(lambda x: self.parameterChanged.emit({'rob': x}))
        self.mdl.currentTextChanged.connect(lambda x: self.parameterChanged.emit({'mdl': x}))        
        self.rate.currentTextChanged.connect(lambda x: self.parameterChanged.emit({'rate': x}))
        self.blockSize.valueChanged.connect(lambda x: self.parameterChanged.emit({'blockSize': x}))
        self.transSize.valueChanged.connect(lambda x: self.parameterChanged.emit({'transSize': x}))        
        self.powerLevel.valueChanged.connect(lambda x: self.parameterChanged.emit({'powerLevel': x}))
        
    @qtc.pyqtSlot()
    def requestAllParameter(self):
        print('requestAllParameter')
        self.parameterChanged.emit({'id': self.id.value(),
                                    'name': self.name.text(),
                                    'mode': self.mode.currentText(),
                                    'rob': self.rob.currentText(),
                                    'mdl': self.mdl.currentText(),
                                    'rate': self.rate.currentText(),
                                    'blockSize': self.blockSize.value(),
                                    'transSize': self.transSize.value(),
                                    'powerLevel': self.powerLevel.value()})
        
    @qtc.pyqtSlot(str)
    def _enableModeChoice(self, text: str):
        if text == 'Auto':
            state = False
        elif text == 'Manual':
            state = True
        else:
            raise ValueError('Wrong item text.')
        self.rob.setEnabled(state)
        self.mdl.setEnabled(state)
        self.rate.setEnabled(state)
        
# simple test
if __name__ == '__main__':
    import utility    
    utility.runManualTest(ModemWidget)