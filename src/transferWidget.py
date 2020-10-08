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
    transferStarted = qtc.pyqtSignal(np.ndarray)
    transferStopped = qtc.pyqtSignal()
    
    WIDGET_TITLE = 'Modem options'
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.imageSize = 0
        self.imageSource = []
        
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
            if self._processImage(image):                 
                self.fileLabel.setText(f'Size: {self.imageSize} bytes')
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.imageLoaded.emit(image)
            else:
                self.fileLabel.setText('No file')
                self.startButton.setEnabled(False)
                self.stopButton.setEnabled(False)   
        else:
            self.fileLabel.setText('No file')
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            
    def _processImage(self, image):       
        # remove alpha channel
        if image.shape[2] == 4:
            image = image[:, :, 0:3]
        image = (image * np.iinfo(np.uint8).max).astype(np.uint8)
        self.imageSize = image.size
        
        dataType = 2 # type of image data
        dataType = np.atleast_1d(np.uint8(dataType))
        imageWidth = image.shape[0]
        if imageWidth > np.iinfo(np.uint16).max:
            self.showError('Too much width of image.')
            return False
        else:
            imageWidth = np.atleast_1d(np.uint16(imageWidth)).view(np.uint8)
        imageHeight = image.shape[1]
        if imageHeight > np.iinfo(np.uint16).max:
            self.showError('Too much height of image.')
            return False
        else:
            imageHeight = np.atleast_1d(np.uint16(imageHeight)).view(np.uint8)    
        
        dataSizeByte = 1 + 2 + 2 + image.size
        if dataSizeByte > np.iinfo(np.uint32).max:
            self.showError('Too much size of image.')
            return False
        else:
            dataSizeByte = np.atleast_1d(np.uint32(dataSizeByte)).view(np.uint8)
         
        self.imageSource = np.concatenate((dataType, imageHeight, imageWidth, np.ravel(image))) 
        return True
            
    @qtc.pyqtSlot(str)
    def showError(self, text):
        qtw.QMessageBox.warning(
            self,
            'Transfer Error',
            text)    
    
    @qtc.pyqtSlot()
    def _startTransfer(self):
        self.typeWidget.setEnabled(False)
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.loadButton.setEnabled(False)
        
        self.transferStarted.emit(self.imageSource)
    
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