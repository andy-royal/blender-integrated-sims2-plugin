#!/usr/bin/python3
#-*- coding: utf-8 -*-

class RCOLParsingError(Exception):
    def __init__(self, value):
        super(RCOLParsingError, self).__init__(value)
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class RCOLNotSupported(NotImplementedError):
    def __init__(self, value):
        super(RCOLNotSupported, self).__init__(value)
        self.value = value
        
    def __str__(self):
        return repr(self.value)

