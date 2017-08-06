#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.datagenerator import DataGenerator
from blendersims2.fileio.errors import RCOLNotSupported
from blendersims2.fileio.rcol.common import RCOLHeader

from blendersims2.fileio.node import cTransformNode, cBoneDataExtension
import blendersims2.fileio.rcol.builders
import blendersims2.fileio.rcol.cres
import blendersims2.fileio.rcol.extension
import blendersims2.fileio.rcol.gmdc
import blendersims2.fileio.rcol.gmnd
import blendersims2.fileio.rcol.light
import blendersims2.fileio.rcol.shape
import blendersims2.fileio.rcol.viewer

cTransformNode.register()
cBoneDataExtension.register()

class RCOL:
    """Sims2 Scenegraph Resource Collection"""
    
    def __init__(self, fh=None, identifier=None, offset=None, size=None, decompressed_size=None, dbpf=None, verbose=False):
        self.dbpf = dbpf
        self.identifier = identifier
        if fh:
            # Create a data generator which is a bit smarter than a file handle, to simplify reads from data blocks which may or may not be compressed
            dg = DataGenerator(fh, offset, size, decompressed_size, verbose)
            if verbose:
                self.extract(dg, verbose=True)
            else:
                self.extract(dg)

    def extract(self, dg, verbose=False, debug=True):
        if verbose:
            print("Creating RCOL header")
        self.header = RCOLHeader(dg, verbose)

        if verbose:
            print("RCOL header done, starting data blocks (item count %s)" % self.header.item_count)
        self.rcoldata = []
        if debug:
            self.unsupported = []
        for datablock in range(self.header.item_count):
            rcol_id = self.header.rcol_ids[datablock]
            if verbose:
                print("Data block %s has type %s" % (datablock, str(rcol_id)))
            if rcol_id.is_rcol():
                self.rcoldata.append(rcol_id.RCOLConstructor()(dg))
            elif debug:
                if rcol_id not in self.unsupported:
                    self.unsupported.append(rcol_id)
                print("Unsupported RCOL Type %s" % str(rcol_id))
                break
            else:
                raise RCOLNotSupported("Unsupported RCOL Type %s" % str(rcol_id))
        if verbose:
            print("Done!")
            
    @classmethod
    def get_name(cls, dg, identifier, verbose=False):
        if verbose:
            print ("Getting name for %s" % str(identifier))
        rcol = cls()
        rcol.header = RCOLHeader(dg, verbose)
        if rcol.header.item_count:
            rcol_id = rcol.header.rcol_ids[0]
            if rcol_id.is_rcol():
                rcol = rcol_id.RCOLConstructor()(dg, shallow=True, verbose=verbose)
                return rcol.get_name()
            else:
                print("Unsupported RCOL type %s in get_name, returning no name" % str(rcol_id))
                return None
        else:
            if verbose:
                print("No items in this RCOL, not returning a name")
            return None
        
    def get_group(self):
        return self.identifier.group;
    
    def ResolveAllLinks(self, packman, verbose=False):
        for link in self.header.filelinks:
            link.resolve(packman, self.dbpf, parent_group=self.identifier.group, verbose=verbose)
        for rcol in self.rcoldata:
            rcol.resolve(packman, self.dbpf, verbose)
    
    def dump(self, indent=0):
        self.header.dump(indent)
        for datablock in self.rcoldata:
            datablock.dump(indent)
        for link in self.header.filelinks:
            print()
            link.target.dump()