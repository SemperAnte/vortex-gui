# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Tue Sep 22 15:15:57 2020

Project: Vortex Upper Layer

Author: DIVE-LINK (www.dive-link.net), dive-link@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    [x] rename to commandProcessor
DESCRIPTION:
    Find commands with fixed or variable length in continious byte stream
"""

class CommandProcessor():
    
    COMMAND_VARIABLE_PREFIX = [b'VX!DATA', b'VX!STAT', b'VX!IMBL']
    
    def __init__(self):
        self.packetBuffer = b''
        self.commandSize = 0 # size for variable-size command
    
    def process(self, packet: bytearray) -> list:
        ''' Find and separate commands from byte stream'''

        self.packetBuffer += packet        
        commandFound = []        
        commandNext = True
        while commandNext:
            commandNext = False
            if self.commandSize > 0: # variable length
                if len(self.packetBuffer) >= self.commandSize:                      
                    commandFound.append(self.packetBuffer[:self.commandSize])
                    self.packetBuffer = self.packetBuffer[self.commandSize:]
                    self.commandSize = 0
                    commandNext = True    
            else:
                for prefix in self.COMMAND_VARIABLE_PREFIX:                
                    if self.packetBuffer.startswith(prefix):
                        if self.packetBuffer.count(b' ') > 1:
                            startIdx = self.packetBuffer.index(b' ') + 1
                            endIdx = startIdx + self.packetBuffer[startIdx:].index(b' ')
                            self.commandSize = self.packetBuffer[startIdx:endIdx]
                            try:
                                self.commandSize = int(self.commandSize)
                            except ValueError:                        
                                self.commandSize = 0
                                self.packetBuffer = self.packetBuffer[endIdx + 1:]
                            else:
                                self.commandSize += endIdx + 1 + 1 # for b'\n'             '                    
                            commandNext = True   
                            break
                else: # fixed length
                    endIdx = self.packetBuffer.find(b'\n')
                    if endIdx != -1:
                        commandFound.append(self.packetBuffer[:endIdx + 1])
                        self.packetBuffer = self.packetBuffer[endIdx + 1:]
                        commandNext = True
        return commandFound            
    
# test
if __name__ == '__main__':
    
    import random
    
    commandProcessor = CommandProcessor()

    COMMAND_FIXED = [b'VX!RATE 1/2\n',
                     b'VX!POWERLEVEL 83\n', 
                     b'VX!BLOCKSIZE 34\n']

    COMMAND_TOTAL_COUNT = 1000
    COMMAND_VARIABLE_MAX_LENGTH = 1000
    PACKET_MAX_SIZE = 500 # in bytes

    commandSource = []
    for i in range(COMMAND_TOTAL_COUNT):
        choice = random.randrange(len(COMMAND_FIXED) + len(CommandProcessor.COMMAND_VARIABLE_PREFIX))
        if choice < len(COMMAND_FIXED):        
            commandSource.append(COMMAND_FIXED[choice])
        else: # variable length
            variableLength = random.randint(1, COMMAND_VARIABLE_MAX_LENGTH)
            variableByte = bytearray([random.randint(0, 255) for x in range(variableLength)])            
            commandVariable = random.choice(CommandProcessor.COMMAND_VARIABLE_PREFIX)
            commandVariable += ' {} '.format(variableLength).encode() + variableByte + b'\n'
            commandSource.append(commandVariable)
        
    commandStream = b''.join(commandSource)
    
    # split continious stream to packets with random length
    commandPacket = []
    packetStart = 0
    packetEnd = 0
    while packetStart < len(commandStream):
        packetLng = random.randint(1, PACKET_MAX_SIZE)
        packetEnd = packetStart + packetLng
        commandPacket.append(commandStream[packetStart:packetEnd])
        packetStart = packetEnd
    assert sum([len(x) for x in commandPacket]) == sum([len(x) for x in commandSource])
  
    commandFound = []
    for singlePacket in commandPacket:
        commandFound.extend(commandProcessor.process(singlePacket))
    
    assert commandSource == commandFound