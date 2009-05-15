#!/usr/bin/env python
# -*- coding: UTF-8 -*-

debugLevel = 10

import optparse
import os
import string
import sys
import time
import traceback

from lxml import etree
from StringIO import StringIO

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
        pass # TODO: init main window

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
                loadGpx(fileName)
            #loadFile(dialog.get_filename())
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


def loadGpx(filename):
    NS = {'gpx': "http://www.topografix.com/GPX/1/0",
          'gs': "http://www.groundspeak.com/cache/1/0"}
    username = "anakhanz"
    userid = "1523158"
    
    if os.path.isfile(filename):
        file = open(filename, 'r')
        doc = etree.parse(file)
        file.close()
    else:
        doc = etree.parse(StringIO("<root>data</root>"))
            
    paths = doc.xpath('//gpx:gpx//gpx:wpt', namespaces=NS)
    i=0
    
    for path in paths:
        i+=1
        name = path.xpath('gpx:name', namespaces=NS)[0].text
        print "Name: %s" % name
        lat = path.attrib["lat"]
        lon = path.attrib["lon"]
        try:
            desc = path.xpath('gpx:desc', namespaces=NS)[0].text
        except:
            desc = ""
        
        Geocacher.db.addWpt(name,lat,lon,desc)
##        print "Time: %s" % path.xpath('gpx:time', namespaces=NS)[0].text
##        print "URL Name: %s URL: %s" % (path.xpath('gpx:urlname', namespaces=NS)[0].text,
##                                        path.xpath('gpx:url', namespaces=NS)[0].text)
##        print "Symbol: %s" % path.xpath('gpx:sym', namespaces=NS)[0].text
##        print "Type: %s" % path.xpath('gpx:type', namespaces=NS)[0].text
##        
##        cachedetail_list = path.xpath('gs:cache', namespaces=NS)
##        if not cachedetail_list == None:
##            cachedetail = cachedetail_list[0]
##            print "ID: %s Avaliable: %s Archived: %s" % (
##                cachedetail.attrib["id"],
##                cachedetail.attrib["available"],
##                cachedetail.attrib["archived"])
##            print "Placed By: %s" % cachedetail.xpath('gs:placed_by', namespaces=NS)[0].text
##            print "Owner: %s id: %s" % (cachedetail.xpath('gs:owner', namespaces=NS)[0].text,
##                                        cachedetail.xpath('gs:owner', namespaces=NS)[0].attrib["id"])
##            print "Type: %s" % cachedetail.xpath('gs:type', namespaces=NS)[0].text
##            print "Container: %s" % cachedetail.xpath('gs:container', namespaces=NS)[0].text
##            print "Difficulty: %s" % cachedetail.xpath('gs:difficulty', namespaces=NS)[0].text
##            print "Terrain: %s" % cachedetail.xpath('gs:terrain', namespaces=NS)[0].text
##            print "Country: %s" % cachedetail.xpath('gs:country', namespaces=NS)[0].text
##            print "State: %s" % cachedetail.xpath('gs:state', namespaces=NS)[0].text
##            try:
##                print "Short Description: %s" % cachedetail.xpath('gs:short_description', namespaces=NS)[0].text # attrib html
##            except:
##                print "Problem with Short description"
##            try:
##                print "Long Description: %s" % cachedetail.xpath('gs:long_description', namespaces=NS)[0].text # attrib html
##            except:
##                print "Problem with Long description"
##            try:
##                print "Encoded Hints: %s" % cachedetail.xpath('gs:encoded_hints', namespaces=NS)[0].text
##            except:
##                print "Problem with hint"
##                
##            # Deal with the log
##            for log in cachedetail.xpath('gs:logs//gs:log', namespaces=NS):
##                logFinder = log.xpath('gs:finder', namespaces=NS)[0]
##                if logFinder.attrib["id"]==userid or logFinder.text == username:
##                    print "matches"
        
        print i
        print
    print len(paths)

def loadLoc(filenane):
    pass

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