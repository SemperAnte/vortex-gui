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

import sys
sys.path.append('src')

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from connectionWidget import ConnectionWidget
from modemWidget import ModemWidget
from transferWidget import TransferWidget
from informationWidget import InformationWidget

class MainWindow(qtw.QMainWindow):
    
    VERSION_MAJOR = 0
    VERSION_MINOR = 2
    
    PROGRAM_TITLE = 'Vortex GUI'
    PROGRAM_ICON_PATH = 'res\\vortexIcon.ico'
    
    def __init__(self):
        super().__init__()
        
        self._setupUi()
        self.show()
        
    def _setupUi(self):
        self.setWindowTitle(f'{self.PROGRAM_TITLE} for Underwater Modem')
        self.setWindowIcon(qtg.QIcon(self.PROGRAM_ICON_PATH))
        
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
        
        # menu bar
        menuSet = self.menuBar().addMenu('Settings')
        menuSet.addAction('Audio')
        menuSet.addAction('Language')
        
        menuHelp = self.menuBar().addMenu('Help')        
        menuHelp.addAction('About', self.showAboutDialog)
        
        # status bar
        self.statusBar().showMessage(f'Welcome to {self.PROGRAM_TITLE}!')
        
        # signal-slot connections
        self.transferWidget.imageLoaded.connect(self.informationWidget.loadImage)
        self.transferWidget.transferStarted.connect(self.informationWidget.startImage)
        self.transferWidget.transferStopped.connect(self.informationWidget.clearImage)
        
    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            f'About {self.PROGRAM_TITLE}',
            f'{self.PROGRAM_TITLE} v{self.VERSION_MAJOR}.{self.VERSION_MINOR}\n\n' +
            'www.dive-link.net'
        )
        
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())