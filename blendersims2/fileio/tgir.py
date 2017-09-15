#!/usr/bin/python3
#-*- coding: utf-8 -*-

import struct
import copy

from enum import IntEnum

from blendersims2.fileio.primitives import Sims2Reader
from blendersims2.fileio.version import Version
from blendersims2.fileio.dumputils import indented_print

class Identifier(Sims2Reader):
    """General way of identifying an RCOL"""
    
    def __init__(self, ver, fh=None):
        self.ver = ver
        super(Identifier, self).__init__(fh)

    def extract(self, fh, verbose=False):
        if (self.ver.minor == 2):
            data = struct.unpack('4I', fh.read(16))    # 4 uint32s
        else:
            data = struct.unpack('3I', fh.read(12))    # 3 uint32s
        self.type = PackedFileType(data[0])
        self.group = data[1]
        self.instance = data[2]
        if (self.ver.minor == 2):
            self.resource = data[3]
        else:
            self.resource = 0;
            
    @classmethod
    def from_tgir(cls, typ, group, instance, resource):
        if resource:
            ver = Version(7, 2)
        else:
            ver = Version(7, 1)
        ident = cls(ver)
        ident.type = PackedFileType(typ)
        ident.group = group
        ident.instance = instance
        if resource:
            ident.resource = resource
        else:
            ident.resource = 0
        return ident

    def get_descriptor(self):
        #if (self.ver.minor == 2):
        descriptor = struct.pack('4I', int(self.type), self.group, self.instance, self.resource)
        #else:
        #    descriptor = struct.pack('3I', int(self.type), self.group, self.instance1)
        return descriptor
    
    def __str__(self):
        #if (self.ver.minor == 2):
        return "Identifier %s:%s:%s:%s (ver %d.%d)" % (format(int(self.type), '#010x'),
                                                       format(self.group, '#010x'),
                                                       format(self.instance, '#010x'),
                                                       format(self.resource, '#010x'),
                                                       self.ver.major, self.ver.minor)
        #else:
        #    return "Identifier %s:%s:%s (ver %d.%d)" % (format(int(self.type), '#010x'),
        #                                                format(self.group, '#010x'),
        #                                                format(self.instance1, '#010x'),
        #                                                self.ver.major, self.ver.minor)

def DecodeDescriptor(descriptor, verbose=False):
    if verbose:
        print ("Identifier length is %d" % len(descriptor))
    if len(descriptor) == 16:    # 4 x 4 bytes
        data = struct.unpack('4I', descriptor)
        ver = Version(7, 2)
    elif len(descriptor) == 12:  # 3 x 4 bytes
        data = struct.unpack('3I', descriptor)
        ver = Version(7, 1)
    else:
        raise ValueError("Unexpected descriptor length: %d" % len(descriptor))
    tmp = Identifier(ver)
    tmp.type = PackedFileType(data[0])
    tmp.group = data[1]
    tmp.instance = data[2]
    if len(descriptor) == 16:
        tmp.resource = data[3]
    else:
        tmp.resource = 0
    return tmp

def GetTypeFromDescriptor(descriptor, verbose=False):
    return PackedFileType(struct.unpack('I', descriptor[0:4])[0])

def GetGroupFromDescriptor(descriptor, verbose=False):
    return struct.unpack('I', descriptor[4:8])[0]

def GetInstanceFromDescriptor(descriptor, verbose=False):
    return struct.unpack('I', descriptor[8:12])[0]

def GetResourceFromDescriptor(descriptor, verbose=False):
    return struct.unpack('I', descriptor[12:16])[0]

class PackedFile(IntEnum):
    invalid  = 0x00000000
    cViewRec = 0x0c152b8e
    XMOL     = 0x0c1fe246
    BINX     = 0x0c560f39
    TXTR     = 0x1c4a276c
    cBound   = 0x1cfeceb8
    cLight   = 0x253d2018
    cTSFace  = 0x2b70b86e
    XTOL     = 0x2c1fd8a1
    BCON     = 0x42434f4e
    BHAV     = 0x42484156
    BMP      = 0x424d505f
    CATS     = 0x43415453
    CTSS     = 0x43545353
    DGRP     = 0x44475250
    FCNS     = 0x46434e53
    FWAV     = 0x46574156
    GLOB     = 0x474c4f42
    TXMT     = 0x49596978
    XSTN     = 0x4c158081
    MMAT     = 0x4c697e5a
    CINE     = 0x4d51f042
    NREF     = 0x4e524546
    NMAP     = 0x4e6d6150
    OBJD     = 0x4f424a44
    OBJF     = 0x4f424a66
    PALT     = 0x50414c54
    POSI     = 0x504f5349
    PTBP     = 0x50544250
    SLOT     = 0x534c4f54
    SPR2     = 0x53505232
    STR      = 0x53545223
    TPRP     = 0x54505250
    TRCN     = 0x5452434e
    TREE     = 0x54524545
    TTAB     = 0x54544142
    TTAs     = 0x54544173
    cProc    = 0x5ce7e026
    cTang    = 0x5d054225 
    cShape   = 0x65245517
    cDLE     = 0x6a836d56
    cTran    = 0x65246462
    COLL     = 0x6c4f359d
    GMND     = 0x7ba3838c
    IMG      = 0x856ddbac
    XHTN     = 0x8c1580b5
    cTag     = 0x9a809646
    cIMB     = 0x9bffc10d
    GMDC     = 0xac4f8687
    TDIDR    = 0xac506764
    AGED     = 0xac598eac
    LGHTA    = 0xc9c81b9b    # Ambient
    LGHTD    = 0xc9c81ba3    # Directional
    LGHTP    = 0xc9c81ba9    # Point
    LGHTS    = 0xc9c81bad    # Spot
    XOBJ     = 0xcca8e925
    LxNR     = 0xcccef852
    matShad  = 0xcd7fe87a
    cViewer  = 0xdca76dbb
    cComp    = 0xdcdda078
    CRES     = 0xe519c933
    CLST     = 0xe86b1eef
    VERS     = 0xebfee342
    GZPS     = 0xEBCF3E27
    cBone    = 0xe9075bc5
    LIFO     = 0xed534136
    ANIM     = 0xfb00791e
    SHPE     = 0xfc6eb1f7

    #@classmethod
    #def _missing_(cls, value):
    #    #raise ValueError("%s is not a valid %s" % (hex(value), cls.__name__))
    
class PackedFileType:

    RCOLDict = {}
    RawPackedDict = {}
    
    RCOLStrings = {
        PackedFile.invalid  : 'NULL',
        PackedFile.cViewRec : 'cViewerRefNodeRecursive',
        PackedFile.XMOL     : 'Mesh overlay XML',
        PackedFile.BINX     : 'Binary Index',
        PackedFile.TXTR     : 'TXTR',
        PackedFile.cBound   : 'cBoundingVolumeBuilder',
        PackedFile.cLight   : 'cLight',
        PackedFile.cTSFace  : 'cTSFaceGeometryBuilder',
        PackedFile.XTOL     : 'Texture Overlay XML',
        PackedFile.BCON     : 'BCON',
        PackedFile.BHAV     : 'BHAV',
        PackedFile.BMP      : 'BMP',
        PackedFile.CATS     : 'CATS',
        PackedFile.CTSS     : 'CTSS',
        PackedFile.DGRP     : 'DGRP',
        PackedFile.FCNS     : 'FCNS',
        PackedFile.FWAV     : 'FWAV',
        PackedFile.GLOB     : 'GLOB',
        PackedFile.TXMT     : 'TXMT',
        PackedFile.XSTN     : 'Skin Tone XML',
        PackedFile.MMAT     : 'MMAT',
        PackedFile.CINE     : 'CINE',
        PackedFile.NREF     : 'NREF',
        PackedFile.NMAP     : 'NMAP',
        PackedFile.OBJD     : 'OBJD',
        PackedFile.OBJF     : 'OBJF',
        PackedFile.PALT     : 'PALT',
        PackedFile.POSI     : 'POSI',
        PackedFile.PTBP     : 'PTBP',
        PackedFile.SLOT     : 'SLOT',
        PackedFile.SPR2     : 'SPR2',
        PackedFile.STR      : 'STR',
        PackedFile.TPRP     : 'TPRP',
        PackedFile.TRCN     : 'TRCN',
        PackedFile.TREE     : 'TREE',
        PackedFile.TTAB     : 'TTAB',
        PackedFile.TTAs     : 'TTAs',
        PackedFile.cProc    : 'cProcessDeformationsBuilder',
        PackedFile.cTang    : 'cTangentSpaceBuilder',
        PackedFile.cShape   : 'cShape',
        PackedFile.cDLE     : 'cDLE',
        PackedFile.cTran    : 'cTran',
        PackedFile.COLL     : 'Collection',
        PackedFile.GMND     : 'GMND',
        PackedFile.IMG      : 'IMG',
        PackedFile.XHTN     : 'Hair tone XML',
        PackedFile.cTag     : 'cTagExtension',
        PackedFile.GMDC     : 'GMDC',
        PackedFile.TDIDR    : '3IDR',
        PackedFile.AGED     : 'AGED',
        PackedFile.LGHTA    : 'LGHTA',    # Ambient
        PackedFile.LGHTD    : 'LGHTD',    # Directional
        PackedFile.LGHTP    : 'LGHTP',    # Point
        PackedFile.LGHTS    : 'LGHTS',    # Spot
        PackedFile.XOBJ     : 'Object XML',
        PackedFile.LxNR     : 'LxNR',
        PackedFile.matShad  : 'matShad',
        PackedFile.cViewer  : 'cViewerRefNode',
        PackedFile.cComp    : 'cCompactorBuilder',
        PackedFile.CRES     : 'CRES',
        PackedFile.CLST     : 'CLST',
        PackedFile.VERS     : 'VERS',
        PackedFile.GZPS     : 'GZPS',
        PackedFile.cBone    : 'cBoneDataExtension',
        PackedFile.LIFO     : 'LIFO',
        PackedFile.ANIM     : 'ANIM',
        PackedFile.SHPE     : 'SHPE'
    }

    def __init__(self, val):
        self.value = PackedFile(val)
        
    def __eq__(self, x):
        return (self.value == x)
    
    def __int__(self):
        return self.value
    
    def __hash__(self):
        return self.value
    
    def is_rcol(self):
        return (self.value in self.RCOLDict)
    
    def is_raw_packed(self):
        return (self.value in self.RawPackedDict)
    
    def RCOLConstructor(self):
        if self.value in self.RCOLDict:
            return self.RCOLDict[self.value]
        else:
            raise("%s is not supported as an RCOL" % str(self.value))

    def RawPackedConstructor(self):
        if self.value in self.RawPackedDict:
            return self.RawPackedDict[self.value]
        else:
            raise("%s is not supported as a RawPacked file" % str(self.value))

    @classmethod
    def register_RCOL(cls, enum, func):
        cls.RCOLDict[enum] = func

    @classmethod
    def register_raw(cls, enum, func):
        cls.RawPackedDict[enum] = func

    def __str__(self):
        return self.RCOLStrings[self.value]

class IndexEntry(Sims2Reader):
    """An entry in a Sims 2 Index"""

    def __init__(self, ver=None, fh=None):
        if fh:
            self.extract(ver, fh)

    def extract(self, ver, fh):
        self.identifier = Identifier(ver, fh)
        data = struct.unpack('2I', fh.read(8)) 
        self.fileoffset = data[0]
        self.filesize = data[1]
            
    def get_descriptor(self):
        return self.identifier.get_descriptor()

class FileLink(Sims2Reader):
    """Links from one RCOL to another"""
    
    def __init__(self, dg=None, res_id=None):
        self.target = None
        if dg:
            self.extract(dg, res_id)

    def extract(self, dg, res_id, verbose=False):
        if res_id:
            data = dg.get_dwords(4)
        else:
            data = dg.get_dwords(3)
        self.group = data[0]
        self.instance = data[1]
        if res_id:
            self.resource = data[2]
            self.type = data[3]
        else:
            self.type = data[2]
            self.resource = 0
        if verbose:
            self.dump()

    def get_descriptor(self, verbose=False):
        #if self.resource:
        descriptor = struct.pack('4I', self.type, self.group, self.instance, self.resource)
        #else:
            #descriptor = struct.pack('4I', self.type, self.group, self.instance, 0)
            #descriptor = struct.pack('3I', self.type, self.group, self.instance)
        return descriptor
    
    def resolve(self, packman, dbpf, parent_group=None, verbose=False):
        descriptor = self.get_descriptor()
        identifier = DecodeDescriptor(descriptor, verbose)
        if verbose:
            print("Resolving filelink, %s" % str(identifier))

        # Try same package first
        self.target = dbpf.getResource(descriptor, verbose)
        if not self.target:
            local_id = copy.copy(identifier)
            if identifier.group != 0xffffffff:
                local_id.group = 0xffffffff
                self.target = dbpf.getResource(local_id.get_descriptor(), verbose)
        if not self.target and identifier.group != parent_group:
            local_id.group = parent_group
            self.target = dbpf.getResource(local_id.get_descriptor(), verbose)
            
        # Otherwise try all known packages
        if not self.target:
            self.target = packman.getResource(descriptor, verbose)
            
        # Out of ideas
        if not self.target:
            raise RuntimeError("Failed to resolve filelink, %s" % str(identifier))
        
        # Iterate
        self.target.ResolveAllLinks(packman, verbose)

    def __str__(self):
        #if self.resource:
        return str("Group = %s, instance = %s, resource = %s, type = %s" % (format(self.group, '#010x'),
                                                                            format(self.instance, '#010x'),
                                                                            format(self.resource, '#010x'),
                                                                            str(self.type)))
        #else:
            #return str("Group = %s, instance = %s, type = %s" % (format(self.group, '#010x'),
            #                                                     format(self.instance, '#010x'),
            #                                                     str(self.type)))
             
    def dump(self, indent=0):
        indented_print(indent, "FileLink: %s" % str(self))
