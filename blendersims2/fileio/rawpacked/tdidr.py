#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.version import Version
from blendersims2.fileio.tgir import Identifier, PackedFile
from blendersims2.fileio.rawpacked.common import RawPacked
from blendersims2.fileio.dumputils import indented_print

class TDIDR(RawPacked):
    """Sims2 3D ID Referencing File"""

    typeEnum = PackedFile.TDIDR

    def extract(self, dg, verbose=False, debug=True):
        data = dg.get_dwords(3)
        if data[0] != 0xdeadbeef:
            raise ValueError("ID is not 0xDEADBEEF")
        self.version = Version(7, data[1])
        count = data[2]
        if verbose:
            print ("3DIDR identifier version %s" % str(self.version))
        self.refs = []
        for _ in range(count):
            identifier = Identifier(self.version, dg)
            ptype = identifier.type
            if verbose:
                print("Type: %s" % str(ptype))
            self.refs.append(identifier)
            
    def dump(self, indent=0):
        super(TDIDR, self).dump(indent)
        indented_print(indent+1, "References:")
        for ident in self.refs:
            indented_print(indent+2, "%s: %s" % (str(ident.type), str(ident)))

TDIDR.register_raw()