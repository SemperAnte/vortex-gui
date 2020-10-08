# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Fri May 22 22:50:17 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), dive-link@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    
DESCRIPTION:
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import sys
sys.path.append('src')
from connectionWidget import ConnectionWidget
from modemWidget import ModemWidget
from transferWidget import TransferWidget
from informationWidget import InformationWidget

from upperLayerConnector import UpperLayerConnector
from upperLayerEmulator import UpperLayerEmulator

sys.path.append('res')
import resources

class MainWindow(qtw.QMainWindow):
    
    APPLICATION_VERSION = '0.2'
    
    APPLICATION_TITLE = 'Vortex GUI'
    APPLICATION_ICON_PATH = ':\\images\\vortexIcon.ico'
    
    # test application using emulator of upper layer (localhost server)
    RUN_UPPER_LAYER_EMULATOR = False
    
    def __init__(self):
        super().__init__()
        
        self.updateLayerVersion('not connected', 'not connected') # unknown, read on connection

        self._setupUi()
        self.show()
        
    def _setupUi(self):
        self.setWindowTitle(f'{self.APPLICATION_TITLE} for Underwater Modem')
        self.setWindowIcon(qtg.QIcon(self.APPLICATION_ICON_PATH))
        
        centralWidget = qtw.QWidget()
        leftWidget = qtw.QWidget()
        rightWidget = qtw.QWidget()
        centralWidget.setLayout(qtw.QHBoxLayout())        
        leftWidget.setLayout(qtw.QVBoxLayout())
        rightWidget.setLayout(qtw.QVBoxLayout())
        centralWidget.layout().addWidget(leftWidget)
        centralWidget.layout().addWidget(rightWidget)        
        centralWidget.layout().setAlignment(leftWidget, qtc.Qt.AlignTop)
        leftWidget.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Preferred)
        self.setCentralWidget(centralWidget)        
        
        self.connectionWidget = ConnectionWidget(parent = self)
        self.modemWidget = ModemWidget(parent = self)    
        self.transferWidget = TransferWidget(parent = self)
        self.informationWidget = InformationWidget(parent = self)
        leftWidget.layout().addWidget(self.connectionWidget)
        leftWidget.layout().addWidget(self.modemWidget)
        rightWidget.layout().addWidget(self.informationWidget)
        rightWidget.layout().addWidget(self.transferWidget)
        self.transferWidget.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Maximum)
        
        self.upperLayerConnector = UpperLayerConnector(self.RUN_UPPER_LAYER_EMULATOR)
        
        if self.RUN_UPPER_LAYER_EMULATOR:
            self.upperLayerEmulator = UpperLayerEmulator()
            self.upperLayerEmulator.open()
        
        # menu bar
        menuSet = self.menuBar().addMenu('Settings')
        menuSet.addAction('Audio')
        menuSet.addAction('Language')
        
        menuHelp = self.menuBar().addMenu('Help')        
        menuHelp.addAction('About', self.showAboutDialog)
        
        # status bar
        self.statusBar().showMessage(f'Welcome to {self.APPLICATION_TITLE}!')
        
        # signal-slot connections
        self.connectionWidget.connectionRequested.connect(self.upperLayerConnector.requestConnection)
        self.upperLayerConnector.connectionStatusChanged.connect(self.connectionWidget.changeConnectionStatus)
        self.upperLayerConnector.errorShown.connect(self.connectionWidget.showError)
        self.upperLayerConnector.layerVersionUpdated.connect(self.updateLayerVersion)
        self.upperLayerConnector.parameterAllRequested.connect(self.modemWidget.requestAllParameter)
        
        self.modemWidget.parameterChanged.connect(self.upperLayerConnector.changeParameter)
        
        self.transferWidget.imageLoaded.connect(self.informationWidget.loadImage)
        self.transferWidget.transferStarted.connect(self.informationWidget.startImage)
        self.transferWidget.transferStopped.connect(self.informationWidget.clearImage)
        
        self.transferWidget.transferStarted.connect(self.upperLayerConnector.startTransfer)
        self.transferWidget.transferStopped.connect(self.upperLayerConnector.stopTtransfer)
        
        self.informationWidget.infoRequested.connect(self.upperLayerConnector.requestInfo)
        self.upperLayerConnector.infoShown.connect(self.informationWidget.showInfo)
        
    def closeEvent(self, event):
        self.upperLayerConnector.close()
        if self.RUN_UPPER_LAYER_EMULATOR:
            self.upperLayerEmulator.close()
        event.accept()
        
    def showAboutDialog(self):            
        qtw.QMessageBox.about(
            self,
            f'About {self.APPLICATION_TITLE}',
            f'{self.APPLICATION_TITLE}: v{self.APPLICATION_VERSION}\n' +
            f'Upper Layer: {self.upperLayerVersion}\n' +
            f'Lower Layer: {self.lowerLayerVersion}\n\n' +
            'www.dive-link.net'
        )
        
    @qtc.pyqtSlot(str, str)
    def updateLayerVersion(self, upperLayerVersion: str, lowerLayerVersion: str):
        self.upperLayerVersion = upperLayerVersion
        self.lowerLayerVersion = lowerLayerVersion
        
if __name__ == '__main__':
    if 'app' in globals():
        del app
    if 'mw' in globals():
        del mw
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())