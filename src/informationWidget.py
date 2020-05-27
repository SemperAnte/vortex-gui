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
    
    WIDGET_TITLE = 'Information'
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.progressValue = 0
        self.art = None
        self.bytesSend = 0
        self.num = 1
        
        self._setupUi()
        
        self.timer = qtc.QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self._stepImage)
        
    @qtc.pyqtSlot(np.ndarray)
    def loadImage(self, image):
        # remove alpha channel
        if image.shape[2] == 4:
            image = image[:, :, 0:3]
            self.imageSource = (image * np.iinfo(np.uint8).max).astype(np.uint8)
            
        self.imageSourceLine = self.imageSource.view()
        self.imageSourceLine.shape = (-1, 3)
            
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')
        self.art = self.ax.imshow(self.imageSource, interpolation = None)
        self.canvas.draw()
        
    @qtc.pyqtSlot()
    def startImage(self):
        self.stat.append('        Pack N|     TX, bytes|    ACK, bytes|         Total|   Rate, bit\s|')
        self.stat.append('---------------------------------------------------------------------------')
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
        self.dataTime = qtw.QLabel('Time remaining: 0 s')
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
        
    def _stepImage(self):
        BITRATE = 3500
        
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
        
        bler = 1.11e-2+ random.uniform(-0.06e-2, 0.06e-2)
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

# simple test
if __name__ == '__main__':
    import utility    
    utility.runManualTest(InformationWidget)