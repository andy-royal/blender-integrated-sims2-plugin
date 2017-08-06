#!/usr/bin/python3
#-*- coding: utf-8 -*-

def ParseName(dg, verbose=False):
    if verbose:
        print ("Parsing name length")
    inbyte = dg.get_byte()
    i = 0
    name_len = 0
    while (inbyte & 0x80) != 0:
        name_len |= ((inbyte & 0x7F) << i)
        i += 7
        inbyte = dg.get_byte()
    name_len |= ((inbyte & 0x7F) << i)
    if verbose:
        print ("Parsing name of length %s" % name_len)
    res = dg.get_string(name_len)
    if verbose:
        print ("Extracted name: \"%s\"" % res)
    return res

def ParseBool(dg):
    raw = dg.get_byte()
    if raw == 1:
        return True
    elif raw == 0:
        return False
    else:
        raise ValueError("Expected bool, got %s" % format(raw, '#04x'))
