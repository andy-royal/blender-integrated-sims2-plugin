#!/usr/bin/python3
#-*- coding: utf-8 -*-

def crcTable24(byte, poly):
    curbyte = byte << 16
    for _ in range(8):
        if (curbyte & 0x800000) != 0:
            curbyte <<= 1
            curbyte ^= poly
        else:
            curbyte <<= 1
    return curbyte
    
def generic_crc24(inbytes, init, poly, inreflect, outreflect, final_xor):
    crc = init
    for byte in inbytes:
        if inreflect:
            curbyte = int('{:08b}'.format(byte)[::-1], 2)
        else:
            curbyte = byte
        pos = (crc ^ (curbyte << 16)) >> 16
        crc = ((crc << 8) ^ crcTable24(pos, poly)) & 0xffffff
    if outreflect:
        final_crc = int('{:024b}'.format(crc)[::-1], 2)
    else:
        final_crc = crc
    return final_crc ^ final_xor

def crcTable32(byte, poly):
    curbyte = byte << 24
    for _ in range(8):
        if (curbyte & 0x80000000) != 0:
            curbyte <<= 1
            curbyte ^= poly
        else:
            curbyte <<= 1
    return curbyte
    
def generic_crc32(inbytes, init, poly, inreflect, outreflect, final_xor):
    crc = init
    for byte in inbytes:
        if inreflect:
            curbyte = int('{:08b}'.format(byte)[::-1], 2)
        else:
            curbyte = byte
        pos = (crc ^ (curbyte << 24)) >> 24
        crc = ((crc << 8) ^ crcTable32(pos, poly)) & 0xffffffff
    if outreflect:
        final_crc = int('{:032b}'.format(crc)[::-1], 2)
    else:
        final_crc = crc
    return final_crc ^ final_xor

def sims2crc32(inbytes):
    return generic_crc32(inbytes, init=0xffffffff, poly=0x04c11db7, inreflect=False, outreflect=False, final_xor=0x00000000)
    
def standard_crc32(inbytes):
    return generic_crc32(inbytes, init=0xffffffff, poly=0x04c11db7, inreflect=True, outreflect=True, final_xor=0xffffffff)

def sims2crc24(inbytes):
    return generic_crc24(inbytes, init=0x00B704CE, poly=0x01864CFB, inreflect=False, outreflect=False, final_xor=0x00000000) | 0xFF000000
