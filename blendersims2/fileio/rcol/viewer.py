#!/usr/bin/python3
#-*- coding: utf-8 -*-


from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.parseutils import ParseName
from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.node import Node, cRenderableNode, cBoundedNode, cTransformNode
from blendersims2.fileio.rcol.common import RCOLDataBlock

class cViewerRefNodeBase(Node):
    # Just a node
    pass

class cViewerRefNode(RCOLDataBlock):

    typeEnum = PackedFile.cViewer

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(cViewerRefNode, self).extract(dg)
        
        # Some nodes
        self.base = cViewerRefNodeBase(dg)
        self.renderablenode = cRenderableNode(dg)
        self.boundednode = cBoundedNode(dg)
        self.transformnode = cTransformNode(dg)

        # Got name so terminate early if shallow
        if shallow:
            return

        # Unknown
        _ = dg.get_word()

        # Use types
        count = dg.get_dword()
        self.use_types = []
        for _ in range(count):
            self.use_types.append(ParseName(dg, verbose))

        # Unknown
        _ = dg.get_dwords(40)
        
    def get_name(self):
        return self.transformnode.objgraphnode.resourcename
        
    def dump(self, indent=0):
        super(cViewerRefNode, self).dump(indent)
        self.base.dump(indent+1)
        self.renderablenode.dump(indent+1)
        self.boundednode.dump(indent+1)
        self.transformnode.dump(indent+1)
        if len(self.use_types) > 0:
            indented_print(indent+1, "Use Types:")
            for index, use_type in enumerate(self.use_types):
                indented_print(indent+2, "%d => %s" % (index, use_type))
        else:
            indented_print(indent+1, "No use types")

class cViewerRefNodeRecursive(RCOLDataBlock):

    typeEnum = PackedFile.cViewRec

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common Node header
        super(cViewerRefNodeRecursive, self).extract(dg, verbose)
        
        # Som nodes
        self.base = cViewerRefNodeBase(dg)
        self.renderablenode = cRenderableNode(dg)
        self.boundednode = cBoundedNode(dg)
        self.transformnode = cTransformNode(dg)

        # Got name so terminate early if shallow
        if shallow:
            return

        # Unknown
        _ = dg.get_word()

        # Use types
        count = dg.get_dword()
        self.use_types = []
        for _ in range(count):
            self.use_types.append(ParseName(dg, verbose))

        # Unknown
        _ = dg.get_dword()    # 0
        _ = dg.get_word()     # 257
        
        self.name = ParseName(dg, verbose)
        
        _ = dg.get_dwords(16)
        
    def get_name(self):
        return self.transformnode.objgraphnode.resourcename
        
    def dump(self, indent=0):
        super(cViewerRefNodeRecursive, self).dump(indent)
        self.base.dump(indent+1)
        self.renderablenode.dump(indent+1)
        self.boundednode.dump(indent+1)
        self.transformnode.dump(indent+1)
        if len(self.use_types) > 0:
            indented_print(indent+1, "Use Types:")
            for index, use_type in enumerate(self.use_types):
                indented_print(indent+2, "%d => %s" % (index, use_type))
        else:
            indented_print(indent+1, "No use types")

cViewerRefNodeRecursive.register_RCOL()
cViewerRefNode.register_RCOL()