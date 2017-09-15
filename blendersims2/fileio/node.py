#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.dumputils import indented_print, DumpName
from blendersims2.fileio.primitives import Sims2Reader, Chain, Translation, Quaternion
from blendersims2.fileio.parseutils import ParseName
from blendersims2.fileio.tgir import PackedFile, PackedFileType

class Node(Sims2Reader):
    """Generic node type which provides the basis of many structures in RCOLs."""
    
    def extract(self, dg, verbose=False):
        if verbose:
            print ("Offset of start of block: %d (%s)" % (dg.tell(), hex(dg.tell())))  

        # First get name of node
        self.node_name = ParseName(dg, verbose)
        if verbose:
            print("Name of Node: %s" % self.node_name)
            
        # Now ID and version
        data = dg.get_dwords(2)
        #self.type = data[0]
        self.type = self.get_nodetype(data[0])
        self.version = data[1]
        
        super(Node, self).extract(dg, verbose)
    
    @staticmethod
    def get_nodetype(data):
        return data

    @staticmethod
    def nodetype2string(data):
        return hex(data)
    
    # May have nothing to resolve
    def resolve(self, packman, dbpf, verbose=False):
        pass
    
    def dump(self, indent=0):
        indented_print(indent, "%s: %s, type = %s, version = %d" % (self.__class__.__name__, self.node_name, self.nodetype2string(self.type), self.version))
                     
class cSGResource(Node):
    def extract(self, dg):
        super(cSGResource, self).extract(dg)
        self.filename = ParseName(dg)

    def dump(self, indent):
        super(cSGResource, self).dump(indent)
        indented_print(indent+1, self.filename) 
        
class cCompositionTreeNode(Node):
    # Identical to Node!
    pass

class cObjectGraphNode(Node):
    
    def extract(self, dg, verbose=False):
        # Read the common Node stuff first
        super(cObjectGraphNode, self).extract(dg, verbose)
        
        # Now a section of Chains which are called "extensions"
        self.extensions = []
        count = dg.get_dword()
        if verbose:
            print ("Extension count: %d" % count)
        for _ in range (0, count):
            self.extensions.append(Chain(dg, verbose))
            
        # Optional resource name
        if self.version == 4:
            self.resourcename = ParseName(dg)
            if verbose:
                print ("Resource name: %s" % DumpName(self.resourcename))

    def dump(self, indent):
        super(cObjectGraphNode, self).dump(indent)
        if len(self.extensions) > 0:
            indented_print(indent+1, "Extensions:")
            for index, ext in enumerate(self.extensions):
                indented_print(indent+2, "%d => %s" % (index, str(ext)))
        else:
            indented_print(indent+1, "No extensions")
            
        if self.version == 4:
            indented_print(indent+1, "Resource name: %s" % DumpName(self.resourcename))

class cRenderableNode(Node):
    # Just a Node
    pass

class cBoundedNode(Node):
    # Just a Node
    pass

class cTransformNode(Node):

    typeEnum = PackedFile.cTran

    def extract(self, dg, verbose=False):
        # First get the common Node header
        super(cTransformNode, self).extract(dg, verbose)
        
        # Some nodes
        self.comptreenode = cCompositionTreeNode(dg, verbose)
        self.objgraphnode = cObjectGraphNode(dg, verbose)
    
        # Some chains
        self.chains = []
        count = dg.get_dword()
        for _ in range (0, count):
            self.chains.append(Chain(dg))
            
        # Then the transforms
        self.translation = Translation(dg)
        self.rotation = Quaternion(dg)
        
        # Finally the "subset"/GMDC joint index
        self.subset = dg.get_dword()
        
    @classmethod
    def register_RCOL(cls):
        PackedFileType.register_RCOL(cls.typeEnum, cls)
    
    def dump(self, indent):
        super(cTransformNode, self).dump(indent)
        self.comptreenode.dump(indent+1)
        self.objgraphnode.dump(indent+1)
        if len(self.chains) > 0:
            indented_print(indent+1, "Chains:")
            for index, chain in enumerate(self.chains):
                indented_print(indent+2, "%d => %s" % (index, str(chain)))
        else:
            indented_print(indent+1, "No chains")
        self.translation.dump(indent+1)
        indented_print(indent+1, "Rotation: %s" % str(self.rotation))
        indented_print(indent+1, "Subset = %s" % hex(self.subset))

class cReferentNode(Node):
    # Just another Node
    pass

class cExtension(Node):
    # Just a node
    pass

class cBoneDataExtension(Node):

    typeEnum = PackedFile.cBone
    
    def extract(self, dg, verbose=False):
        # First get the common RCOLDataBlock header
        super(cBoneDataExtension, self).extract(dg)
        
        # Nodes
        self.ext = cExtension(dg, verbose=False)

        # Unknowns
        _ = dg.get_dwords(4)

        if self.version >= 4:
            self.rotation = Quaternion(dg)
            
    @classmethod
    def register_RCOL(cls):
        PackedFileType.register_RCOL(cls.typeEnum, cls)
    
    def dump(self, indent=0):
        super(cBoneDataExtension, self).dump(indent)
        self.ext.dump(indent+1)
        self.rotation.dump(indent+1)