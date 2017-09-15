#!/usr/bin/python3
#-*- coding: utf-8 -*-

from abc import abstractmethod

from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.primitives import Sims2Reader
from blendersims2.fileio.tgir import PackedFileType, FileLink
from blendersims2.fileio.node import Node

class RCOLHeader(Sims2Reader):
    """Sims2 Scenegraph Resource Collection header"""
    
    def extract(self, dg, verbose=False):
        # Read first DWORD. If it's 0xFFFF0001 we'll get resource IDs in the file links and the next DWORD is the
        # number of file links. Otherwise the first DWORD is the number of file links.
        data = dg.get_dword()
        if data == 0xFFFF0001:
            self.version_mark = True
            if verbose:
                print("First DWORD is 0xFFFF0001, setting version mark flag")
            sectlen = data = dg.get_dword()
        else:
            self.version_mark = False
            if verbose:
                print("First DWORD is %s, clearing version mark flag as not 0xFFFF0001" % format(data, '#010x'))
            sectlen = data
            
        # Now read in the specified number of file links
        self.filelinks = []
        if verbose:
            print("Reading %s FileLinks" % sectlen)
        for _ in range(sectlen):
            tmp = FileLink(dg, self.version_mark)
            self.filelinks.append(tmp)
            
        # RCOLIDs
        self.item_count = dg.get_dword()
        self.rcol_ids = []
        if verbose:
            print("Reading %s RCOL IDs" % self.item_count)
        for index in range(self.item_count):
            rcol_id = PackedFileType(dg.get_dword())
            if verbose:
                print("    %d => %s" % (index, str(rcol_id)))
            self.rcol_ids.append(rcol_id)
            
    def dump(self, indent=0):
        indented_print(indent, "RCOL Header:")
        if self.version_mark:
            indented_print(indent+1, "Version mark present")
            if len(self.filelinks) > 0:
                indented_print(indent+1, "FileLinks:")
                for index, link in enumerate(self.filelinks):
                    indented_print(indent+2, "%d => %s" % (index, str(link)))
            else:
                indented_print(indent+1, "No filelinks")

class RCOLDataBlock(Node):
    """Base data block for RCOL data. Bulk of RCOL will be formed of classes derived from this."""
    
    # This is basically a node, but it must also have a name
    def __init__(self, dg=None, shallow=False, verbose=False):
        self.name = None
        if dg:
            # If not verbose, don't set it false so default is used
            if verbose:
                self.extract(dg, shallow, verbose=True)
            else:
                self.extract(dg, shallow)
    
    @abstractmethod
    def extract(self, dg, shallow=False, verbose=False):
        super(RCOLDataBlock, self).extract(dg, verbose)

    @abstractmethod
    def get_name(self):
        pass

    @classmethod
    def register_RCOL(cls):
        PackedFileType.register_RCOL(cls.typeEnum, cls)

    @staticmethod
    def get_nodetype(data):
        return PackedFileType(data)

    @staticmethod
    def nodetype2string(data):
        return str(data)
