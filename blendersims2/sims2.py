#!/usr/bin/python3
#-*- coding: utf-8 -*-

import winreg
import fnmatch
import os

from blendersims2.fileio.package import PackageManager
from blendersims2.fileio.tgir import Identifier, PackedFile, DecodeDescriptor
from blendersims2.fileio.crcutils import sims2crc32, sims2crc24
from blendersims2.fileio.rawpacked.objd import OBJD

def AddSims2DirectoriesToPackageManager(packman):
    # Get Sims 2 install directory and add appropriate subdirectories
    sims2reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
               "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\Sims2.exe")
    sims2install, dummy = winreg.QueryValueEx(sims2reg, "Path")
    #if True:
    #    sims2install = "C:\\Users\\aroyal\\Documents\\Sims 2 Exports"
    packpath = sims2install + "\\TSData\\Res\\"    # Default search path
    subdirs = ["Sims3D", "Objects", "Materials"]
    for leafdir in subdirs:
        packman.AddDirectory(packpath + leafdir + "\\")
    neighpath = packpath + "UserData\\Neighborhoods\\"
    for item in fnmatch.filter(os.listdir(neighpath), "N*"):
        if os.path.isdir(neighpath + item):
            packman.AddDirectory(neighpath + item + "\\Characters\\")

    # University
    sims2reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
               "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\Sims2EP1.exe")
    sims2install, dummy = winreg.QueryValueEx(sims2reg, "Path")
    packpath = sims2install + "\\TSData\\Res\\"    # Default search path
    subdirs = ["3D", "Objects", "Materials"]
    for leafdir in subdirs:
        packman.AddDirectory(packpath + leafdir + "\\")

    # Nightlife
    sims2reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
               "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\Sims2EP2.exe")
    sims2install, dummy = winreg.QueryValueEx(sims2reg, "Path")
    packpath = sims2install + "\\TSData\\Res\\"    # Default search path
    subdirs = ["3D", "Objects", "Materials"]
    for leafdir in subdirs:
        packman.AddDirectory(packpath + leafdir + "\\")

    # User data
    sims2user = "C:\\Users\\aroyal\\Documents\\EA Games\\The Sims 2"    # Environment?
    subdirs = ["SavedSims", "Downloads"]
    for leafdir in subdirs:
        packman.AddDirectory(sims2user + "\\" + leafdir + "\\")

def CheckAllCRES(verbose=False, starting_point=0):
    
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices()
    unsupported = []
    creslist = packman.GetRCOLsByType(PackedFile.CRES)
    index = 0
    for cres_descriptor in creslist:
        if index < starting_point:
            index += 1
            continue
        if verbose:
            print("Extracting CRES at index %d: %s" % (index, str(DecodeDescriptor(cres_descriptor))))
        cres = packman.getResource(cres_descriptor)
        cres.ResolveAllLinks(packman)
        if cres.unsupported:
            unsupported.extend(cres.unsupported)
        index += 1
    if unsupported:
        print("Unsupported RCOL formats:")
        for rcol_type in unsupported:
            print("    %s" % str(rcol_type))
    return index

def getGroupResources(group, verbose=False):    
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices()
    packman.getGroupResources(group, verbose=verbose)

def dumpAllObjects(verbose=False):
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices()
    for group, name in packman.getAllObjects(verbose=verbose):
        print("0x%08x => %s" % (group, name))
        for res_desc in packman.GetRCOLsByGroup(group):
            ident = DecodeDescriptor(res_desc)
            print("%s(%x)" % (ident.type, ident.instance), end=', ')
        print("")

def findStupidCases(verbose=False):
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices()
    resources = packman.GetRCOLsByType(PackedFile.OBJD)
    stupid_cases = 0
    for item_desc in resources:
        ident = DecodeDescriptor(item_desc)
        objd = packman.getResource(item_desc)
        if objd.stupid_namelen:
            stupid_cases += 1
            print ("Stupid case - %s in file %s" % (str(ident), objd.dbpf.file))
    print("Total stupid cases: %d" % stupid_cases)

def spag():
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices(extract_namemaps=False, verbose=True, alert_identifier=0xffe69795)
    identifier = Identifier.from_tgir(0x4f424a44, 0x7f1cbcf8, 0x000041a8, 0x00000000)
    res = packman.getResource(identifier.get_descriptor(), verbose=True)
    #res.ResolveAllLinks(packman, verbose=True)
    res.dump()
#    for key, val in PackedFileType.RCOLDict.items():
#        print("%s => %s" % (key, val))
    
if __name__ == "__main__":
    if False:
        import cProfile
        cProfile.run('CheckAllCRES()', sort='time')
    else:
        #print ("Checked %d CRES files" % CheckAllCRES(starting_point=0))
        #getGroupResources(0x7fac04c8)
        #dumpAllObjects()
        findStupidCases()
        #spag()
    print("Done!")
