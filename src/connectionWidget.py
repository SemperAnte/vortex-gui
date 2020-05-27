# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Fri May 22 23:39:22 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), dive-link@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    [x] switch widget
    [x] ip address validator
    [x] emulation file dialog
    [x] waiting for connection widget
    [ ] signal/slot functions
    
DESCRIPTION:
    Connection Widget
        signals:
            commandSend
        slots:
            receiveCommand
"""
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import time
import utility
        
class ConnectionWidget(qtw.QGroupBox):
    
    commandSend = qtc.pyqtSignal()
    
    WIDGET_TITLE = 'Connection options'
    DEFAULT_IP_PORT = 10204
    MIN_IP_PORT = 0
    MAX_IP_PORT = 2**16 - 1
    DEFAULT_IP_ADDRESS = '192.168.1.180'    
    CONNECTION_BUTTON_ON_ICON_PATH = 'res\\connectionButtonOn.png'
    CONNECTION_BUTTON_OFF_ICON_PATH = 'res\\connectionButtonOff.png'
    STATUS_LABEL = 'Status: '
    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self._setupUi()
        
        self.connectionStatus = False
        self.emulationPath = qtc.QDir.currentPath()
        self.comPortList = utility.getComPortList()    
    
    @property
    def connectionStatus(self):
        return self._connectionStatus
    @connectionStatus.setter
    def connectionStatus(self, value):
        self._connectionStatus = value
        
        self.switch.setEnabled(not self._connectionStatus)
        if self._connectionStatus:
            self.connectionButton.setText('Disconnect')
            self.connectionButton.setIcon(self.connectionButtonIconOn)
            statusStr = 'connected'
        else:
            self.connectionButton.setText('Connect')
            self.connectionButton.setIcon(self.connectionButtonIconOff)
            statusStr = 'not connected'   
        self.statusLabel.setText(self.STATUS_LABEL + statusStr)
        
    @property
    def emulationPath(self):
        return self._emulationPath
    @emulationPath.setter
    def emulationPath(self, value):
        self._emulationPath = value
        self.pathLine.setText(self._emulationPath)
        
    @property
    def comPortList(self):
        return self._comPortList
    @comPortList.setter
    def comPortList(self, value):
        self._comPortList = value
        self.comPort.clear()
        self.comPort.addItems(self._comPortList)    
        
    @qtc.pyqtSlot(dict)
    def receiveCommand(opt):
        pass
        
    def _setupUi(self):        
        self.setTitle(self.WIDGET_TITLE)       
        
        self.type = qtw.QComboBox()
        self.type.addItems(['Hardware', 'Emulation'])
        
        # stackForType - pageHardware - stackForProtocol - pageIp 
        #              \ pageEmulation                   \ pageCom
        self.ipAdr = qtw.QLineEdit()
        self.ipAdr.setText(self.DEFAULT_IP_ADDRESS)
        self.ipAdr.setValidator(utility.IpAdrValidator())
        self.ipPort = qtw.QSpinBox()
        self.ipPort.setMinimum(self.MIN_IP_PORT)
        self.ipPort.setMaximum(self.MAX_IP_PORT)
        self.ipPort.setValue(self.DEFAULT_IP_PORT)
        pageIp = qtw.QWidget()
        pageIp.setLayout(qtw.QFormLayout())
        pageIp.layout().setContentsMargins(0, 0, 0, 0)
        pageIp.layout().addRow('Address', self.ipAdr)
        pageIp.layout().addRow('Port', self.ipPort)
        
        self.comPort = qtw.QComboBox() # show self.comPortList
        pageCom = qtw.QWidget()
        pageCom.setLayout(qtw.QFormLayout())
        pageCom.layout().setContentsMargins(0, 0, 0, 0)
        pageCom.layout().addRow('Port', self.comPort)
        self.stackForProtocol = qtw.QStackedWidget()
        self.stackForProtocol.addWidget(pageIp)
        self.stackForProtocol.addWidget(pageCom)
        
        self.protocol = qtw.QComboBox()
        self.protocol.addItems(['TCPIP', 'Serial'])          
        pageHardware = qtw.QWidget()
        pageHardware.setLayout(qtw.QFormLayout())
        pageHardware.layout().setContentsMargins(0, 0, 0, 0)
        pageHardware.layout().addRow('Protocol', self.protocol)
        pageHardware.layout().addRow(self.stackForProtocol) 
        
        self.pathLine = qtw.QLineEdit() # show self.emulationPath
        self.pathButton = qtw.QPushButton('...')
        self.pathButton.setMaximumSize(24, 24) 
        pathWidget = qtw.QWidget()
        pathWidget.setLayout(qtw.QHBoxLayout())
        pathWidget.layout().setContentsMargins(0, 0, 0, 0)
        pathWidget.layout().addWidget(self.pathLine)
        pathWidget.layout().addWidget(self.pathButton)
        
        pageEmulation = qtw.QWidget()
        pageEmulation.setLayout(qtw.QFormLayout())
        pageEmulation.layout().setContentsMargins(0, 0, 0, 0)
        pageEmulation.layout().addRow('Path', pathWidget)
        self.stackForType = qtw.QStackedWidget()
        self.stackForType.addWidget(pageHardware)
        self.stackForType.addWidget(pageEmulation)
        
        self.switch = qtw.QWidget()
        self.switch.setLayout(qtw.QFormLayout())
        self.switch.layout().setContentsMargins(0, 0, 0, 0)
        self.switch.layout().addRow('Type', self.type)
        self.switch.layout().addRow(self.stackForType)
        utility.alignLabelWidth(self.switch.layout())
        
        # control button Connect/Disconnect
        self.connectionButton = qtw.QPushButton()
        self.connectionButton.setCheckable(True)
        self.connectionButtonIconOn = qtg.QIcon(self.CONNECTION_BUTTON_ON_ICON_PATH)
        self.connectionButtonIconOff = qtg.QIcon(self.CONNECTION_BUTTON_OFF_ICON_PATH) # no state argument here
                
        self.statusLabel = qtw.QLabel() # show self.connectionStatus          
         
        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(self.switch)
        self.layout().addWidget(self.connectionButton)
        self.layout().addWidget(self.statusLabel)
        
        # signal-slot connections
        self.protocol.currentIndexChanged.connect(self.stackForProtocol.setCurrentIndex)
        self.type.currentIndexChanged.connect(self.stackForType.setCurrentIndex) 
        self.pathButton.clicked.connect(self._openEmulationFile)
        self.connectionButton.clicked.connect(self._clickConnectionButton)
        
    @qtc.pyqtSlot(bool)
    def _clickConnectionButton(self, state):      
        _ConnectingWindow.show(self)
        self.commandSend.emit()
        self.connectionStatus = state
        
    def _openEmulationFile(self):
        fileName, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select emulation run file to open ...",
            self.emulationPath,
            'Python Files (*.py) ;;All Files (*)',
            'Python Files (*.py)',
            qtw.QFileDialog.DontUseNativeDialog |
            qtw.QFileDialog.DontResolveSymlinks
        )
        if fileName:
            self.emulationPath = fileName
            
class _ConnectingWindow(qtw.QDialog):
    
    WAITING_TIME = 2 # in sec

    def __init__(self, parent = None):
        if parent is not None:
            if parent.parent() is not None:
                parent = parent.parent()
        super().__init__(parent)
        
        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(qtw.QLabel('Connecting ...'))
        
    @staticmethod
    def show(parent = None):
        win = _ConnectingWindow(parent)
        win.setWindowFlags(qtc.Qt.FramelessWindowHint | qtc.Qt.Dialog)
        win.open()
        qtw.QApplication.processEvents()
        time.sleep(_ConnectingWindow.WAITING_TIME)
        win.accept()        
        
# simple test
if __name__ == '__main__':
    
    utility.runManualTest(ConnectionWidget)