#!/usr/bin/python3
#-*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from blendersims2.fileio.parseutils import ParseBool, ParseName
from blendersims2.fileio.dumputils import indented_print

class Sims2Reader(metaclass=ABCMeta):
    """A mixin class which can be directly read in whole or part from a DBPF data file"""
    
    # Constructor can do extraction if a filehandle is specified
    def __init__(self, fh=None, verbose=False):
        if fh:
            # If not verbose, don't set it false so default is used
            if verbose:
                self.extract(fh, verbose=True)
            else:
                self.extract(fh)

    @abstractmethod
    def extract(self, fh, verbose=False):
        pass

class NamePair(Sims2Reader):

    def extract(self, dg, verbose=False):
        self.name1 = ParseName(dg)
        self.name2 = ParseName(dg)

class Chain(Sims2Reader):
    def extract(self, dg, verbose=False):
        self.enabled = ParseBool(dg)
        self.subnode = ParseBool(dg)
        self.node = dg.get_dword()
        
    def __str__(self):
        res = str()
        if self.enabled:
            res += "Enabled, "
        if self.subnode:
            res += "Subnode, "
        res += "Node = %d" % self.node
        return res
        
class Translation(Sims2Reader):
    def extract(self, dg, verbose=False):
        self.x = dg.get_float()
        self.y = dg.get_float()
        self.z = dg.get_float()
        
    def __str__(self):
        return "x = %f, y = %f, z = %f" % (self.x, self.y, self.z)
    
    def dump(self, indent):
        indented_print(indent, "Translation: %s" % str(self))

class Quaternion(Sims2Reader):
    def extract(self, dg, verbose=False):
        self.x = dg.get_float()
        self.y = dg.get_float()
        self.z = dg.get_float()
        self.w = dg.get_float()

    def __str__(self):
        return "x = %f, y = %f, z = %f, w = %f" % (self.x, self.y, self.z, self.w)

    def dump(self, indent):
        indented_print(indent, "Quaternion: %s" % str(self))
