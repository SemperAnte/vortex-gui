# -*- coding: utf-8 -*-
"""
HISTORY:
	Created on Mon May 25 07:12:24 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:

DESCRIPTION:
    
    VX?UVER
    VX?LVER
"""
from PyQt5 import QtCore as qtc

import interfaceTcp
import upperLayerEmulator
import re
import numpy as np

class UpperLayerConnector(qtc.QObject):
    
    layerVersionUpdated = qtc.pyqtSignal(str, str)
    errorShown = qtc.pyqtSignal(str)
    connectionStatusChanged = qtc.pyqtSignal(bool)
    parameterAllRequested = qtc.pyqtSignal()
    infoShown = qtc.pyqtSignal(dict)
    
    TIMEOUT_LIMIT = 5.0
    
    def __init__(self, testMode):  
        super().__init__()
        self.testMode = testMode
        self.con = interfaceTcp.TcpClient()
        self.connectionStatus = False
        
    @qtc.pyqtSlot(dict)
    def requestConnection(self, request: dict):
        if request['action'] == 'Connection':
            if request['type'] == 'Hardware':
                if request['protocol'] == 'TCPIP':
                    if self.testMode:
                        ip = upperLayerEmulator.UpperLayerEmulator.EMULATOR_IP
                        port = upperLayerEmulator.UpperLayerEmulator.EMULATOR_PORT
                    else:
                        if request['ip']:
                            ip = request['ip']
                        else:
                            ip = 'localhost'
                        port = request['port']
                        
                    self.con.setAddress(ip, port)
                    self.con.open()
                    
                    # read versions on connection
                    res = self._requestParameter('VX?UVER', r'VX!UVER (.*)\n')
                    if res:
                        upperLayerVersion = res[0]
                    else:
                        return
                    res = self._requestParameter('VX?LVER', r'VX!LVER (.*)\n')
                    if res:
                        lowerLayerVersion = res[0]
                    else:
                        return
                      
                    self.layerVersionUpdated.emit(upperLayerVersion, lowerLayerVersion)                    
                    self.connectionStatus = True
                    self.connectionStatusChanged.emit(self.connectionStatus)
                    self.parameterAllRequested.emit()
                elif request['protocol'] == 'Serial':
                    self.errorShown.emit('Serial connection is not supported yet.')
                else:
                    raise ValueError('Wrong protocol type.')
            elif request['type'] == 'Emulation':
                self.errorShown.emit('Emulation type is not supported yet.')
            else:
                raise ValueError('Wrong connection type.')
        elif request['action'] == 'Disconnection':
            self.con.close()
            self.layerVersionUpdated.emit('not connected', 'not connected')
            self.connectionStatus = False
            self.connectionStatusChanged.emit(self.connectionStatus)
        else:
            raise ValueError
    
    @qtc.pyqtSlot(dict)
    def changeParameter(self, parm):
        for key, value in parm.items():            
            if self.connectionStatus:
                if key == 'id':
                    self._setParameter('VX!ID', value)                    
                elif key == 'name':
                    self._setParameter('VX!NAME', value)
                elif key == 'mode':
                    self._setParameter('VX!MODE', value)
                elif key == 'rob':
                    self._setParameter('VX!ROB', value)
                elif key == 'mdl':
                    self._setParameter('VX!MDL', value)
                elif key == 'rate':
                    self._setParameter('VX!RATE', value)
                elif key == 'blockSize':
                    self._setParameter('VX!BLOCKSIZE', value)
                elif key == 'transSize':
                    self._setParameter('VX!TRANSSIZE', value)
                elif key == 'powerLevel':
                    self._setParameter('VX!POWERLEVEL', value)
                else:
                    raise ValueError
                    
    @qtc.pyqtSlot()
    def requestInfo(self):
        res = self._requestParameter('VX?INFO', 
                                     r'VX!INFO ([\d+-.e]+?) ([\d+-.e]+?) ([\d+-.e]+?) ([\d+-.e]+?)\n')
        d = None
        if res:
            progress = int(res[0][0])
            datarate = float(res[0][1])
            ber = float(res[0][2])
            bler = float(res[0][3])
            d = {'progress': progress,
                 'datarate': datarate,
                 'ber': ber,
                 'bler': bler}
        else:
            return
        
        res = self._requestStat()        
        if res:
            d['stat'] = res            
            
        res = self._requestImbl()
        if res.size > 1:
            d['imbl'] = res
        
        if d is not None:
            self.infoShown.emit(d)
    
    @qtc.pyqtSlot(np.ndarray)
    def startTransfer(self, image):
        PACKET_SIZE = 8192 # in bytes, for transfer via interface
        for packNum in np.arange(np.ceil(image.size / PACKET_SIZE)).astype(int):
            packNum = int(packNum)
            packByte = image[packNum * PACKET_SIZE:(packNum + 1) * PACKET_SIZE]
            packByte = packByte.tobytes()
            s = 'VX!DATA {:d} '.format(len(packByte)).encode() + packByte + b'\n'
            self.con.write(s)
            self._waitOkResponse(b'VX!DATA ...')
        self._setParameter('VX!START')
        
    @qtc.pyqtSlot()
    def stopTtransfer(self):
        self._setParameter('VX!STOP')
        
    def _requestStat(self):
        self.con.write(('VX?STAT\n').encode()) 
        data = self.con.read(self.TIMEOUT_LIMIT)
        if data[:7] == b'VX!STAT':                   
            startIdx = data.index(b' ') + 1
            endIdx = startIdx + data[startIdx:].index(b' ')
            byteSize = data[startIdx:endIdx]
            byteSize = int(byteSize)
            commandSize = byteSize + endIdx + 1
            res = data[endIdx + 1:commandSize]
            return res.decode()
        else:
            raise IOError
            
    def _requestImbl(self):
        self.con.write(('VX?IMBL\n').encode()) 
        data = self.con.read(self.TIMEOUT_LIMIT)
        if data[:7] == b'VX!IMBL':             
            startIdx = data.index(b' ') + 1
            endIdx = startIdx + data[startIdx:].index(b' ')
            byteSize = data[startIdx:endIdx]
            byteSize = int(byteSize)
            commandSize = byteSize + endIdx + 1
            res = data[endIdx + 1:commandSize]
            res = np.frombuffer(res, dtype = np.uint8)
            return res
        else:
            raise IOError

    def _requestParameter(self, req, pattern):
        self.con.write((req + '\n').encode())       
        data = self.con.read(self.TIMEOUT_LIMIT)
        data = data.decode()
        res = re.findall(pattern, data)
        if not res:
            self.con.close()
            self.errorShown.emit('Can not connect to upper layer.\n\n No response for command {}.'.format(req))
            self.connectionStatus = False
            self.connectionStatusChanged.emit(self.connectionStatus)
        return res
            
    def _setParameter(self, cmd, value = None):
        if value is None:
            cmd = cmd + '\n'
            cmd = cmd.encode()
        else:
            value = str(value)
            cmd = cmd + ' ' + value.upper() + '\n'
            cmd = cmd.encode()
        self.con.write(cmd)
        self._waitOkResponse(cmd)
                    
    def _waitOkResponse(self, cmd):
        data = self.con.read(self.TIMEOUT_LIMIT)
        if not data == b'VX!OK\n':               
            self.con.close()
            self.errorShown.emit('Can not connect to upper layer.\n\n No ok acknowledgement for command {}.'.\
                                 format(cmd.decode()))
            self.connectionStatus = False
            self.connectionStatusChanged.emit(self.connectionStatus)
    
    def close(self):
        self.con.close()    