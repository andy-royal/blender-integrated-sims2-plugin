#!/usr/bin/python3
#-*- coding: utf-8 -*-

class Version:
    """Sims 2 major/minor version"""
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __str__(self):
        return "%d.%d" % (self.major, self.minor)
