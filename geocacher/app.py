#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Three files have very similar code pieces. They are:
#   * gcer
#   * gcer.py
#   * geocacher/app.py
# The reason for this is different environments with different needs.
# gcer is the main shell script to run for UNIX-type settings
# gcer.py is required for py2app (OSX Bundle Maker) to work
# geocacher/app.py is the main debug file in Wingware IDE, so that
#    breakpoints work properly (psyco stops the breakpoints from
#    working in Wingware IDE)
# As such, all three of these need to be kept in sync. Fortunately,
# there is extremely little logic in here. It's mostly a startup
# shell, so this bit of code can be mostly ignored. This note is
# just to explain why these pieces are here, and why all of them must
# be updated if one of them is.

import gettext
import os
import sys
import wx

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

basepath = module_path()
localedir = os.path.join(basepath, 'locale')
langid = wx.LANGUAGE_DEFAULT    # use OS default; or use LANGUAGE_JAPANESE, etc.
domain = "messages"             # the translation file is messages.mo
# Set locale for wxWidgets
mylocale = wx.Locale(langid)
mylocale.AddCatalogLookupPathPrefix(localedir)
mylocale.AddCatalog(domain)

# Set up Python's gettext
mytranslation = gettext.translation(domain, localedir,
    [mylocale.GetCanonicalName()], fallback = True)
mytranslation.install()

from geocacher.libs.xmldb import Geocacher
from geocacher.libs.db import Database

from geocacher.widgets.mainWindow import MainWindow

import geocacher.__version__
import geocacher

__version__ = geocacher.__version__.gcVERSION_NUMBER

class GeocacherApp (wx.App):
    '''
    Application Class
    '''
    def OnInit(self):
        '''
        Provides the additional initalisation needed for the application.
        '''
        self.checker = wx.SingleInstanceChecker(".Geocacher_"+wx.GetUserId())
        if self.checker.IsAnotherRunning():
            dlg = wx.MessageDialog(None,
                message=_("Geocacher is already running, please switch to that instance."),
                caption=_("Geocacher Already Running"),
                style=wx.CANCEL|wx.ICON_HAND)
            dlg.ShowModal()
            return False
        else:
            dirName = os.path.dirname(os.path.abspath(__file__))
            imageName = os.path.join(dirName, 'gfx', 'splash.png')
            image = wx.Image(imageName, wx.BITMAP_TYPE_PNG)
            bmp = image.ConvertToBitmap()
            wx.SplashScreen(bmp, wx.SPLASH_CENTER_ON_SCREEN |
                            wx.SPLASH_TIMEOUT, 5000, None,
                            wx.ID_ANY)
            wx.Yield()
            geocacher = Geocacher(True)
            xmldb = geocacher.db
            frame = MainWindow(None,-1, xmldb)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    def OnExit(self):
        pass

def main():
    app = GeocacherApp(redirect=False, useBestVisual=True)
    app.MainLoop()

if __name__ == "__main__":
    if not hasattr(sys, "frozen") and 'wx' not in sys.modules and 'wxPython' not in sys.modules:
        import wxversion
        wxversion.ensureMinimal("2.8")
    main()