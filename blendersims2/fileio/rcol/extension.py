#!/usr/bin/python3
#-*- coding: utf-8 -*-

from enum import IntEnum
from abc import abstractmethod

from blendersims2.fileio.parseutils import ParseName
from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.primitives import Sims2Reader, Translation, Quaternion
from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.node import Node
from blendersims2.fileio.rcol.common import RCOLDataBlock

class Extension(Sims2Reader):
    @ abstractmethod
    def extract(self, dg, verbose=False):
        self.name = ParseName(dg, verbose)
        
    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.name)
        
    def dump(self, indent=0):
        indented_print(str(self))

class DeltaExtension(Extension):
    def extract(self, dg, verbose=False):
        super(DeltaExtension, self).extract(dg, verbose)
        self.delta = dg.get_dword()
        
class FloatExtension(Extension):
    def extract(self, dg, verbose=False):
        super(FloatExtension, self).extract(dg, verbose)
        self.float = dg.get_float()
        
class TranslationExtension(Extension):
    def extract(self, dg, verbose=False):
        super(TranslationExtension, self).extract(dg, verbose)
        self.translation = Translation(dg)
        
class TagExtension(Extension):
    def extract(self, dg, verbose=False):
        super(TagExtension, self).extract(dg, verbose)
        self.tag = ParseName(dg, verbose)

class RecursiveExtension(Extension):
    
    def extract(self, dg, verbose=False):
        super(RecursiveExtension, self).extract(dg, verbose)

        self.extensionarray = []
        count = dg.get_dword()
        if verbose:
            print ("Recursive extension has count: %d" % count)
        for _ in range(count):
            self.extensionarray.append(CreateExtension(dg))
            
    def __str__(self):
        return "%s, count = %d" % (super(RecursiveExtension, self).__str__(), len(self.extensionarray))
        
    def dump(self, indent):
        indented_print(indent, str(self))
        for index, ext in enumerate(self.extensionarray):
            indented_print(indent+1, "%d => %s" % (index, str(ext)))

class RotationExtension(Extension):
    def extract(self, dg, verbose=False):
        super(RotationExtension, self).extract(dg, verbose)
        self.rotation = Quaternion(dg)
        
class DataExtension(Extension):
    def extract(self, dg, verbose=False):
        super(DataExtension, self).extract(dg, verbose)
        count = dg.get_dword()
        self.data = dg.read(count)
        if verbose:
            print("DataExtension type: %s" % type(self.data))
        
class ExtensionType(IntEnum):
    Delta       = 0x02
    Float       = 0x03
    Translation = 0x05
    Tag         = 0x06
    Recursive   = 0x07
    Rotation    = 0x08
    Data        = 0x09
    
    def __str__(self):
        return self.name + "Extension"

ExtensionConstructorDict = {
    ExtensionType.Delta       : DeltaExtension,
    ExtensionType.Float       : FloatExtension,
    ExtensionType.Translation : TranslationExtension,
    ExtensionType.Tag         : TagExtension,
    ExtensionType.Recursive   : RecursiveExtension,
    ExtensionType.Rotation    : RotationExtension,
    ExtensionType.Data        : DataExtension
}

def CreateExtension(dg, verbose=False):
    ext_type = ExtensionType(dg.get_byte())
    if verbose:
        print ("Extension type: %s" % ext_type)
    return ExtensionConstructorDict[ext_type](dg, verbose)

class cDataListExtension(Node):
    # Just a Node
    pass

class cDLEData(RCOLDataBlock):

    typeEnum = PackedFile.cDLE

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(cDLEData, self).extract(dg)
        
        # Then a cDataListExtension node and the extensions
        if verbose:
            print("Starting cDLE parsing")
        self.dle = cDataListExtension(dg)
        self.extension = CreateExtension(dg)
        
    def get_name(self):
        return self.extension.name

    def dump(self, indent):
        super(cDLEData, self).dump(indent)
        self.dle.dump(indent+1)
        self.extension.dump(indent+1)

#class cTagExtension(RCOLDataBlock, TagExtension):
class cTagExtension(RCOLDataBlock):

    typeEnum = PackedFile.cTag

    def extract(self, dg, shallow=False, verbose=False):
        super(cTagExtension, self).extract(dg, shallow, verbose)

        self.node = Node(dg, verbose)
        self.tag = ParseName(dg, verbose)

    def get_name(self):
        return self.tag
    
cDLEData.register_RCOL()
cTagExtension.register_RCOL()