#!/usr/bin/python3
#-*- coding: utf-8 -*-

import struct

from blendersims2.fileio.crcutils import sims2crc32
from blendersims2.fileio.parseutils import ParseName, ParseBool
from blendersims2.fileio.dumputils import indented_print, DumpName
from blendersims2.fileio.primitives import Sims2Reader, Chain
from blendersims2.fileio.tgir import PackedFile, DecodeDescriptor
from blendersims2.fileio.rcol.common import RCOLDataBlock
from blendersims2.fileio.node import cSGResource, cReferentNode, cObjectGraphNode, cRenderableNode, cBoundedNode, cTransformNode

class LOD(Sims2Reader):
    
    def __init__(self, dg=None, version=8, verbose=False):
        if dg:
            self.extract(dg, version, verbose)
    
    def extract(self, dg, version=8, verbose=False):
        self.version = version
        self.lodtype = dg.get_dword()
        if self.version == 6 or self.version == 7:
            self.chain = Chain(dg)
        else:    # Version 8?
            self.enabled = ParseBool(dg)
            self.name = ParseName(dg)
            self.target = None

    def resolve(self, packman, dbpf, verbose=False):
        if self.version != 6 and self.version != 7:
            targ_descriptor = dbpf.findname(PackedFile.GMND, self.name)
            if targ_descriptor:
                if verbose:
                    print("Found target descriptor: %s => %s" % (self.name, str(DecodeDescriptor(targ_descriptor))))
            else:
                if verbose:
                    print("Failed to find target descriptor for %s in local name map, checking global" % self.name)
                targ_descriptor = packman.findname(PackedFile.GMND, self.name)
                if targ_descriptor:
                    if verbose:
                        print("Found target descriptor: %s => %s" % (self.name, str(DecodeDescriptor(targ_descriptor))))
                else:
                    raise ValueError("Failed to find target descriptor for %s in name maps" % self.name)
            self.target = packman.getResource(targ_descriptor)
            if not self.target:
                resource = sims2crc32(self.name.lower().encode('ascii'))
                resource_bytes = struct.pack('I', resource)
                descriptor = b''.join((targ_descriptor, resource_bytes))
                self.target = packman.getResource(descriptor)
            self.target.ResolveAllLinks(packman, verbose)

    def __str__(self):
        res = "Type = %d, " % self.lodtype
        if self.version == 6 or self.version == 7:
            res += "Chain: %s" % str(self.chain)
        else:
            if self.enabled:
                res += "enabled, "
            res += "name = %s" % self.name
        return res
    
    def dump_target(self, indent=0):
        if self.version != 6 and self.version != 7:
            print()
            self.target.dump(indent)

class MaterialDef(Sims2Reader):
    
    def extract(self, dg, verbose=False):
        self.groupname = ParseName(dg)
        self.matdefname = ParseName(dg)
        
        # Unknowns
        if verbose:
            print("Checking unknowns")
        tmp = dg.get_dword()
        if tmp != 0:
            raise ValueError("Expected unknown parameter value 0, got %d" % tmp)
        tmp = dg.get_byte()
        if tmp != 0:
            raise ValueError("Expected unknown parameter value 0, got %d" % tmp)
        tmp = dg.get_dword()
        if tmp != 0:
            raise ValueError("Expected unknown parameter value 0, got %d" % tmp)

    def __str__(self):
        return "Group Name: %s, Material Definition Name: %s" % (DumpName(self.groupname), DumpName(self.matdefname))

class SHPEData(RCOLDataBlock):

    typeEnum = PackedFile.SHPE

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(SHPEData, self).extract(dg)
        
        # Some nodes
        self.sgres = cSGResource(dg)

        # Got name so terminate early if shallow
        if shallow:
            return

        self.refer = cReferentNode(dg)
        self.objgraphnode = cObjectGraphNode(dg)
        
        # LOD values, if version is at least 6
        if self.version > 6:
            count = dg.get_dword()
            if verbose:
                print("LOD value count = %d" % count)
            #if count > 0:
            self.lod_values = dg.get_dwords(count)
            
        # Now get LOD blocks
        count = dg.get_dword()
        if verbose:
            print("LOD count = %d" % count)
        self.lods = []
        for _ in range(count):
            self.lods.append(LOD(dg, self.version))
                
        # Material definitions
        self.matdefs = []
        count = dg.get_dword()
        if verbose:
            print("Matdef count = %d" % count)
        for _ in range(count):
            self.matdefs.append(MaterialDef(dg))
            
    def get_name(self):
        return self.sgres.filename

    def resolve(self, packman, dbpf, verbose=False):
        if verbose:
            print ("Resolving LODs for SHPE: %s" % DumpName(self.sgres.filename))
        for lod in self.lods:
            lod.resolve(packman, dbpf, verbose)

    def dump(self, indent=0):
        super(SHPEData, self).dump(indent)
        self.sgres.dump(indent+1)
        self.refer.dump(indent+1)
        self.objgraphnode.dump(indent+1)
        
        if self.version > 6:
            if len(self.lod_values) > 0:
                indented_print(indent+1, "LOD values:")
                for index, value in enumerate(self.lod_values):
                    indented_print(indent+2, "%d => %d" % (index, value))
            else:
                indented_print(indent+1, "No LOD values")
        
        if self.lods:
            indented_print(indent+1, "LODs:")
            for index, lod in enumerate(self.lods):
                indented_print(indent+2, "%d => %s" % (index, str(lod)))
        else:
            indented_print(indent+1, "No LODs")
        
        if self.matdefs:
            indented_print(indent+1, "Material definitions:")
            for index, matdef in enumerate(self.matdefs):
                indented_print(indent+2, "%d => %s" % (index, str(matdef)))
                
        if self.lods:
            for lod in self.lods:
                lod.dump_target(indent)

class cShapeRefNode(RCOLDataBlock):

    typeEnum = PackedFile.cShape

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(cShapeRefNode, self).extract(dg)
        
        # Then a bunch of nodes
        self.renderablenode = cRenderableNode(dg)
        self.boundednode = cBoundedNode(dg)
        self.transformnode = cTransformNode(dg)
        
        # Unknowns
        if verbose:
            print("Checking unknowns 1")
        tmp = dg.get_word()
        if tmp != 1:
            raise ValueError("Expected unknown parameter value 1, got %d" % tmp)
        tmp = dg.get_dword()
        if tmp != 1:
            raise ValueError("Expected unknown parameter value 1, got %d" % tmp)
        
        # Kind
        self.kind = ParseName(dg, verbose)

        # Got name so terminate early if shallow
        if shallow:
            return

        # More unknowns
        if verbose:
            print("Checking unknowns 2")
        tmp = dg.get_dword()
        if tmp != 0:
            raise ValueError("Expected unknown parameter value 0, got %d" % tmp)
        tmp = dg.get_byte()
        if tmp != 1:
            raise ValueError("Expected unknown parameter value 1, got %d" % tmp)
        
        # Shape links
        if verbose:
            print("Extracting Shape Links")
        count = dg.get_dword()
        if verbose:
            print("Shape link count = %d" % count)
        self.shapelinks = []
        for _ in range (count):
            self.shapelinks.append(Chain(dg))
            
        # More unknowns
        if verbose:
            print("Checking unknowns 3")
        tmp = dg.get_dword()
        if tmp != 0 and tmp != 16:
            raise ValueError("Expected unknown parameter value 0 or 16, got %d" % tmp)
            
        # Blends?
        if verbose:
            print("Extracting blend info")
        self.blendnames = {}
        count = dg.get_dword()
        if verbose:
            print("Blend count = %d" % count)
        blendvalues = list(dg.get_dwords(count))
        if self.version == 21:
            for index in range (count):
                self.blendnames[blendvalues[index]] = ParseName(dg, verbose)
        else:
            self.blendvalues = blendvalues
        
        # Unknown section
        if verbose:
            print("Extracting unknown section")
        count = dg.get_dword()
        if verbose:
            print("Unknown count = %d" % count)
        for index in range (count):
            tmp = dg.get_byte()
            if tmp != 0:
                raise ValueError("Expected unknown parameter value 0 at position %d, got %d" % (index, tmp))
        
        # A final unknown DWORD
        tmp = dg.get_dword()
        if tmp != 0xffffffff:
            raise ValueError("Expected unknown parameter value 0xffffffff, got %s" % hex(tmp))
        
    def get_name(self):
        return self.kind + " - " + self.transformnode.objgraphnode.resourcename

    def dump(self, indent):
        super(cShapeRefNode, self).dump(indent)
        self.renderablenode.dump(indent+1)
        self.boundednode.dump(indent+1)
        self.transformnode.dump(indent+1)
        indented_print(indent+1, "Kind = %s" % self.kind)
        if len(self.shapelinks) > 0:
            indented_print(indent+1, "Shape Links:")
            for index, link in enumerate(self.shapelinks):
                indented_print(indent+2, "%d => %s" % (index, str(link)))
        else:
            indented_print(indent+1, "No shape links")
        if self.version == 21:
            if len(self.blendnames) > 0:
                indented_print(indent+1, "Blend Names:")
                for index, blendname in self.blendnames.items():
                    indented_print(indent+2, "%d => %s" % (index, blendname))
            else:
                indented_print(indent+1, "No blend names")
        else:
            if len(self.blendvalues) > 0:
                indented_print(indent+1, "Blend Values:")
                for index, blendvalue in enumerate(self.blendvalues):
                    indented_print(indent+2, "%d => %d" % (index, blendvalue))
            else:
                indented_print(indent+1, "No blend values")

cShapeRefNode.register_RCOL()
SHPEData.register_RCOL()
