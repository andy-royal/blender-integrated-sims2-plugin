#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.parseutils import ParseName
from blendersims2.fileio.tgir import PackedFile, PackedFileType
from blendersims2.fileio.node import Node, cSGResource, cReferentNode, cObjectGraphNode, cRenderableNode, \
                                     cBoundedNode, cTransformNode
from blendersims2.fileio.rcol.common import RCOLDataBlock

class cStandardLightBase(Node):
    # Just a node
    pass

class cLightT(Node):
    # Just a node
    pass

class cDirectionalLight(Node):

    def extract(self, dg, verbose=False):
        # First get the common Node header
        super(cDirectionalLight, self).extract(dg, verbose)
        
        # A load of mostly pointless nodes
        self.standard_light_base = cStandardLightBase(dg)
        self.sgres1 = cSGResource(dg)
        self.light = cLightT(dg)
        self.sgres2 = cSGResource(dg)
        self.refer = cReferentNode(dg)
        self.objgraphnode = cObjectGraphNode(dg)
        
        # Name
        self.light_name = ParseName(dg)
        
        # Parameters
        data = dg.get_floats(5)
        self.far_attenuation = data[0]
        self.near_attenuation = data[1]
        self.red = data[2]
        self.green = data[3]
        self.blue = data[4]
        
    def dump(self, indent):
        super(cDirectionalLight, self).dump(indent)
        
        self.standard_light_base.dump(indent+1)
        self.sgres1.dump(indent+1)
        self.light.dump(indent+1)
        self.sgres2.dump(indent+1)
        self.refer.dump(indent+1)
        self.objgraphnode.dump(indent+1)

        indented_print(indent+1, "Name: %s" % self.light_name)
        indented_print(indent+1, "Parameters:")
        indented_print(indent+2, "Far   = %f" % self.far_attenuation)
        indented_print(indent+2, "Near  = %f" % self.near_attenuation)
        indented_print(indent+2, "red   = %f" % self.red)
        indented_print(indent+2, "green = %f" % self.green)
        indented_print(indent+2, "blue  = %f" % self.blue)

class LGHTData(RCOLDataBlock):

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common Node header
        super(LGHTData, self).extract(dg, verbose)
        
        # A load of mostly pointless nodes
        self.standard_light_base = cStandardLightBase(dg)
        self.sgres1 = cSGResource(dg)

        # Got name so terminate early if shallow
        if shallow:
            return

        self.light = cLightT(dg)
        self.sgres2 = cSGResource(dg)
        self.refer = cReferentNode(dg)
        self.objgraphnode = cObjectGraphNode(dg)
        
        # Name
        self.light_name = ParseName(dg)
        
        # Parameters
        data = dg.get_floats(5)
        self.far_attenuation = data[0]
        self.near_attenuation = data[1]
        self.red = data[2]
        self.green = data[3]
        self.blue = data[4]
        
    def get_name(self):
        return self.sgres1.filename
        
    def dump(self, indent):
        super(LGHTData, self).dump(indent)
        
        self.standard_light_base.dump(indent+1)
        self.sgres1.dump(indent+1)
        self.light.dump(indent+1)
        self.sgres2.dump(indent+1)
        self.refer.dump(indent+1)
        self.objgraphnode.dump(indent+1)

        indented_print(indent+1, "Name: %s" % self.light_name)
        indented_print(indent+1, "Parameters:")
        indented_print(indent+2, "Far   = %f" % self.far_attenuation)
        indented_print(indent+2, "Near  = %f" % self.near_attenuation)
        indented_print(indent+2, "red   = %f" % self.red)
        indented_print(indent+2, "green = %f" % self.green)
        indented_print(indent+2, "blue  = %f" % self.blue)

    @classmethod
    def register_RCOL(cls):
        PackedFileType.register_RCOL(PackedFile.LGHTA, cls)
        PackedFileType.register_RCOL(PackedFile.LGHTD, cls)
        PackedFileType.register_RCOL(PackedFile.LGHTP, cls)
        PackedFileType.register_RCOL(PackedFile.LGHTS, cls)

class cLightRefNode(RCOLDataBlock):

    typeEnum = PackedFile.cLight
    
    def extract(self, dg, shallow=False, verbose=False):
        # First get the common Node header
        super(cLightRefNode, self).extract(dg, verbose)
        
        # Some nodes
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
            
        self.light_file_link_index = dg.get_dword()
            
        # Unknown
        _ = dg.get_dword()
        _ = dg.get_bytes(5)
        
    def get_name(self):
        return self.transformnode.objgraphnode.resourcename

    def dump(self, indent):
        super(cLightRefNode, self).dump(indent)
        self.renderablenode.dump(indent+1)
        self.boundednode.dump(indent+1)
        self.transformnode.dump(indent+1)
        if len(self.use_types) > 0:
            indented_print(indent+1, "Use Types:")
            for index, use_type in enumerate(self.use_types):
                indented_print(indent+2, "%d => %s" % (index, use_type))
        else:
            indented_print(indent+1, "No use types")
        indented_print(indent+1, "Light File Link Index: %d" % self.light_file_link_index)

cLightRefNode.register_RCOL()
LGHTData.register_RCOL()
