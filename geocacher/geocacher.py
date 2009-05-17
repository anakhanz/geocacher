#!/usr/bin/env python
# -*- coding: UTF-8 -*-

debugLevel = 10

import optparse
import os
import string
import sys
import time
import traceback

try:
    os.chdir(os.path.split(sys.argv[0])[0])
except:
    pass

#====
import pygtk
pygtk.require('2.0')
#====


import gtk
import locale

from libs.gladeapp import GladeApp
from libs.i18n import createGetText

# make translation available in the gui/gtk
GladeApp.bindtextdomain("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

from libs.db import Geocacher

from libs.commongtk import InputBox, InputQuestion, MessageBox

import gobject

try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"

def myExceptHook(type, value, tb):
    sys.__excepthook__(type, value, tb)
    lines = traceback.format_exception(type, value, tb)
    MessageBox(None,string.join(lines),title=_("Geocacher Error"))

class Window(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'data/geocacher.glade')
    window = "geocacherMain"

    def init(self):
        w = Geocacher.conf.common.mainWiidth or 700
        h = Geocacher.conf.common.mainHeight or 500
        self.main_widget.resize(w,h)
        self.tsCaches = gtk.ListStore(str, str, str)

        self.tvCaches=gtk.TreeView(self.tsCaches)

        self.nameColumn = gtk.TreeViewColumn(_('Name'))
        self.lonColumn = gtk.TreeViewColumn(_('Lon'))
        self.latColumn = gtk.TreeViewColumn(_('Lat'))

        self.tvCaches.append_column(self.nameColumn)
        self.tvCaches.append_column(self.latColumn)
        self.tvCaches.append_column(self.lonColumn)

        self.cellTxt = gtk.CellRendererText()

        self.nameColumn.pack_start(self.cellTxt, True)
        self.lonColumn.pack_start(self.cellTxt, True)
        self.latColumn.pack_start(self.cellTxt, True)

        self.nameColumn.add_attribute(self.cellTxt, 'text', 0)
        self.lonColumn.add_attribute(self.cellTxt, 'text', 1)
        self.latColumn.add_attribute(self.cellTxt, 'text', 2)
        self.nameColumn.set_reorderable(False)
        self.lonColumn.set_reorderable(True)
        self.latColumn.set_reorderable(True)


        # Gridlines commented out as libries shipped with current windows
        # jbrout pack do not support this, need new libs to enable.
        try:
            self.tvCaches.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        except:
            pass

        self.swCaches.add(self.tvCaches)

        self.swCaches.show_all()

        self.reloadCaches()

    def reloadCaches(self):
        self.tsCaches.clear()
        for cache in Geocacher.db.getCacheList():
            self.addCache(cache)

    def addCache(self, cache):
        #print cache
        self.tsCaches.append(cache)

    def on_miHelpAbout_activate(self,*args):
        import Image
        about = gtk.AboutDialog()
        about.set_name('Geocacher')
        about.set_version(__version__)
        about.set_copyright('Copyright 2009 Rob Wallace')
        about.set_license(open("data/gpl.txt").read())
        about.set_authors(["Rob Wallace"])
        about.set_website('http://example.com')
        about.set_comments(
"""Library Versions:
Python: %d.%d.%d
PyGTK: %d.%d.%d
GTK: %d.%d.%d""" % (sys.version_info[:3] + gtk.pygtk_version + gtk.gtk_version))
        def close(w, res):
            if res == gtk.RESPONSE_CANCEL:
                w.destroy()
        about.connect("response", close)
        #~ about.set_comments('handle your photos')
        about.show()

    def on_miLoadWpts_activate(self,*args):
        # TODO: save/load last dir used
        # TODO: set file types
        dialog = gtk.FileChooserDialog(_('Select source folder'),
                self.main_widget,
                gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        if os.path.isdir(Geocacher.conf.common.lastFolder):
            dialog.set_current_folder(Geocacher.conf.common.lastFolder)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            Geocacher.conf.common.lastFolder = dialog.get_current_folder()
            fileName = dialog.get_filename()
            Geocacher.dbgPrint("Got file", 3)
            if os.path.splitext(fileName)[1] == '.gpx':
                Geocacher.db.loadGpx(fileName,mode="replace")
            elif os.path.splitext(fileName)[1] == '.loc':
                Geocacher.db.loadLoc(fileName,mode="replace")
            self.reloadCaches()
        dialog.destroy()

    def on_miPreferences_activate(self,widget,*args):
        winPrefs = Preferences()
        winPrefs.loop()
        # TODO: force update of main window on preferences update

    def on_miQuit_activate(self,widget,*args):
        self.on_geocacherMain_delete_event(widget,*args)

    def on_geocacherMain_delete_event(self,*args):

        Geocacher.conf.save()
        Geocacher.db.save()
        self.quit()

class Preferences(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'data/geocacher.glade')
    window = "preferences"

    def init(self):
        self.entUserName.set_text(Geocacher.conf.gc.userName)
        self.entUserId.set_text(Geocacher.conf.gc.userId)

    def on_butOk_clicked(self,widget,*args):
        Geocacher.conf.gc.userName = self.entUserName.get_text()
        Geocacher.conf.gc.userId = self.entUserId.get_text()
        self.on_preferences_delete_event(widget,*args)

    def on_butCancel_clicked(self,widget,*args):
        self.on_preferences_delete_event(widget,*args)

    def on_preferences_delete_event(self,*args):
        self.quit()

def escape(str):
    # you can also use
    # from xml.sax.saxutils import escape
    # Caution: you have to escape '&' first!
    str = str.replace(u'&',u'&amp;')
    str = str.replace(u'<',u'&lt;')
    str = str.replace(u'>',u'&gt;')
    return str

def main (debug, canModify):
    locked = not Geocacher.lockOn()
    if locked:
        if InputQuestion (None,
                _("Geocacher appears to already be running are you sure you wish to run another copy"),
                title=_("Geocacher Already Running"),
                buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK)):
            locked = False
    if not locked:
        try:
            sys.excepthook = myExceptHook
            Geocacher.init(debug, canModify)

# TODO: Add icon
#            gtk.window_set_default_icon_from_file("data/gfx/ico.ico")
            window = Window()

            window.loop()
        finally:
            Geocacher.lockOff()
    else:
        print 'Geocacher appears to already be running, if not delete the file listed above.'
        sys.exit(1)
USAGE = """%s [options]
JBrout %s by Rob Wallace (c)2009, Licence GPL2
http://www.example.com""" % ("%prog",__version__)

if __name__ == "__main__":
    try:
        parser = optparse.OptionParser(usage=USAGE, version=("Geocaching "+__version__))
        parser.add_option("-d","--debug",action="store",type="int",dest="debug",
                            help="set debug level 0-9")
        parser.add_option("-v","--view",action="store_true",dest="view",
                            help="run in only view mode")
        parser.set_defaults(debug=debugLevel,viewOnly=False)

        (options, args) = parser.parse_args()

        main(options.debug, not(options.viewOnly))

    except KeyboardInterrupt:
        pass
    sys.exit(0)