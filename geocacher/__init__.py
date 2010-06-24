# -*- coding: UTF-8 -*-

import sys

if not hasattr(sys, "frozen") and 'wx' not in sys.modules and 'wxPython' not in sys.modules:
    import wxversion
    wxversion.ensureMinimal("2.8")
import wx

import geocacher.libs.config
import geocacher.libs.db

import __version__

version = __version__.gcVERSION_STRING
appname = 'Geocacher'
appdescription = "Application for Geocaching waypoint management"
appcopyright = 'Copyright 2009 Rob Wallace'
developers = ['Rob Wallace']
website = 'http://example.com'


def getLicense():
    return open("data/gpl.txt").read()

def config():
    return geocacher.libs.config.Config()

def db(debugging=False):
    return geocacher.libs.db.Database(debugging)

class InvalidID(Exception):
    pass