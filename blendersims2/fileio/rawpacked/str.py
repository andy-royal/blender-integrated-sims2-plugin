#!/usr/bin/python3
#-*- coding: utf-8 -*-

from blendersims2.fileio.tgir import PackedFile
from blendersims2.fileio.rawpacked.common import RawPacked
from blendersims2.fileio.dumputils import indented_print
from blendersims2.fileio.parseutils import ParseNullTerminatedString

class STR(RawPacked):
    """Sims2 Text List"""

    typeEnum = PackedFile.STR

    def extract(self, dg, verbose=False, debug=False):
        self.name = ParseNullTerminatedString(dg, size=64, verbose=verbose)
        self.format = dg.get_word()
        if verbose:
            print("Name: \"%s\"; Format: 0x%04x" % (self.name, self.format))
        count = dg.get_word()
        self.strings = {}
        for _ in range(count):
            language_code = dg.get_byte()
            if language_code not in self.strings:
                self.strings[language_code] = []
            val = ParseNullTerminatedString(dg, size=None, verbose=verbose)
            description = ParseNullTerminatedString(dg, size=None, verbose=verbose)
            self.strings[language_code].append((val, description))
            if verbose:
                print("%d: %s => %s" % (language_code, val, description))
        
    def dump(self, indent=0):
        super(STR, self).dump(indent)
        indented_print(indent+1, "Name: %s" % self.name)
        indented_print(indent+1, "Format: 0x%04x" % self.format)
        for language_code in self.strings:
            indented_print(indent+1, "Language %d:" % language_code)
            for val, description in self.strings[language_code]:
                indented_print(indent+2, "%s => %s" % (val, description))

STR.register_raw()
