# -*- coding: utf-8 -*-
"""
HISTORY:
	Created on Mon May 25 07:12:24 2020

Project: Vortex GUI

Author: DIVE-LINK (www.dive-link.net), divelink@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:

DESCRIPTION:
"""
class interface():
    
    def __init__(self):
        self.status = False
    
    def connect(self):
        self.status = True
    
    def sendCommand(self, cmd):
        assert self.status, 'No connection.'
    
    def reset(self):
        cmd = 'VX!RESET'
        self.sendCommand(cmd)
        return True
    
    def readVersion(self):
        cmd = 'VX?VER'
        self.sendCommand(cmd)
        return '0.1'