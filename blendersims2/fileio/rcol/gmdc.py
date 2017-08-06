#!/usr/bin/python3
#-*- coding: utf-8 -*-

from enum import IntEnum
from abc import abstractmethod

from blendersims2.fileio.parseutils import ParseName
from blendersims2.fileio.dumputils import DumpName, indented_print
from blendersims2.fileio.primitives import Sims2Reader, NamePair, Quaternion, Translation
from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.node import cSGResource
from blendersims2.fileio.rcol.common import RCOLDataBlock

class ElemIdent(IntEnum):
    
    BLEND_INDICES          = 0x1C4AFC56
    BLEND_WEIGHTS          = 0x5C4AFC5C
    TARGET_INDICES         = 0x7C4DEE82
    NORMAL_MORPH_DELTAS    = 0xCB6F3A6A
    COLOUR                 = 0xCB7206A1
    COLOUR_DELTAS          = 0xEB720693
    NORMALS_LIST           = 0x3B83078B
    VERTICES               = 0x5B830781
    UV_COORDINATES         = 0xBB8307AB
    UV_COORDINATE_DELTAS   = 0xDB830795
    BINORMALS              = 0x9BB38AFB
    BONE_WEIGHTS           = 0x3BD70105
    BONE_ASSIGNMENTS       = 0xFBD70111
    BUMP_MAP_NORMALS       = 0x89D92BA0
    BUMP_MAP_NORMAL_DELTAS = 0x69D92B93
    MORPH_VERTEX_DELTAS    = 0x5CF2CFE1
    MORPH_VERTEX_MAP       = 0xDCF2CFDC
    VERTEX_ID              = 0x114113C3
    REGION_MASK            = 0x114113CD

    def __str__(self):
        return elemident_fullnames[self.value]

elemident_fullnames = {
    ElemIdent.BLEND_INDICES          : "Blend Indices",
    ElemIdent.BLEND_WEIGHTS          : "Blend Weights",
    ElemIdent.TARGET_INDICES         : "Target Indices",
    ElemIdent.NORMAL_MORPH_DELTAS    : "Normal Morph Deltas",
    ElemIdent.COLOUR                 : "Colour",
    ElemIdent.COLOUR_DELTAS          : "Colour Deltas",
    ElemIdent.NORMALS_LIST           : "Normals List",
    ElemIdent.VERTICES               : "Vertices",
    ElemIdent.UV_COORDINATES         : "UV Coordinates",
    ElemIdent.UV_COORDINATE_DELTAS   : "UV Coordinate Deltas",
    ElemIdent.BINORMALS              : "Binormals",
    ElemIdent.BONE_WEIGHTS           : "Bone Weights",
    ElemIdent.BONE_ASSIGNMENTS       : "Bone Assignments",
    ElemIdent.BUMP_MAP_NORMALS       : "Bump Map Normals",
    ElemIdent.BUMP_MAP_NORMAL_DELTAS : "Bump Map Normal Deltas",
    ElemIdent.MORPH_VERTEX_DELTAS    : "Morph Vertex Deltas",
    ElemIdent.MORPH_VERTEX_MAP       : "Morph Vertex Map",
    ElemIdent.VERTEX_ID              : "Vertex ID",
    ElemIdent.REGION_MASK            : "Region Mask"   
}

class BlockFormat(IntEnum):
    OneFloat   = 0x0
    TwoFloat   = 0x1
    ThreeFloat = 0x2
    OneDWORD   = 0x4
    
    def __str__(self):
        return self.name
    
    def block_size(self):
        return block_format_sizes[self]

block_format_sizes = {
    BlockFormat.OneFloat   : 1,
    BlockFormat.TwoFloat   : 2,
    BlockFormat.ThreeFloat : 3,
    BlockFormat.OneDWORD   : 1
}

class SetGroup(IntEnum):
    Main      = 0x0
    Norms     = 0x1
    UV        = 0x2
    Secondary = 0x3
    
    def __str__(self):
        return self.name
    
class GMDCSection(Sims2Reader):
    
    def __init__(self, dg=None, gmdc_version=0, verbose=False):
        self.version = gmdc_version
        if dg:
            if verbose:
                self.extract(dg, True)
            else:
                self.extract(dg)

    @abstractmethod
    def extract(self, dg, verbose=False):
        pass
        
class Element(GMDCSection):
    
    def extract(self, dg, verbose=False):
        self.refarray_size = dg.get_dword()
        self.identity = ElemIdent(dg.get_dword())
        if verbose:
            print ("Identity: \"%s\"" % str(self.identity))
        self.repetition = dg.get_dword()
        self.block_format = BlockFormat(dg.get_dword())
        self.set_group = SetGroup(dg.get_dword())
        block_size = dg.get_dword()
        
        setlength = self.block_format.block_size()
        
        if block_size % (setlength * 4) != 0:
            raise ValueError("Block size (%d) is not an integer multiple of setlength*4 (%d)" % (block_size, setlength))
        listLength = block_size // (setlength * 4)
        
        self.block = []
        if self.block_format == 4:
            block_func = dg.get_dword
        else:
            block_func = dg.get_float
        for _ in range(listLength):
            for _ in range(setlength):
                self.block.append(block_func())

        item_count = dg.get_dword()
        self.items = []
        if self.version == 4:
            item_func = dg.get_word
        else:
            item_func = dg.get_dword
        for _ in range(item_count):
            self.items.append(item_func())
            
    def __str__(self):
        return "RefArraySize = %d, %s %d, %s, %s, block(%d), items(%d)" % (self.refarray_size, str(self.identity), self.repetition, self.block_format,
                                                                           str(self.set_group), len(self.block), len(self.items))

class Linkage(GMDCSection):
    
    def extract(self, dg, verbose=False):
        if self.version == 4:
            index_func = dg.get_word
        else:
            index_func = dg.get_dword
        index_types = ['elements', 'subset', 'normals', 'uv']
        self.indices = {}
        for it in index_types:
            self.indices[it] = []
            count = dg.get_dword()
            if verbose:
                print("%d indices of type %s" % (count, it))
            for _ in range(count):
                self.indices[it].append(index_func())
            if it == 'elements':
                self.referenced_array_size = dg.get_dword()
                self.active_elements = dg.get_dword()
                if verbose:
                    print("Ref size = %d, active = %d" % (self.referenced_array_size, self.active_elements))
                
    def __str__(self, indent=0):
        return "Ref size = %d, Active = %d, links: element(%d), subset(%d), normals(%d), uv(%d)" % (self.referenced_array_size, self.active_elements,
            len(self.indices['elements']), len(self.indices['subset']), len(self.indices['normals']), len(self.indices['uv']))

class Group(GMDCSection):
    
    def extract(self, dg, verbose=False):
        if verbose:
            print ("Offset of start of block: %d (%s)" % (dg.tell(), hex(dg.tell())))
        
        # Integer type based on GMDC version
        if self.version == 4:
            face_func = dg.get_words
            subset_func = dg.get_word
        else:
            face_func = dg.get_dwords
            subset_func = dg.get_dword
        
        # Basics
        self.primitive_type = dg.get_dword()
        self.link_index = dg.get_dword()
        self.name = ParseName(dg)
        if verbose:
            print ("Group name: %s" % DumpName(self.name))
        
        # Faces
        face_count = dg.get_dword()
        if verbose:
            print ("Face count = %d" % (face_count // 3))
        if (face_count % 3) != 0:
            raise ValueError("Face count (%d) is not a multiple of 3, current offset: %d (%s)" % (face_count, dg.tell(), hex(dg.tell())))
        self.faces = []
        for _ in range(face_count // 3):
            self.faces.append(face_func(3))    # N.B. As get_dwords returns a list, and we're using append rather than extend, this creates a list of lists
            
        # Opacity
        self.opacity = dg.get_dword()
        
        # Subsets
        if self.version == 2 or self.version == 4:    # i.e. not 1
            subset_count = dg.get_dword()
            if verbose:
                print ("Subset count = %d" % subset_count)
            self.subsets = []
            for _ in range(subset_count):
                self.subsets.append(subset_func())
        
    def __str__(self, indent=0):
        res = "%s: Prim type = %d, link index = %d, opacity = %s, faces = %d" % (self.name, self.primitive_type, self.link_index, hex(self.opacity), len(self.faces))
        if self.version == 2 or self.version == 4:
            res += ", subsets = %d" % len(self.subsets)
        return res

class Model(GMDCSection):

    def extract(self, dg, verbose=False):

        # Transforms
        transform_count = dg.get_dword()
        if verbose:
            print ("Transform count: %d" % transform_count)
        self.transforms = []
        for _ in range(transform_count):
            self.transforms.append((Quaternion(dg, verbose), Translation(dg, verbose)))    # 2-tuple
            
        # Pairs
        pair_count = dg.get_dword()
        if verbose:
            print ("Pair count: %d" % transform_count)
        self.pairs = []
        for _ in range(pair_count):
            self.pairs.append(NamePair(dg, verbose))
            
        # Subset
        self.subset = Subset(dg, self.version, verbose)

    def dump(self, indent=0):
        indented_print(indent, "Transforms(%d), Pairs(%d)" % (len(self.transforms), len(self.pairs)))
        indented_print(indent, "Subset: %s" % str(self.subset))
        
class Subset(GMDCSection):

    def extract(self, dg, verbose=False):
        vertex_count = dg.get_dword()
        if vertex_count > 0:
            face_count = dg.get_dword()
            self.vertices = []
            self.faces = []
            for _ in range(vertex_count):
                self.vertices.append(dg.get_dwords(3))    # N.B. As get_dwords returns a list, and we're using append rather than extend, this creates a list of lists
            # Integer type based on GMDC version
            if self.version == 4:
                face_func = dg.get_words
            else:
                face_func = dg.get_dwords
            for _ in range(face_count // 3):
                self.faces.append(face_func(3))
        else:
            self.vertices = None
            self.faces = None
            
    def __str__(self):
        if self.vertices:
            return "Vertices(%d), Faces(%d)" % (len(self.vertices), len(self.faces))
        else:
            return "No vertices"

class GMDCData(RCOLDataBlock):

    typeEnum = PackedFile.GMDC

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(GMDCData, self).extract(dg)
        
        # Some nodes
        self.sgres = cSGResource(dg)
        
        # Got name so terminate early if shallow
        if shallow:
            return

        if verbose:
            print("GMDC version = %d" % self.version)
            
        # Elements
        count = dg.get_dword()
        if verbose:
            print("%d elements" % count)
        self.elements = []
        for _ in range (count):
            self.elements.append(Element(dg, self.version, verbose))

        # Elements
        count = dg.get_dword()
        if verbose:
            print("%d linkages" % count)
        self.linkages = []
        for _ in range (count):
            self.linkages.append(Linkage(dg, self.version, verbose))

        # Groups
        count = dg.get_dword()
        if verbose:
            print("%d groups" % count)
        self.groups = []
        for _ in range (count):
            self.groups.append(Group(dg, self.version, verbose))
            
        # Model
        if verbose:
            print("Extracting model")
        self.model = Model(dg, self.version, verbose)

        # Subsets
        count = dg.get_dword()
        if verbose:
            print("%d subsets" % count)
        self.subsets = []
        for _ in range (count):
            self.subsets.append(Subset(dg, self.version, verbose))

    def get_name(self):
        return self.sgres.filename

    def dump(self, indent=0):
        super(GMDCData, self).dump(indent)
        self.sgres.dump(indent+1)
        
        if self.elements:
            indented_print(indent+1, "Elements:")
            for index, elem in enumerate(self.elements):
                indented_print(indent+2, "%d => %s" % (index, str(elem))) 
        else:
            indented_print(indent+1, "No elements")
            
        if self.linkages:
            indented_print(indent+1, "Linkages:")
            for index, link in enumerate(self.linkages):
                indented_print(indent+2, "%d => %s" % (index, str(link))) 
        else:
            indented_print(indent+1, "No linkages")
            
        if self.groups:
            indented_print(indent+1, "Groups:")
            for index, group in enumerate(self.groups):
                indented_print(indent+2, "%d => %s" % (index, str(group))) 
        else:
            indented_print(indent+1, "No groups")
            
        indented_print(indent+1, "Model:")
        self.model.dump(indent+2)
        
        if self.subsets:
            indented_print(indent+1, "Subsets:")
            for index, subset in enumerate(self.subsets):
                indented_print(indent+2, "%d => %s" % (index, str(subset))) 
        else:
            indented_print(indent+1, "No subsets")

GMDCData.register()