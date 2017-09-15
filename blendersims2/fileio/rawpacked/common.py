#!/usr/bin/python3
#-*- coding: utf-8 -*-

from abc import abstractmethod
from blendersims2.fileio.datagenerator import DataGenerator
from blendersims2.fileio.tgir import PackedFileType
from blendersims2.fileio.dumputils import indented_print

class RawPacked:

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

    @abstractmethod
    def extract(self, dg, verbose=False, debug=False):
        pass

    @classmethod
    def register_raw(cls):
        PackedFileType.register_raw(cls.typeEnum, cls)

    def dump(self, indent=0):
        indented_print(indent, "%s:" % self.__class__.__name__)
