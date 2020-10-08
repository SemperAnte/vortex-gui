# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Wed May 27 14:27:16 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:

DESCRIPTION:    
    InformationWidget
        slots:
            loadImage
            startImage
            clearImage
"""
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np
import random

class InformationWidget(qtw.QGroupBox):
    
    infoRequested = qtc.pyqtSignal()
    
    WIDGET_TITLE = 'Information'
    TIMER_INTERVAL = 2.0
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.progressValue = 0
        self.art = None
        self.bytesSend = 0
        self.num = 1
        
        self._setupUi()
        
        self.timer = qtc.QTimer()
        self.timer.setInterval(int(self.TIMER_INTERVAL * 1000))
        self.timer.timeout.connect(self.infoRequested)
        
    @qtc.pyqtSlot(np.ndarray)
    def loadImage(self, image):
        # remove alpha channel
        if image.shape[2] == 4:
            image = image[:, :, 0:3]
        self.imageSource = (image * np.iinfo(np.uint8).max).astype(np.uint8)
        
        numBlock = np.ceil(self.imageSource.size * 8 / 288).astype(int)
        imageCopy = self.imageSource.flatten()
        imageCopy = np.unpackbits(imageCopy)
        imageCopy.resize((numBlock, 288))
        self.imageCopy = imageCopy.T
            
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')
        self.art = self.ax.imshow(self.imageSource, interpolation = None)
        self.canvas.draw()
    
    @qtc.pyqtSlot()
    def startImage(self):
        self.timer.start()
    
    @qtc.pyqtSlot()
    def clearImage(self):      
        self.timer.stop()
        
        self.bytesSend = 0
        self.progressValue = 0
        self.progress.setValue(self.progressValue)
        
    def _setupUi(self):  
        self.setTitle(self.WIDGET_TITLE)
        
        monospaceFont = qtg.QFont('Courier New', 9)
        
        self.stat = qtw.QTextEdit()
        self.stat.setReadOnly(True)
        self.stat.setCurrentFont(monospaceFont)
        self.statCursor = self.stat.textCursor()
        self.log = qtw.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setCurrentFont(monospaceFont) 
        self.tab = qtw.QTabWidget()
        self.tab.addTab(self.stat, 'Statistics')
        self.tab.addTab(self.log, 'Log')
        self.tab.setMinimumWidth(750)
        self.tab.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Maximum)

        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.progress = qtw.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(self.progressValue)
        # data widget
        self.dataTime = qtw.QLabel('Time remaining: -')
        self.dataRate = qtw.QLabel('Bitrate: 0 bit/s')
        self.dataBer = qtw.QLabel('BER: 0.0')
        self.dataBler = qtw.QLabel('BLER: 0.0')
        self.dataWidget = qtw.QWidget()        
        self.dataWidget.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Maximum)
        self.dataWidget.setLayout(qtw.QGridLayout())
        self.dataWidget.layout().setContentsMargins(0, 0, 0, 0)        
        self.dataWidget.layout().addWidget(self.dataTime, 0, 0)
        self.dataWidget.layout().addWidget(self.dataRate, 1, 0)
        self.dataWidget.layout().addWidget(self.dataBer, 0, 1)
        self.dataWidget.layout().addWidget(self.dataBler, 1, 1)
        
        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(self.tab)
        self.layout().addWidget(self.canvas)
        self.layout().addWidget(self.progress)
        self.layout().addWidget(self.dataWidget)
        
    @qtc.pyqtSlot(dict)
    def showInfo(self, info):
        for key, value in info.items():
            if key == 'progress':
                self.progress.setValue(value)
            elif key == 'datarate':
                self.dataRate.setText('Bitrate: {0:.1f} bit/s'.format(value))
            elif key == 'ber':
                self.dataBer.setText('BER: {0:.2e}'.format(value))
            elif key == 'bler':
                self.dataBler.setText('BLER: {0:.2e}'.format(value))
            elif key == 'stat':        
                self.stat.insertPlainText(value)
                self.statCursor.movePosition(qtg.QTextCursor.End)
                self.stat.setTextCursor(self.statCursor)
            elif key == 'imbl':         
                idx = np.unpackbits(value).astype(np.bool)  
                idx = idx[:self.imageCopy.shape[1]]   
                print(f'size = {idx.size}, {idx}')
                
                imageSink = np.full_like(self.imageCopy, np.iinfo(np.uint8).max)
                imageSink[:, idx] = self.imageCopy[:, idx]              
                imageSink = imageSink.T.flatten()
                imageSink = np.packbits(imageSink)
                imageSink.resize(self.imageSource.shape)         
                
                self.art.set_data(imageSink)
                self.canvas.draw()
            else:
                raise NameError        
        
    '''
    def _stepImage(self):
        BITRATE = 874
        
        self.bytesSend += 2 * BITRATE / 8
        if self.bytesSend > self.imageSource.size:
            self.bytesSend = self.imageSource.size
        self.progressValue = self.bytesSend / self.imageSource.size * 100
        self.progress.setValue(self.progressValue)
        
        time = (100 - self.progressValue) / 100 * (self.imageSource.size * 8 / BITRATE)
        self.dataTime.setText(f'Time remaining: {time:.1f} s')
        
        rate = BITRATE + random.uniform(-300, 300)
        self.dataRate.setText(f'Bitrate: {rate:.1f} bit/s')
        
        ber = 2.03e-4 + random.uniform(-0.11e-4, 0.11e-4)
        self.dataBer.setText(f'BER: {ber:.2e}')
        
        bler = 1.11e-2 + random.uniform(-0.06e-2, 0.06e-2)
        self.dataBler.setText(f'BLER: {bler:.2e}')
        
        imageSink = np.full_like(self.imageSource, np.iinfo(np.uint8).max)
        imageSinkLine = imageSink.view()
        imageSinkLine.shape = self.imageSourceLine.shape
        n = self.progressValue / 100 * self.imageSourceLine.shape[0]
        n = int(n)
        imageSinkLine[0:n, :] = self.imageSourceLine[0:n, :]
        self.art.set_data(imageSink)
        self.canvas.draw()
        
        b = 960 - int(random.uniform(0, 40))
        self.stat.append(f'{self.num:14d}|           960|{b:14d}|{self.progressValue:13.1f}%|{rate:14.1f}|')
        self.num += 1
    '''

# simple test
if __name__ == '__main__':
    import utility    
    utility.runManualTest(InformationWidget)