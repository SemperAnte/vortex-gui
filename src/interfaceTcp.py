# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 12:16:32 2020

@author: Shustov Aleksey, semete@semte.ru

TcpServer and TcpClient socket classes running in separated thread.

TcpServer available public methods:
    - setAddress
    - setEcho
    - open
    - isOpened
    - hasConnection
    - write
    - read
    - close
    
TcpClient available public methods:
    - setAddress
    - open
    - isOpened
    - write
    - read
    - close
"""
import abc
import enum
import queue
import threading
import time
import socket
import weakref

class TcpRole(enum.Enum):    
    SERVER = 0
    CLIENT = 1

class TcpAbc(abc.ABC):
    
    DEFAULT_IP = 'localhost'
    DEFAULT_PORT = 10204
    PACKET_SIZE = 2 ** 10   # how much bytes connection send or receive for one network operation
    TIMEOUT_LIMIT = 1.0     # in seconds, timeout for all blocking operations
    
    ERROR_ALREADY_OPEN = IOError('connection is already opened.')
    ERROR_WRITE_CLOSE = IOError('attempt to write to closed connection.')
    ERROR_READ_CLOSE = IOError('attempt to write to closed connection.')

    @abc.abstractmethod
    def __init__(self, role: TcpRole):
        self.role = role
        self.logger = TcpLogger(self)
        
        self.ip = self.DEFAULT_IP
        self.port = self.DEFAULT_PORT        
        
        self.bufRead = queue.Queue()
        self.bufWrite = queue.Queue()
        
        self.threadWrite = None
        self.threadRead = None
        self.threadFinish = False # finish all running threads for accelerating closing operations
        
        self.lockWrite = threading.Lock()
        self.lockRead = threading.Lock()
        
        self.sock = None
        
    def setAddress(self, ip: str, port: int):
        ''' use for setting ip address and port berfore opening '''
        if not self.isOpened():
            self.ip = ip
            self.port = port
        else:
            raise self._raiseError(self.ERROR_ALREADY_OPEN)
    
    @abc.abstractmethod
    def open(self):
        if not self.isOpened():
            while not self.bufRead.empty():
                self.bufRead.get_nowait()
            while not self.bufWrite.empty():
                self.bufWrite.get_nowait()
                
            self.threadFinish = False
            self.threadWrite = threading.Thread(target = self._serviceWrite)
            self.threadRead = threading.Thread(target = self._serviceRead)
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            self.sock.settimeout(self.TIMEOUT_LIMIT)
            self.logger.log('opened.', TcpLogLevel.INFO)
        else:
            raise self._raiseError(self.ERROR_ALREADY_OPEN)
        
    def isOpened(self):
        return self.sock is not None
    
    def write(self, data: bytearray):
        if self.isOpened():    
            for packet in self._splitToPacket(data):
                self.bufWrite.put_nowait(packet)
        else:
            self._raiseError(self.ERROR_WRITE_CLOSE)
            
    def read(self, timeout: float = 0) -> bytearray:
        if self.isOpened():
            try:
                if timeout > 0:
                    data = self.bufRead.get(True, timeout)
                else:
                    data = self.bufRead.get_nowait()
            except queue.Empty:
                data = b''
            finally:
                return data
        else:
            self._raiseError(self.ERROR_READ_CLOSE)
            
    def close(self):
        self.threadFinish = True
        with self.lockRead, self.lockWrite:        
            if self.isOpened():            
                self.sock.close()
                self.sock = None
                self.logger.log('closed.', TcpLogLevel.INFO)            
        if self.threadWrite is not None:
            self.threadWrite.join()
        if self.threadRead is not None:
            self.threadRead.join()    
            
    def _splitToPacket(self, data: bytearray) -> list:
        if len(data) <= self.PACKET_SIZE:
            return [data]
        else:
            return [data[self.PACKET_SIZE*i: self.PACKET_SIZE*(i+1)] \
                        for i in range(len(data) // self.PACKET_SIZE + bool(len(data) % self.PACKET_SIZE))]
            
    def _serviceWrite(self):
        while True:            
            if self.threadFinish:
                break
            else:
                with self.lockWrite:
                    if self.isOpened():
                        try:                        
                            data = self.bufWrite.get(block = True, timeout = self.TIMEOUT_LIMIT)                                              
                        except queue.Empty:
                            pass
                        else:
                            numByte = 0
                            while numByte < len(data):
                                data = data[numByte:]
                                try:
                                    numByte = self._send(data)
                                except socket.timeout:
                                    pass        
                                except (ConnectionResetError, OSError):
                                    with self.lockRead:
                                        self.logger.log('other side disconnected during writing.', TcpLogLevel.INFO)
                                        if self.role == TcpRole.SERVER:
                                            self.client.close()
                                            self.client = None
                                        else:
                                            self.sock.close()
                                            self.sock = None
        
    def _serviceRead(self):
        while True:
            if self.threadFinish:
                break
            else:
                with self.lockRead:
                    if self.isOpened():
                        if self.role == TcpRole.SERVER and not self.hasConnection():                
                            try:
                                self.client, adr = self.sock.accept()
                            except socket.timeout:
                                pass
                            else:
                                self.logger.log('accepted connection from {}.'.format(adr), TcpLogLevel.INFO)
                                self.client.settimeout(self.TIMEOUT_LIMIT)                            
                        else:
                            try:
                                data = self._recv(self.PACKET_SIZE)
                            except socket.timeout:
                                pass
                            except (ConnectionResetError, OSError):
                                with self.lockWrite:
                                    self.logger.log('other side disconnected during reading.', TcpLogLevel.INFO)
                                    if self.role == TcpRole.SERVER:
                                        self.client.close()
                                        self.client = None
                                    else:
                                        self.sock.close()
                                        self.sock = None
                            else:
                                if data:
                                    self.bufRead.put_nowait(data)                                
                                else:
                                    with self.lockWrite:
                                        self.logger.log('other side closed connection.', TcpLogLevel.INFO)
                                        if self.role == TcpRole.SERVER:
                                            self.client.close()
                                            self.client = None                                                                                                                  
                                        else:
                                            self.sock.close()
                                            self.sock = None
            
    def _raiseError(self, err: Exception):
        self.logger.log(str(err), TcpLogLevel.ERROR)
        raise err
        
    def __del__(self):
        self.close()

class TcpServer(TcpAbc):
    
    def __init__(self):
        super().__init__(TcpRole.SERVER)
        self.echo = False
        self.client = None
        
    def open(self):
        super().open()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1) # max connection limit to one
        
        self.threadWrite.start()
        self.threadRead.start()
        
    def hasConnection(self):
        return self.client is not None  
    
    def _send(self, data: bytearray) -> int:
        if self.hasConnection():
            return self.client.send(data)
        else:
            return len(data)
    
    def _recv(self, size: int) -> bytearray:
        return self.client.recv(size)
        
class TcpClient(TcpAbc):
    
    def __init__(self):
        super().__init__(TcpRole.CLIENT)        
        
    def open(self):        
        super().open()
        self.sock.connect_ex((self.ip, self.port))
        
        self.threadWrite.start()
        self.threadRead.start()
        
    def _send(self, data: bytearray) -> int:
        return self.sock.send(data)
    
    def _recv(self, size: int) -> bytearray:
        return self.sock.recv(size)
        
class TcpLogLevel(enum.IntEnum):    
    
    ERROR = 3
    INFO = 2
    DEBUG = 1
    NOTSET = 0
    
class TcpLogger():
    
    LOGGING_ENABLE = True
    MINIMUM_LOG_LEVEL = TcpLogLevel.DEBUG
    
    def __init__(self, caller):
        self.caller = weakref.proxy(caller)
        
    def log(self, mes: str, level: TcpLogLevel = TcpLogLevel.NOTSET):
        if self.LOGGING_ENABLE and level >= self.MINIMUM_LOG_LEVEL:
            name = self.caller.role.name.capitalize() + str((self.caller.ip, self.caller.port))
            mesType = level.name.lower()
            print(name + ': ' + mesType + ': ' +  mes + '\n', end = '')
        
if __name__ == '__main__':
    tcpServer = TcpServer()
    tcpClient = TcpClient()
    
    tcpServer.open()
    tcpClient.open()
    #time.sleep(1.0)
    #time.sleep(5.0)
    #tcpClient.close()
    #time.sleep(10.0)
    #tcpClient.open()    
    #bytearray([56]*1000)
    tcpServer.write(b'123456')
    res = tcpClient.read(1.0)
    print(res)
    #time.sleep(10)
    # tcpClient.close()
    # tcpClient.open()
    # tcpClient.write(b'789')
    # res = tcpServer.read(1.0)
    # print(res)
    tcpServer.close()
    tcpClient.close()