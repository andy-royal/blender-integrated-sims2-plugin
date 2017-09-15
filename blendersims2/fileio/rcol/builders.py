#!/usr/bin/python3
#-*- coding: utf-8 -*-

import struct

from blendersims2.fileio.parseutils import ParseName, ParseBool
from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.node import Node
from blendersims2.fileio.rcol.common import RCOLDataBlock

class cGeometryBuilder(Node):
    # Just a node
    pass

class cIndexedMeshBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cIMB

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        #if shallow:
        #    return

        if verbose:
            print("Start offset of cIndexedMeshBuilder: %s" % hex(dg.tell()))

        # First get the common RCOLDataBlock header
        super(cIndexedMeshBuilder, self).extract(dg)
        
        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)
        
        # Unknown
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(3)
            
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(3)
            
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(2)
        
        if verbose:
            print("Start offset of cIndexedMeshBuilder zeroes: %s" % hex(dg.tell()))
            
        # 20 zeroes
        for _ in range(5):
            _ = dg.get_dword()
            
        count = dg.get_dword()
        
        _ = dg.get_dword()    # 0x41
        
        # 20 zeroes
        for _ in range(5):
            _ = dg.get_dword()
            
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(2)
        
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(2)
        
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dwords(2)
        
        _ = dg.get_dwords(512)
        
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = ParseName(dg, verbose)
            _ = ParseName(dg, verbose)
            inner = dg.get_dword()
            for _ in range(inner):
                _ = dg.get_dwords(4)
            _ = dg.get_dword()
        
        _ = dg.get_dword()    # 1
        _ = dg.get_dword()    # 3
        
        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dword()

        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dword()

        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dword()

        count = dg.get_dword()
        if verbose:
            print("Unknown count: %d" % count) 
        for _ in range(count):
            _ = dg.get_dword()
            
        _ = dg.get_dword()    # 1
        _ = dg.get_dword()    # 0
        _ = dg.get_dword()    # 0
        _ = dg.get_dword()    # 0
        _ = dg.get_dword()    # Count
        _ = dg.get_dword()    # 1
        
        self.name = ParseName(dg, verbose)

    def get_name(self):
        return self.name
    
class cTSFaceGeometryBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cTSFace

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        if shallow:
            return

        if verbose:
            print("Start offset of cTSFaceGeometryBuilder: %s" % hex(dg.tell()))

        super(cTSFaceGeometryBuilder, self).extract(dg, verbose)

        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)

        _ = dg.get_dword()    # 2
        _ = dg.get_byte()
        _ = dg.get_dword()    # 0x103
        
        for _ in range(10):
            _ = dg.get_word()
            
            count = dg.get_dword()
            if verbose:
                print("Element count: %d" % count) 
            #for _ in range(count):
            #    _ = dg.get_dword()
            count = dg.get_dword()
            if verbose:
                print("Vertex count: %d" % count) 
            for _ in range(count):
                _ = dg.get_dwords(3)
            count = dg.get_dword()
            if verbose:
                print("Normal count: %d" % count) 
            for _ in range(count):
                _ = dg.get_dwords(3)
                
    def get_name(self):
        return "{None}"

class cCompactorBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cComp

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        if shallow:
            return

        if verbose:
            print("Start offset of cCompactorBuilder: %s" % hex(dg.tell()))

        super(cCompactorBuilder, self).extract(dg, verbose)

        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)

    def get_name(self):
        return "{None}"

class cBoundingVolumeBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cBound

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        if shallow:
            return

        if verbose:
            print("Start offset of cBoundingVolumeBuilder: %s" % hex(dg.tell()))

        super(cBoundingVolumeBuilder, self).extract(dg, verbose)

        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)
        
        if self.version == 2:
            self.enabled = ParseBool(dg)
            self.index = dg.get_dword()

    def get_name(self):
        return "{None}"

class cProcessDeformationsBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cProc

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        if shallow:
            return

        if verbose:
            print("Start offset of cProcessDeformationsBuilder: %s" % hex(dg.tell()))

        super(cProcessDeformationsBuilder, self).extract(dg, verbose)

        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)
        
        # GMDC reference
        data = dg.get_dwords(3)
        self.gmdc_ref = struct.pack('3I', data[2], data[0], data[1])
        
        self.enabled = ParseBool(dg)
        self.mesh = ParseBool(dg)
        self.index = dg.get_dword()

    def get_name(self):
        return "{None}"

class cTangentSpaceBuilder(RCOLDataBlock):

    typeEnum = PackedFile.cTang

    def extract(self, dg, shallow=False, verbose=False):
        
        # No name so terminate early if shallow
        if shallow:
            return

        super(cTangentSpaceBuilder, self).extract(dg, verbose)

        # Nodes
        self.geo = cGeometryBuilder(dg, verbose)
        
        # GMDC reference
        self.gmdc_index = dg.get_dword()

    def get_name(self):
        return "{None}"
    
cBoundingVolumeBuilder.register_RCOL()
cTSFaceGeometryBuilder.register_RCOL()
cProcessDeformationsBuilder.register_RCOL()
cTangentSpaceBuilder.register_RCOL()
cIndexedMeshBuilder.register_RCOL()
cCompactorBuilder.register_RCOL()