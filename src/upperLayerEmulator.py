# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Thu Sep  3 15:53:05 2020

Project: Vortex Upper Layer

Author: DIVE-LINK (www.dive-link.net), dive-link@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    
DESCRIPTION:
"""
import numpy as np
import re
import threading

import interfaceTcp
import commandProcessor

class UpperLayerEmulator():
    
    EMULATOR_IP = 'localhost'
    EMULATOR_PORT = 10204
    
    UPPER_LAYER_VERSION = '0.41 emu'
    LOWER_LAYER_VERSION = '0.39 emu'
    
    TIMEOUT_LIMIT = 1.0
            
    def open(self):
        self.server = interfaceTcp.TcpServer()
        self.server.setAddress(self.EMULATOR_IP, self.EMULATOR_PORT)
        self.server.open()
        self.thread = threading.Thread(target = self._service)
        self.thread.start()
        
        self.commandProcessor = commandProcessor.CommandProcessor()
        
        self.id = None
        self.name = None
        self.mode = None
        self.rob = None
        self.mdl = None
        self.rate = None
        self.blockSize = None
        self.transSize = None
        self.powerLevel = None
        self.imageSource = None
        self.start = None
        self.stop = None
        self.progress = 0
        self.datarate = 1345.2
        self.ber = 2.35e-3
        self.bler = 1.34e-2
        self.stat = '        Pack N|     TX, bytes|    ACK, bytes|         Total|   Rate, bit\s|'
            
    def close(self):        
        if self.server is not None:
            self.server.close()
            self.server = None
            self.thread.join()
            
    def _service(self):
        while True:
            data = self.server.read(self.TIMEOUT_LIMIT)
            commandFound = self.commandProcessor.process(data)
            for data in commandFound:
                if data == b'VX?UVER\n':
                    self.server.write('VX!UVER {}\n'.format(self.UPPER_LAYER_VERSION).encode())
                elif data == b'VX?LVER\n':
                    self.server.write('VX!LVER {}\n'.format(self.LOWER_LAYER_VERSION).encode())
                elif data[:7] == b'VX!DATA':                   
                    startIdx = data.index(b' ') + 1
                    endIdx = startIdx + data[startIdx:].index(b' ')
                    byteSize = data[startIdx:endIdx]
                    byteSize = int(byteSize)
                    commandSize = byteSize + endIdx + 1
                    res = data[endIdx + 1:commandSize]
                    res = np.frombuffer(res, dtype = np.uint8)
                    if self.imageSource is None:
                        self.imageSource = res
                    else:
                        self.imageSource = np.concatenate((self.imageSource, res))
                else:                
                    data = data.decode(encoding="ascii", errors="ignore")
                    res = re.findall(r'VX!ID (\d+)\n', data)
                    if res:
                        self.id = int(res[0])
                        print('id = {}'.format(self.id))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!NAME (\w+)\n', data)
                    if res:
                        self.name = res[0]
                        print('name = {}'.format(self.name))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!MODE (\w+)\n', data)
                    if res:
                        self.mode = res[0].capitalize()
                        print('mode = {}'.format(self.mode))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!ROB (\w)\n', data)                
                    if res:
                        self.rob = res[0]
                        print('rob = {}'.format(self.rob))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!MDL (\w+)\n', data)                
                    if res:
                        self.mdl = res[0]
                        print('mdl = {}'.format(self.mdl))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!RATE ([\d/]+)\n', data)                
                    if res:
                        self.rate = res[0]
                        print('rate = {}'.format(self.rate))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!BLOCKSIZE (\d+)\n', data)                
                    if res:
                        self.blockSize = res[0]
                        print('blockSize = {}'.format(self.blockSize))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!TRANSSIZE (\d+)\n', data)                
                    if res:
                        self.transSize = res[0]
                        print('transSize = {}'.format(self.transSize))
                        self.server.write(b'VX!OK\n')
                        
                    res = re.findall(r'VX!POWERLEVEL (\d+)\n', data)                
                    if res:
                        self.powerLevel = res[0]
                        print('powerLevel = {}'.format(self.powerLevel))
                        self.server.write(b'VX!OK\n')
                        
                    if data == 'VX!START\n':
                        self.server.write(b'VX!OK\n')
                        
                    if data == 'VX!STOP\n':
                        print('stop transfer')
                        self.server.write(b'VX!OK\n')
                        
                    if data == 'VX?INFO\n':
                        print('request for info')
                        data = 'VX!INFO {progress:d} {datarate:.1f} {ber:.2e} {bler:.2e}\n'.\
                                                format(progress = self.progress,
                                                       datarate = self.datarate,
                                                       ber = self.ber,
                                                       bler = self.bler)
                        self.server.write(data.encode())
                        if self.progress < 100:
                            self.progress += 1
                            
                    if data == 'VX?STAT\n':                    
                        data = 'VX!STAT {}\n'.format(self.stat)
                        self.server.write(data.encode())
            
            if self.server is None:                
                break
            
    def __del__(self):
        self.close()
        
if __name__ == '__main__':
    emu = UpperLayerEmulator()
    emu.open()
    emu.close()
