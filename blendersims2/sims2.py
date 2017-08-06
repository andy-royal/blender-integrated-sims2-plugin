#!/usr/bin/python3
#-*- coding: utf-8 -*-

import winreg
import fnmatch
import os

from blendersims2.fileio.package import PackageManager
from blendersims2.fileio.tgir import Identifier, PackedFile, DecodeDescriptor

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

def CheckAllCRES(verbose=True, starting_point=0):
    
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
        cres = packman.GetRCOL(cres_descriptor)
        cres.ResolveAllLinks(packman)
        if cres.unsupported:
            unsupported.extend(cres.unsupported)
        index += 1
    if unsupported:
        print("Unsupported RCOL formats:")
        for rcol_type in unsupported:
            print("    %s" % str(rcol_type))
    return index

def spag():
    packman = PackageManager()
    AddSims2DirectoriesToPackageManager(packman)
    packman.ReadDBPFIndices(extract_namemaps=False, verbose=True, alert_identifier=0xffe69795)
    #packman.ReadDBPFIndices(extract_namemaps=True)
    #rcol = packman.GetRCOLByName(PackedFile.LGHTP, "cursorOnly_rig_key_plumbbob_lght")
#    identifier = Identifier.from_tgir(0xe519c933, 0x1c0532fa, 0xff7b1cc5, 0x00000000)
#    identifier = Identifier.from_tgir(0xe519c933, 0xffffffff, 0xffe69795, 0x00000000)
#    identifier = Identifier.from_tgir(0xe519c933, 0x7f32fc43, 0xff7046d5, 0x00000000)
#    identifier = Identifier.from_tgir(0xfc6eb1f7, 0xffffffff, 0xff1e4188, 0x00000000)
#    identifier = Identifier.from_tgir(0xe519c933, 0xffffffff, 0xffa25aec, 0x00000000)
#    identifier = Identifier.from_tgir(0xe519c933, 0x1c0532fa, 0xff09f942, 0xf8ee6a74)
    identifier = Identifier.from_tgir(0xe519c933, 0x1c0532fa, 0xff773c2c, 0x72d82f55)
    rcol = packman.GetRCOL(identifier.get_descriptor(), verbose=True)
    #rcol.dbpf.dump_index()
    rcol.ResolveAllLinks(packman, verbose=True)
    rcol.dump()
#    for key, val in PackedFileType.RCOLDict.items():
#        print("%s => %s" % (key, val))
    
if __name__ == "__main__":
    if False:
        import cProfile
        cProfile.run('CheckAllCRES()', sort='time')
    else:
        print ("Checked %d CRES files" % CheckAllCRES(starting_point=0))
        #spag()
    print("Done!")
