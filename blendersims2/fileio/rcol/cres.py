#!/usr/bin/python3
#-*- coding: utf-8 -*-

import struct

from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.parseutils import ParseBool
from blendersims2.fileio.primitives import Chain
from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.node import cSGResource, cObjectGraphNode, cCompositionTreeNode
from blendersims2.fileio.rcol.common import RCOLDataBlock

class CRESData(RCOLDataBlock):
    """cResourceNode, the bones of the scenegraph tree"""
    typeEnum = PackedFile.CRES

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(CRESData, self).extract(dg)
        
        # Now the Typecode, which radically changes the structure
        self.typecode = dg.get_byte()
        if verbose:
            print("Typecode: %d" % self.typecode)
        if self.typecode == 1:
            # A couple of Nodes
            self.sgres = cSGResource(dg)

            # Got name so terminate early if shallow
            if shallow:
                return

            self.comptreenode = cCompositionTreeNode(dg)
            self.objgraphnode = cObjectGraphNode(dg)
            
            # A section of Chains
            self.chains = []
            count = dg.get_dword()
            for _ in range (0, count):
                self.chains.append(Chain(dg))
            
            # Subnode flag and purpose
            self.subnode = ParseBool(dg)
            self.purpose = struct.unpack('I', dg.read(4))[0]
        elif self.typecode == 0:
            self.objgraphnode = cObjectGraphNode(dg)
            self.chains.append(Chain(dg))
            self.objectcount = struct.unpack('I', dg.read(4))[0]
        else:
            raise ValueError("Invalid typecode: %s" % format(self.typecode, '#010x'))
        
        if verbose:
            print("CRES name: %s" % self.get_name)
        
    def get_name(self):
        if self.typecode == 1:
            return self.sgres.filename
        else:
            raise NotImplementedError("I don't know where to get the name for this!")

    def dump(self, indent):
        super(CRESData, self).dump(indent)
        if self.typecode == 1:
            self.sgres.dump(indent+1)
            self.comptreenode.dump(indent+1)
            self.objgraphnode.dump(indent+1)
            if len(self.chains) > 0:
                indented_print(indent+1, "Chains:")
                for index, chain in enumerate(self.chains):
                    indented_print(indent+2, "%d => %s" % (index, str(chain)))
            else:
                indented_print(indent+1, "No chains")
            if self.subnode:
                indented_print(indent+1, "Subnode")
            indented_print(indent+1, "Purpose = %d" % self.purpose)
            
CRESData.register()