#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import struct
import collections
#import zlib

from blendersims2.fileio.crcutils import sims2crc32, sims2crc24
from blendersims2.fileio.datagenerator import DataGenerator
from blendersims2.fileio.version import Version
from blendersims2.fileio.primitives import Sims2Reader
from blendersims2.fileio.tgir import Identifier, PackedFile, GetTypeFromDescriptor, GetGroupFromDescriptor, \
                 GetInstanceFromDescriptor, GetResourceFromDescriptor, DecodeDescriptor, IndexEntry
from blendersims2.fileio.rcol import RCOL
import blendersims2.fileio.rcol
import blendersims2.fileio.rawpacked

class DBPF(Sims2Reader):
    """Sims 2 Database-Packed File"""

    def extract(self, file, index_only=True, verbose=False):
        self.file = file
        if verbose:
            print("Opening file: %s" % file)
        try:
            with open(file, 'rb') as fh:
                if verbose:
                    print("Reading DBPF header")
                if (fh.read(4) != b'DBPF'):
                    raise ValueError("Not a valid DBPF!")
                data = struct.unpack('22I', fh.read(88))    # 22 uint32s
                self.ver = Version(data[0], data[1])
                # 3 unknown uint32s and 2 timestamps we don't care about
                self.indexver = Version(data[7], data[14])
                self.indexentrycount = data[8]
                self.indexoffset = data[9]
                self.indexsize = data[10]
                #holentrycount = data[11]
                #holeoffset = data[12]
                #holesize = data[13]
                #indexoffset_alt = data[15]
                # 6 reserved uint32s
        
                if (self.indexver.major != 7 or (self.indexver.minor != 1 and self.indexver.minor != 2)):
                    raise ValueError("Index version " + str(self.indexver) + " not supported")

                # Read the Index
                if verbose:
                    print("Reading DBPF index, which contains %d entries" % self.indexentrycount)
                fh.seek(self.indexoffset)
                self.dircomp_location = None
                self.dircomp = None
                self.index = {}
                self.namemap_locations = []
                self.namemaps = None
                for _ in range(0, self.indexentrycount):
                    entry = IndexEntry(self.indexver, fh)
                    if entry.identifier.type == PackedFile.CLST:
                        if self.dircomp_location:
                            raise ValueError("Found more than one directory of compressed files")
                        else:
                            self.dircomp_location = (entry.fileoffset, entry.filesize)
                    else:
                        descriptor = entry.identifier.get_descriptor()
                        if entry.identifier.type == PackedFile.NMAP:
                            self.namemap_locations.append((descriptor, entry.fileoffset, entry.filesize))
                        else:
                            self.index[descriptor] = (entry.fileoffset, entry.filesize, entry.identifier.ver)

                # If a directory of compressed files was found, and we're told to extract it, build up a list of descriptors
                if not index_only:
                    self.extract_dircomp(fh)
                    if len(self.namemap_locations) > 0:
                        self.extract_namemaps(fh)
    
        except ValueError as err:
            print("ValueError: \"%s\" in file %s" % (err, file))

    def dump_index(self):
        for descriptor in self.index:
            print(str(DecodeDescriptor(descriptor)))

    def extract_dircomp(self, fh, verbose=False):
        if self.dircomp_location:
            if not self.dircomp:    # Exists but not extracted
                self.dircomp = {}
                if verbose:
                    print("File contains a directory of compressed files")
                diroffset, dirsize = self.dircomp_location
                fh.seek(diroffset)
                if self.indexver.minor == 2:
                    records = dirsize // 20
                    if dirsize % 20 != 0:
                        raise ValueError("Size of directory of compressed files is not a multiple of 20: got %d, version %s, file = \"%s\"" % (dirsize, str(self.indexver), self.file))
                else:
                    records = dirsize // 16
                    if dirsize % 16 != 0:
                        raise ValueError("Size of directory of compressed files is not a multiple of 16: got %d, version %s, file = \"%s\"" % (dirsize, str(self.indexver), self.file))
                for _ in range(0, records):
                    identifier = Identifier(self.indexver, fh)
                    descriptor = identifier.get_descriptor()
                    decompressed_size = struct.unpack('I', fh.read(4))[0]
                    if verbose:
                        print("%s -> size %d" % (str(identifier), decompressed_size))
                    self.dircomp[descriptor] = decompressed_size
            return True
        else:
            return False

    def extract_namemaps(self, fh, verbose=False):
        if not self.namemaps:
            self.namemaps = {}
            self.extract_dircomp(fh)
    
            for descriptor, nmap_offset, nmap_size in self.namemap_locations:
                decompressed_size = None
                if descriptor in self.dircomp:
                    decompressed_size = self.dircomp[descriptor]
                    if verbose:
                        print("NMAP is compressed (%d bytes, decompressed %d)" % (nmap_size, decompressed_size))
                elif verbose:
                    print("NMAP is not compressed ")
                if verbose:
                    print ("Extracting NMAP")
                dg = DataGenerator(fh, nmap_offset, nmap_size, decompressed_size)
                
                count = dg.get_dword()
                new_map = {}
                nmap_type = GetInstanceFromDescriptor(descriptor)
                if verbose:
                    print("Decoding NMAP for type %s, entries = %d" % (str(nmap_type), count))
                for index in range(0, count):
                    if verbose:
                        print("%d => " % index, end='')
                    data = dg.get_dwords(3)
                    rcol_group = data[0]
                    rcol_instance = data[1]
                    # Get name - note unusual DWORD length
                    rcol_namelen = data[2]
                    rcol_name = dg.get_string(rcol_namelen)
                    rcol_descriptor = struct.pack('3I', nmap_type, rcol_group, rcol_instance)
                    new_map[rcol_name] = rcol_descriptor
                    if verbose:
                        print("%s => (%s, %s)" % (rcol_name, hex(rcol_group), hex(rcol_instance)))
                self.namemaps[nmap_type] = new_map
                
    def build_namemaps(self, verbose=False):
        """Construct a namemap from all packed RCOLs"""
        if verbose:
            print("Constructing namemap for " + self.file)

        with open(self.file, 'rb') as fh:
            self.namemaps = {}
            self.extract_dircomp(fh)

            for descriptor, (offset, size, _) in self.index.items():
                identifier = DecodeDescriptor(descriptor)
                if verbose:
                    print("Creating namemap entry for %s" % str(identifier))

                decompressed_size = None
                if descriptor in self.dircomp:
                    decompressed_size = self.dircomp[descriptor]
                dg = DataGenerator(fh, offset, size, decompressed_size)

                if identifier.type.is_rcol():
                    name = RCOL.get_name(dg).lower()
                    if int(identifier.type) not in self.namemaps:
                        self.namemaps[identifier.type] = {}
                    self.namemaps[identifier.type][name] = descriptor
                else:
                    if verbose:
                        print ("Skipping non-RCOL type %s" % str(identifier.type))

    def getResource(self, descriptor, verbose=False):
        decompressed_size = None
        rcol = None

        if descriptor in self.index:
            (offset, size, _) = self.index[descriptor]
        else:
            descriptor = descriptor[0:12] + bytes.fromhex('00000000')
            if descriptor in self.index:
                (offset, size, _) = self.index[descriptor]            
            else:
                if verbose:
                    print("Descriptor not found in index: %s" % str(DecodeDescriptor(descriptor)))
                return rcol

        if verbose:
            print ("Opening " + self.file)
        with open(self.file, 'rb') as fh:
            if self.extract_dircomp(fh) and descriptor in self.dircomp:
                decompressed_size = self.dircomp[descriptor]
                if verbose:
                    print("RCOL is compressed (%d bytes, decompressed %d)" % (size, decompressed_size))
            elif verbose:
                print("RCOL is not compressed ")
            self.extract_namemaps(fh)
            identifier = DecodeDescriptor(descriptor)
            if identifier.type.is_rcol():
                if verbose:
                    print ("Extracting RCOL from %s" % str(identifier))
                resource = RCOL(fh, identifier, offset, size, decompressed_size, self, verbose)
            else:
                if verbose:
                    print("Extracting raw packed file from %s" % str(identifier))
                resource = identifier.type.RawPackedConstructor()(fh, identifier, offset, size, decompressed_size, self, verbose)
            if verbose:
                print ("Done!")
        #except ValueError as err:
        #    print("ValueError while processing %s: %s" % (self.file, err))
        #    print("Descriptor: %s" % str(descriptor))
        #    rcol = None
        return resource
    
    def findname(self, rcol_type, rcol_name, verbose=False):
        if not self.namemaps:
            if type(self.namemaps) == None:
                raise RuntimeError("Namemaps not initialised")
            else:
                if verbose:
                    print("No namemap in file %s" % self.file)
                self.build_namemaps(verbose)
        if rcol_type not in self.namemaps:
            if verbose:
                print("No local namemap for type %s" % str(rcol_type))
            return None
        rcol_map = self.namemaps[rcol_type]
        lc_name = rcol_name.lower()
        if lc_name in rcol_map:
            if verbose:
                print("SIMS2 CRC32 = %s" % hex(sims2crc32(lc_name.encode('ascii'))))
                print("SIMS2 CRC24 = %s" % hex(sims2crc24(lc_name.encode('ascii'))))
                #print("Standard CRC32 = %s" % hex(standard_crc32(lc_name.encode('ascii'))))
                #print("ZLIB CRC32 = %s" % hex(zlib.crc32(lc_name.encode('ascii'))))            
            return rcol_map[lc_name]
        else:
            print("Failed to find %s in %s local namemap" % (rcol_name, str(rcol_type)))
            return None

class PackageManager:
    
    def __init__(self):
        self.packages = []
        self.package_index = {}
        self.searchlist = []
        
    def AddDirectory(self, path):
        self.searchlist.append(path)
        
    def ReadDBPFIndices(self, extract_namemaps=False, verbose=False, alert_identifier=None):
        packfiles = []
        
        # Iterate through directories and get all the .package files
        for searchdir in self.searchlist:
            if verbose:
                print("Searching " + searchdir)
            for root, _, files in os.walk(searchdir):
                for file in files:
                    if file.lower().endswith(".package"):
                        packfiles.append(os.path.join(root, file))
        if verbose:
            print("Found " + str(len(packfiles)) + " .package files")
            
        # Now iterate through the files and read the DBPFs, building up a hash of parts and a list of CRESs
        if verbose:
            typecounts = collections.Counter()
        self.meta_namemap = {}
        for file in packfiles:
            if verbose:
                print(file)
            package = DBPF()
            package.extract(file, index_only=(not extract_namemaps))
            self.packages.append(package)
            for descriptor in package.index:
                typ = GetTypeFromDescriptor(descriptor)
                if verbose:
                    typecounts[typ] += 1
                self.package_index[descriptor] = package
                if alert_identifier:
                    if alert_identifier == GetInstanceFromDescriptor(descriptor):
                        print("Found identifier %s, descriptor %s, in file %s \n" % (format(alert_identifier, '#010x'),
                                                                                     str(DecodeDescriptor(descriptor)),
                                                                                     file));
            if extract_namemaps:
                self.extract_namemap(package)

        if verbose:
            total = 0
            for typename, count in typecounts.items():
                print(str(count) + " " + str(typename) + "s found")
                total += count
            print ("Total %d RCOLs" % total)
    
    def extract_namemap(self, package, verbose=False):
        if not package.namemaps:
            #package.build_namemaps()
            pass
        if package.namemaps:
            for rcol_type, namemap in package.namemaps.items():
                if rcol_type not in self.meta_namemap:
                    self.meta_namemap[rcol_type] = {}
                self.meta_namemap[rcol_type].update(namemap)

    def GetRCOLsByType(self, rtype):
        for descriptor in self.package_index:
            dtype = GetTypeFromDescriptor(descriptor)
            if rtype == dtype:
                yield descriptor
    
    def GetRCOLsByGroup(self, rgroup):
        for descriptor in self.package_index:
            dgroup = GetGroupFromDescriptor(descriptor)
            if rgroup == dgroup:
                yield descriptor
    
    def GetRCOLsByInstance(self, rinst):
        for descriptor in self.package_index:
            dinst = GetInstanceFromDescriptor(descriptor)
            if rinst == dinst:
                yield descriptor
    
    def GetRCOLsByResource(self, rres):
        for descriptor in self.package_index:
            dres = GetResourceFromDescriptor(descriptor)
            if rres == dres:
                yield descriptor
    
    def getResource(self, descriptor, verbose=False):
        if descriptor not in self.package_index:
            descriptor = descriptor[0:12] + bytes.fromhex('00000000')
        if descriptor in self.package_index:
            package = self.package_index[descriptor]
            if verbose:
                print ("Getting resource for %s" % str(DecodeDescriptor(descriptor)))
            return package.getResource(descriptor, verbose)
        else:
            #raise RuntimeError("Can't find descriptor in package list")
            return None
    
    def GetRCOLByName(self, rcol_type, rcol_name, verbose=False):
        descriptor = self.findname(rcol_type, rcol_name)
        rcol = self.getResource(descriptor)
        if not rcol:
            if verbose:
                print("Couldn't locate descriptor: %s" % str(DecodeDescriptor(descriptor)))
            resource = sims2crc32(rcol_name.lower().encode('ascii'))
            resource_bytes = struct.pack('I', resource)
            descriptor = b''.join((descriptor, resource_bytes))
            rcol = self.getResource(descriptor)
            if not rcol:
                print("Couldn't locate descriptor: %s" % str(DecodeDescriptor(descriptor)))
                raise RuntimeError("Can't find descriptor in package list")
        return rcol

    def findname(self, rcol_type, resource_name, verbose=False):
        name_lc = resource_name.lower()
        if not self.meta_namemap:
            if verbose:
                print("Using findname but meta namemap hasn't been generated, generating now")
            for package in self.packages:
                if not package.namemaps:
                    with open(package.file, 'rb') as fh:
                        package.extract_namemaps(fh)
                self.extract_namemap(package)
        if rcol_type not in self.meta_namemap:
            raise RuntimeError("Can't find RCOL type \"%s\" in meta namemap" % str(rcol_type))            
        namemap = self.meta_namemap[rcol_type]
        if name_lc not in namemap:
            if False:
                from pprint import pprint
                pprint(namemap)
                #pprint(self.meta_namemap)
                for pack in self.packages:
                    if not pack.namemaps:
                        print ("No namemaps for file %s" % pack.file)
                    elif rcol_type not in pack.namemaps:
                        print ("No %s namemap for file %s" % (str(rcol_type), pack.file))                        
                    elif name_lc in pack.namemaps[rcol_type]:
                        print("Found in namemap for file %s" % pack.file)
            raise RuntimeError("Can't find \"%s\" in \"%s\" namemap" % (resource_name, str(rcol_type)))
        ident = DecodeDescriptor(namemap[name_lc])
        if ident.resource == 0:
            ident.resource = sims2crc32(name_lc.encode('ascii'))
        return ident.get_descriptor()
    
    def getAllObjects(self, verbose=True):
        resources = self.GetRCOLsByType(PackedFile.OBJD)
        for item_desc in resources:
            ident = DecodeDescriptor(item_desc)
            objd = self.getResource(item_desc)
            yield (ident.group, objd.name)
        
    def getGroupResources(self, group, verbose=True):        
        resources = self.GetRCOLsByGroup(group)
        objd = None
        model_names = None
        cres = None
        for item_desc in resources:
            # Must already be in index as that's where we got it from
            package = self.package_index[item_desc]
            ident = DecodeDescriptor(item_desc)
            if ident.type == PackedFile.OBJD:
                if verbose:
                    print("%s %s found in %s" % (str(ident.type), str(ident), package.file))
                objd = self.getResource(item_desc)
            if ident.type == PackedFile.STR and ident.instance == 0x00000085:
                if verbose:
                    print("%s %s found in %s" % (str(ident.type), str(ident), package.file))
                model_names = self.getResource(item_desc)

        if model_names:
            model_name, _ = model_names.strings[1][1]
            cres_name = model_name + "_cres"
            descriptor = self.findname(PackedFile.CRES, cres_name.lower())
            cres = self.getResource(descriptor)

        if verbose:
            print("Name: \"%s\"" % objd.name)
            print("Model Name: \"%s\"" % model_name)
            print("CRES: %s" % cres.rcoldata[0].sgres.filename)