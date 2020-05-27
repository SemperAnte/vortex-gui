# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Tue May 26 22:32:49 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    [ ] change to more model-view structure
    
DESCRIPTION:
    TransferWidget
        signals:
            imageLoaded
            transferStarted
            transferStopped
"""
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import matplotlib.image as mpimg
import numpy as np

class TransferWidget(qtw.QGroupBox):
    
    imageLoaded = qtc.pyqtSignal(np.ndarray)
    transferStarted = qtc.pyqtSignal()
    transferStopped = qtc.pyqtSignal()
    
    WIDGET_TITLE = 'Modem options'
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self._setupUi()
    
    def _setupUi(self):  
        self.setTitle(self.WIDGET_TITLE)
        
        # transfer type button group
        self.file = qtw.QRadioButton('File')
        self.image = qtw.QRadioButton('Image') 
        self.voice = qtw.QRadioButton('Voice')        
        self.message = qtw.QRadioButton('Message') 
        self.file.click()
        self.typeGroup = qtw.QButtonGroup()
        self.typeGroup.addButton(self.file)
        self.typeGroup.addButton(self.image)
        self.typeGroup.addButton(self.voice)
        self.typeGroup.addButton(self.message)
        self.typeWidget = qtw.QWidget()
        self.typeWidget.setLayout(qtw.QHBoxLayout())
        self.typeWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.typeWidget.layout().addWidget(self.file)
        self.typeWidget.layout().addWidget(self.image)
        self.typeWidget.layout().addWidget(self.voice)
        self.typeWidget.layout().addWidget(self.message)
        
        self.startButton = qtw.QPushButton('Start')
        self.startButton.setCheckable(True)
        self.stopButton = qtw.QPushButton('Stop')
        self.loadButton = qtw.QPushButton('Load')
        self.fileLabel = qtw.QLabel('No file')         
        
        self.setLayout(qtw.QGridLayout())
        self.layout().addWidget(self.typeWidget, 0, 0, 1, 2)
        self.layout().addWidget(self.loadButton, 1, 0)
        self.layout().addWidget(self.fileLabel, 1, 1)
        self.layout().addWidget(self.startButton, 2, 0)
        self.layout().addWidget(self.stopButton, 2, 1)      
        
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        
        # signal-slot connections
        self.loadButton.clicked.connect(self._openFile)
        self.startButton.clicked.connect(self._startTransfer)
        self.stopButton.clicked.connect(self._stopTransfer)
      
    @qtc.pyqtSlot()
    def _openFile(self):
        fileName, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select image to transfer ...",
            qtc.QDir.currentPath(),
            'PNG Files (*.png) ;;All Files (*)',
            'PNG Files (*.png)',
            qtw.QFileDialog.DontUseNativeDialog | 
            qtw.QFileDialog.DontResolveSymlinks
        )
        if fileName:
            image = mpimg.imread(fileName) 
            self.fileLabel.setText(f'Size: {image.size} bytes')
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.imageLoaded.emit(image)
        else:
            self.fileLabel.setText('No file')
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(False)
    
    @qtc.pyqtSlot()
    def _startTransfer(self):
        self.typeWidget.setEnabled(False)
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)        
        self.loadButton.setEnabled(False)
        
        self.transferStarted.emit()
    
    @qtc.pyqtSlot()
    def _stopTransfer(self):
        self.typeWidget.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.loadButton.setEnabled(True)

        self.transferStopped.emit()

# simple test
if __name__ == '__main__':
    import utility    
    utility.runManualTest(TransferWidget)