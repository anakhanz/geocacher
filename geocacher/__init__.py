# -*- coding: UTF-8 -*-
import gettext
import sys
import os

if not hasattr(sys, "frozen") and 'wx' not in sys.modules and 'wxPython' not in sys.modules:
    import wxversion
    wxversion.ensureMinimal("2.8")
import wx
import geocacher.libs.config
import geocacher.libs.db

MAJOR_VERSION   = 0 # major functionality change
MINOR_VERSION   = 1 # minor functionality change
BUILD_NUMBER    = 0 # problem/bug fix
STATUS          = 1 # 1 = alpha, 2 = beta, 3 = release candidate, 9 = final stable
VERSION_STRING  = u'%s.%s.%s.%s' % (MAJOR_VERSION,MINOR_VERSION,BUILD_NUMBER,
                                    STATUS)

VERSION_NUMBER  = u'%s.%s.%s' % (MAJOR_VERSION,MINOR_VERSION,BUILD_NUMBER)

version = VERSION_STRING
__version__ = VERSION_NUMBER

appname = 'Geocacher'
appdescription = "Application for Geocaching waypoint management"
appcopyright = 'Copyright 2009 Rob Wallace'
developers = ['Rob Wallace']
author = 'Rob Wallace'
authoremail = 'rob@wallace.gen.nz'
website = 'http://rnr.wallace.gen.nz/redmine/geocacher'

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

def getBasePath():
    return module_path()

def getLicense():
    return open("data/gpl.txt").read()

def config():
    return geocacher.libs.config.Config()

def db(debugging=False):
    return geocacher.libs.db.Database(False)

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
            self.SetupTanslation()
            from geocacher.widgets.mainWindow import MainWindow
            dirName = os.path.dirname(os.path.abspath(__file__))
            imageName = os.path.join(dirName, 'gfx', 'splash.png')
            image = wx.Image(imageName, wx.BITMAP_TYPE_PNG)
            bmp = image.ConvertToBitmap()
            wx.SplashScreen(bmp, wx.SPLASH_CENTER_ON_SCREEN |
                            wx.SPLASH_TIMEOUT, 5000, None,
                            wx.ID_ANY)
            wx.Yield()
            frame = MainWindow(None,-1)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    def SetupTanslation(self):
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

    def OnExit(self):
        pass

class InvalidID(Exception):
    pass