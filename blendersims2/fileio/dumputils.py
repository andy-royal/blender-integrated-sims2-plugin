#!/usr/bin/python3
#-*- coding: utf-8 -*-

def indented_print(indent, string):
    print('    ' * indent, end='')
    print(string)
    
def DumpName(string):
    if len(string) == 0:
        return "{None}"
    else:
        return string
