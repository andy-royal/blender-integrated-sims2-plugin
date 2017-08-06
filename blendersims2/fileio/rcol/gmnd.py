#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.tgir import PackedFile, PackedFileType
from blendersims2.fileio.node import cObjectGraphNode, cSGResource
from blendersims2.fileio.rcol.common import RCOLDataBlock

class GMNDData(RCOLDataBlock):

    typeEnum = PackedFile.GMND

    def extract(self, dg, shallow=False, verbose=False):
        # First get the common RCOLDataBlock header
        super(GMNDData, self).extract(dg)
        
        # Some nodes
        self.objgraphnode = cObjectGraphNode(dg)
        self.sgres = cSGResource(dg)
        
        # Got name so terminate early if shallow
        if shallow:
            return

        # Forced relocation?
        if self.version == 11:
            tmp = dg.get_word()
            if tmp == 2:
                self.forced_relocation = True
            elif tmp == 512:
                self.forced_relocation = False
            else:
                raise ValueError("Unexpected forced relocation value %d" % tmp)
            
        # Assisted geometry
        if self.version == 11 or self.version == 12:
            tmp = dg.get_word()
            if tmp == 1:
                self.assisted_geometry = True
            elif tmp == 256:
                self.assisted_geometry = False
            else:
                raise ValueError("Unexpected assisted geometry value %d" % tmp)
            # Unknown
            tmp = dg.get_byte()
            if tmp != 1:
                raise ValueError("Expected unknown parameter value 1, got %d" % tmp)

        # Attached RCOLs
        count = dg.get_dword()
        self.attached_RCOLs = []
        for _ in range(count):
            rcol_type = PackedFileType(dg.get_dword())
            if rcol_type.is_rcol():
                rcol_type.RCOLConstructor()(dg, verbose)
            else:
                raise ValueError("%s is not an RCOL type" % str(rcol_type))
#             rcol = RCOL()
#             rcol.extract(dg, verbose)
#             self.attached_RCOLs.append(rcol)

    def get_name(self):
        return self.sgres.filename

    def dump(self, indent=0):
        super(GMNDData, self).dump(indent)
        self.objgraphnode.dump(indent+1)
        self.sgres.dump(indent+1)
        
        if self.version == 11:
            indented_print(indent+1, "Forced relocation = %s" % str(self.forced_relocation))
        if self.version == 11 or self.version == 12:
            indented_print(indent+1, "Assisted geometry = %s" % str(self.assisted_geometry))

        indented_print(indent+1, "%d attached RCOLs" % len(self.attached_RCOLs))

    def dump_references(self, indent=0):
        if self.attached_RCOLs:
            for rcol in self.attached_RCOLs:
                print()
                rcol.dump(indent)

GMNDData.register()