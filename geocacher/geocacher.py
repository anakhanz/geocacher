#!/usr/bin/env python
# -*- coding: UTF-8 -*-

debugLevel = 5
import logging
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

import wx
import wx.grid             as  gridlib
import wx.lib.gridmovers   as  gridmovers

#====
#import pygtk
#pygtk.require('2.0')
#====


#import gtk
import locale

#from libs.gladeapp import GladeApp
from libs.i18n import createGetText

# make translation available in the gui/gtk
#GladeApp.bindtextdomain("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

from libs.db import Geocacher
from libs.gpx import gpxLoad
from libs.loc import locLoad

#from libs.commongtk import InputBox, InputQuestion, MessageBox

#Simport gobject

try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"

##def myExceptHook(type, value, tb):
##    sys.__excepthook__(type, value, tb)
##    lines = traceback.format_exception(type, value, tb)
##    MessageBox(None,string.join(lines),title=_("Geocacher Error"))
##
##class Window(GladeApp):
##    glade=os.path.join(os.path.dirname(__file__), 'data/geocacher.glade')
##    window = "geocacherMain"
##
##    def init(self):
##        w = Geocacher.conf.common.mainWiidth or 700
##        h = Geocacher.conf.common.mainHeight or 500
##        self.main_widget.resize(w,h)
##        self.tsCaches = gtk.ListStore(str, str, str)
##
##        self.tvCaches=gtk.TreeView(self.tsCaches)
##
##        self.nameColumn = gtk.TreeViewColumn(_('Name'))
##        self.lonColumn = gtk.TreeViewColumn(_('Lon'))
##        self.latColumn = gtk.TreeViewColumn(_('Lat'))
##
##        self.tvCaches.append_column(self.nameColumn)
##        self.tvCaches.append_column(self.latColumn)
##        self.tvCaches.append_column(self.lonColumn)
##
##        self.cellTxt = gtk.CellRendererText()
##
##        self.nameColumn.pack_start(self.cellTxt, True)
##        self.lonColumn.pack_start(self.cellTxt, True)
##        self.latColumn.pack_start(self.cellTxt, True)
##
##        self.nameColumn.add_attribute(self.cellTxt, 'text', 0)
##        self.lonColumn.add_attribute(self.cellTxt, 'text', 1)
##        self.latColumn.add_attribute(self.cellTxt, 'text', 2)
##        self.nameColumn.set_reorderable(False)
##        self.lonColumn.set_reorderable(True)
##        self.latColumn.set_reorderable(True)
##
##        try:
##            self.tvCaches.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
##        except:
##            pass
##
##        self.swCaches.add(self.tvCaches)
##
##        self.swCaches.show_all()
##
##        self.reloadCaches()
##
##    def reloadCaches(self):
##        self.tsCaches.clear()
##        for cache in Geocacher.db.getCacheList():
##            self.addCache(cache)
##
##    def addCache(self, cache):
##        row = (cache.code,cache.lat,cache.lon)
##        self.tsCaches.append(row)
##
##    def on_miHelpAbout_activate(self,*args):
##        import Image
##        about = gtk.AboutDialog()
##        about.set_name('Geocacher')
##        about.set_version(__version__)
##        about.set_copyright('Copyright 2009 Rob Wallace')
##        about.set_license(open("data/gpl.txt").read())
##        about.set_authors(["Rob Wallace"])
##        about.set_website('http://example.com')
##        about.set_comments(
##"""Library Versions:
##Python: %d.%d.%d
##PyGTK: %d.%d.%d
##GTK: %d.%d.%d""" % (sys.version_info[:3] + gtk.pygtk_version + gtk.gtk_version))
##        def close(w, res):
##            if res == gtk.RESPONSE_CANCEL:
##                w.destroy()
##        about.connect("response", close)
##        #~ about.set_comments('handle your photos')
##        about.show()
##
##    def on_miLoadWpts_activate(self,*args):
##        # TODO: set file types
##        dialog = gtk.FileChooserDialog(_('Select source folder'),
##                self.main_widget,
##                gtk.FILE_CHOOSER_ACTION_OPEN,
##                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
##                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
##        dialog.set_default_response(gtk.RESPONSE_OK)
##        if os.path.isdir(Geocacher.conf.common.lastFolder):
##            dialog.set_current_folder(Geocacher.conf.common.lastFolder)
##        response = dialog.run()
##        if response == gtk.RESPONSE_OK:
##            Geocacher.conf.common.lastFolder = dialog.get_current_folder()
##            fileName = dialog.get_filename()
##            Geocacher.dbgPrint("Got file", 3)
##            if os.path.splitext(fileName)[1] == '.gpx':
##                gpxLoad(fileName,Geocacher.db,mode="replace")
##            elif os.path.splitext(fileName)[1] == '.loc':
##                Geocacher.db.loadLoc(fileName,mode="replace")
##            self.reloadCaches()
##        dialog.destroy()
##
##    def on_miPreferences_activate(self,widget,*args):
##        winPrefs = Preferences()
##        winPrefs.loop()
##        # TODO: force update of main window on preferences update
##
##    def on_miQuit_activate(self,widget,*args):
##        self.on_geocacherMain_delete_event(widget,*args)
##
##    def on_geocacherMain_delete_event(self,*args):
##        (Geocacher.conf.common.mainWiidth,Geocacher.conf.common.mainHeight) = self.main_widget.get_size()
##        Geocacher.conf.save()
##        Geocacher.db.save()
##        self.quit()
##
##class Preferences(GladeApp):
##    glade=os.path.join(os.path.dirname(__file__), 'data/geocacher.glade')
##    window = "preferences"
##
##    def init(self):
##        self.entUserName.set_text(Geocacher.conf.gc.userName)
##        self.entUserId.set_text(Geocacher.conf.gc.userId)
##
##    def on_butOk_clicked(self,widget,*args):
##        Geocacher.conf.gc.userName = self.entUserName.get_text()
##        Geocacher.conf.gc.userId = self.entUserId.get_text()
##        self.on_preferences_delete_event(widget,*args)
##
##    def on_butCancel_clicked(self,widget,*args):
##        self.on_preferences_delete_event(widget,*args)
##
##    def on_preferences_delete_event(self,*args):
##        self.quit()

def escape(str):
    # you can also use
    # from xml.sax.saxutils import escape
    # Caution: you have to escape '&' first!
    str = str.replace(u'&',u'&amp;')
    str = str.replace(u'<',u'&lt;')
    str = str.replace(u'>',u'&gt;')
    return str

class ImageRenderer(gridlib.PyGridCellRenderer):
    def __init__(self, table):
        gridlib.PyGridCellRenderer.__init__(self)
        self.table = table
        self._images = {}
        self._default = None

        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        if value not in self._images:
            logging.warn("Image not defined for '%s'" % value)
            value = self._default
        bmp = self._images[value]
        image = wx.MemoryDC()
        image.SelectObject(bmp)

        # clear the background
        dc.SetBackgroundMode(wx.SOLID)

        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)

        # copy the image but only to the size of the grid cell
        width, height = bmp.GetWidth(), bmp.GetHeight()

        if width > rect.width-2:
            width = rect.width-2

        if height > rect.height-2:
            height = rect.height-2

        dc.Blit(rect.x+1, rect.y+1, width, height,
                image,
                0, 0, wx.COPY, True)

class CacheSizeRenderer(ImageRenderer):
    def __init__(self, table):
        gridlib.PyGridCellRenderer.__init__(self)
        self.table = table
        self._images = {'Micro':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-micro.gif'), wx.BITMAP_TYPE_GIF),
                        'Small':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-small.gif'), wx.BITMAP_TYPE_GIF),
                        'Regular':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-regular.gif'), wx.BITMAP_TYPE_GIF),
                        'Large':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-large.gif'), wx.BITMAP_TYPE_GIF),
                        'Not chosen':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-not_chosen.gif'), wx.BITMAP_TYPE_GIF),
                        'Virtual':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-virtual.gif'), wx.BITMAP_TYPE_GIF),
                        'Other':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-other.gif'), wx.BITMAP_TYPE_GIF)}
        self._default='Other'

        self.colSize = None
        self.rowSize = None

class CacheTypeRenderer(ImageRenderer):
    def __init__(self, table):
        gridlib.PyGridCellRenderer.__init__(self)
        self.table = table
        self._images = {'Traditional Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-traditional.gif'), wx.BITMAP_TYPE_GIF),
                        'Ape':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-ape.gif'), wx.BITMAP_TYPE_GIF),
                        'CITO':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-cito.gif'), wx.BITMAP_TYPE_GIF),
                        'Earthcache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-earthcache.gif'), wx.BITMAP_TYPE_GIF),
                        'Event':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-event.gif'), wx.BITMAP_TYPE_GIF),
                        'Maze':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-gps_maze.gif'), wx.BITMAP_TYPE_GIF),
                        'Letterbox Hybrid':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-letterbox.gif'), wx.BITMAP_TYPE_GIF),
                        'Mega':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-mega.gif'), wx.BITMAP_TYPE_GIF),
                        'Multi-cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-multi-cache.gif'), wx.BITMAP_TYPE_GIF),
                        'Unknown Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-mystery.gif'), wx.BITMAP_TYPE_GIF),
                        'Reverse':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-reverse.gif'), wx.BITMAP_TYPE_GIF),
                        'Virtual Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-virtual.gif'), wx.BITMAP_TYPE_GIF),
                        'Webcam':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-webcam.gif'), wx.BITMAP_TYPE_GIF),
                        'WhereIGo':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-whereigo.gif'), wx.BITMAP_TYPE_GIF)
                        }
        self._default='Traditional Cache'

        self.colSize = None
        self.rowSize = None


##class CacheSizeRenderer(gridlib.PyGridCellRenderer):
##    def __init__(self, table):
##        gridlib.PyGridCellRenderer.__init__(self)
##        self.table = table
##        self._images = {'Micro':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-micro.gif'), wx.BITMAP_TYPE_GIF),
##                        'Small':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-small.gif'), wx.BITMAP_TYPE_GIF),
##                        'Regular':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-regular.gif'), wx.BITMAP_TYPE_GIF),
##                        'Large':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-large.gif'), wx.BITMAP_TYPE_GIF),
##                        'Not chosen':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-not_chosen.gif'), wx.BITMAP_TYPE_GIF),
##                        'Virtual':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-virtual.gif'), wx.BITMAP_TYPE_GIF),
##                        'Other':wx.Bitmap(os.path.join(os.path.dirname(__file__),'data','gfx','sz-other.gif'), wx.BITMAP_TYPE_GIF)}
##
##        self.colSize = None
##        self.rowSize = None
##
##    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
##        value = self.table.GetValue(row, col)
##        if value not in self._images:
##            value = 'Other'
##            log.warn("Cache Size '%s' not in known sizes" % value)
##        bmp = self._images[value]
##        image = wx.MemoryDC()
##        image.SelectObject(bmp)
##
##        # clear the background
##        dc.SetBackgroundMode(wx.SOLID)
##
##        if isSelected:
##            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
##            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
##        else:
##            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
##            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
##        dc.DrawRectangleRect(rect)
##
##        # copy the image but only to the size of the grid cell
##        width, height = bmp.GetWidth(), bmp.GetHeight()
##
##        if width > rect.width-2:
##            width = rect.width-2
##
##        if height > rect.height-2:
##            height = rect.height-2
##
##        dc.Blit(rect.x+1, rect.y+1, width, height,
##                image,
##                0, 0, wx.COPY, True)

class CacheDataTable(gridlib.PyGridTableBase):
    def __init__(self):
        gridlib.PyGridTableBase.__init__(self)

        self.identifiers = ['code','lon','lat','name','found','type','size']

        self.colLabels = {
            'code':_('Code'),
            'lon':_("Longitude"),
            'lat':_('Latitude'),
            'name':_('Name'),
            'found':_('Found By Me'),
            'type':_('Type'),
            'size':_('Size')}

        #sizeRenderer = CacheSizeRenderer(self)

        self.dataTypes = {
            'code':gridlib.GRID_VALUE_STRING,
            'lon':gridlib.GRID_VALUE_FLOAT + ':6,6',
            'lat':gridlib.GRID_VALUE_FLOAT + ':6,6',
            'name':gridlib.GRID_VALUE_STRING,
            'found':gridlib.GRID_VALUE_BOOL,
            'type':gridlib.GRID_VALUE_STRING,
            'size':gridlib.GRID_VALUE_STRING}

        self.renderers = {
            'size':CacheSizeRenderer,
            'type':CacheTypeRenderer}

        self.data = []

    def reloadCaches(self):
        oldNumRows=len(self.data)
        self.data = []
        grid = self.GetView()
        for cache in Geocacher.db.getCacheList():
            self.__addRow(cache)
        newNumRows=len(self.data)
        if newNumRows < oldNumRows:
            msg = wx.grid.GridTableMessage(
                self,                     # the table
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                newNumRows,               # position
                oldNumRows - newNumRows)  # how many
            grid.ProcessTableMessage(msg)

        elif newNumRows >  oldNumRows:
            msg = wx.grid.GridTableMessage(
                    self,                     # the table
                    wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                    newNumRows - oldNumRows)  # how many
            grid.ProcessTableMessage(msg)

        msg = wx.grid.GridTableMessage(
                self,
                wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)
        self._updateColAttrs(grid)

    def __addRow(self, cache):
        row = {'code':cache.code,'lon':cache.lon,'lat':cache.lat,
                'name':cache.name,'found':cache.found,'type':cache.type,
                'size':cache.container}
        self.data.append(row)

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.identifiers)

    def IsEmptyCell(self, row, col):
        id = self.identifiers[col]
        return not self.data[row][id]

    def GetValue(self, row, col):
        id = self.identifiers[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        id = self.identifiers[col]
        self.data[row][id] = value

    def GetColLabelValue(self, col):
        id = self.identifiers[col]
        return self.colLabels[id]

    def GetTypeName(self, row, col):
        id = self.identifiers[col]
        return self.dataTypes[id]

    def CanGetValueAs(self, row, col, typeName):
        id = self.identifiers[col]
        colType = self.dataTypes[id].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        id = self.identifiers[col]
        return self.CanGetValueAs(row, id, typeName)

    def MoveColumn(self,frm,to):
        grid = self.GetView()

        if grid:
            # Move the identifiers
            old = self.identifiers[frm]
            del self.identifiers[frm]

            if to > frm:
                self.identifiers.insert(to-1,old)
            else:
                self.identifiers.insert(to,old)

            # Notify the grid
            grid.BeginBatch()

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)

            grid.EndBatch()

    def _updateColAttrs(self, grid):
        """
        wx.Grid -> update the column attributes to add the
        appropriate renderer given the column name.  (renderers
        are stored in the self.plugins dictionary)

        Otherwise default to the default renderer.
        """
        col = 0

        for identifier in self.identifiers:
            attr = gridlib.GridCellAttr()
            if identifier in self.renderers:
                renderer = self.renderers[identifier](self)

                if renderer.colSize:
                    grid.SetColSize(col, renderer.colSize)

                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)

                attr.SetReadOnly(True)
                attr.SetRenderer(renderer)

            grid.SetColAttr(col, attr)
            col += 1

class CacheGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1)

        table = CacheDataTable()

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        table.reloadCaches()

        # Enable Column moving
        gridmovers.GridColMover(self)
        self.Bind(gridmovers.EVT_GRID_COL_MOVE, self.OnColMove, self)

        self.SetRowLabelSize(0)
        self.SetMargins(0,0)

    # Event method called when a column move needs to take place
    def OnColMove(self,evt):
        frm = evt.GetMoveColumn()       # Column being moved
        to = evt.GetBeforeColumn()      # Before which column to insert
        self.GetTable().MoveColumn(frm,to)

    # Event method called when a row move needs to take place
    def OnRowMove(self,evt):
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self.GetTable().MoveRow(frm,to)

    def reloadCaches(self):
        self.GetTable().reloadCaches()

class MainWindow(wx.Frame):
    """Main Frame holding the Panel."""
    def __init__(self,parent,id,title):
        """Create the main frame"""
        w = Geocacher.conf.common.mainWiidth or 700
        h = Geocacher.conf.common.mainHeight or 500
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size = (w,h),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        self.CreateStatusBar()

        # Build the menu bar
        MenuBar = wx.MenuBar()

        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_ANY, text=_("&Load Waypoints"))
        self.Bind(wx.EVT_MENU, self.OnLoadWpt, item)
        item = FileMenu.Append(wx.ID_EXIT, text=_("&Quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, item)


        MenuBar.Append(FileMenu, _("&File"))

        PrefsMenu = wx.Menu()

        item = PrefsMenu.Append(wx.ID_ANY, text=_("&Preferences"))
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        MenuBar.Append(PrefsMenu, _("&Edit"))

        HelpMenu = wx.Menu()

        item = HelpMenu.Append(wx.ID_ABOUT, text=_("&About"))
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, item)

        MenuBar.Append(HelpMenu, _("&Help"))

        self.SetMenuBar(MenuBar)

        self.cacheGrid = CacheGrid(self)

        self.Show(True)

    def OnHelpAbout(self, event=None):
        HelpAbout = wx.AboutDialogInfo()
        HelpAbout.SetName('Geocacher')
        HelpAbout.SetVersion(__version__)
        HelpAbout.SetCopyright(_('Copyright 2009 Rob Wallace'))
        HelpAbout.AddDeveloper('Rob Wallace')
        HelpAbout.SetLicense(open("data/gpl.txt").read())
        HelpAbout.SetWebSite('http://example.com')
        HelpAbout.SetDescription(_("Application for Geocaching waypoint management"))
        wx.AboutBox(HelpAbout)

    def OnLoadWpt(self, event=None):
        print "Loading waypoints"
        wildcard = "GPX File (*.gpx)|*.gpx|"\
                   "LOC file (*.loc)|*.loc|"\
                   "Compressed GPX File (*.zip)|*.zip|"\
                   "All files (*.*)|*.*"
        if os.path.isdir(Geocacher.conf.common.lastFolder):
            dir = Geocacher.conf.common.lastFolder
        else:
            dir = os.getcwd()
        dlg = wx.FileDialog(
            self, message=_("Choose a file to load"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE
            )

        if dlg.ShowModal() == wx.ID_OK:
            Geocacher.conf.common.lastFolder = dlg.GetDirectory()
            paths = dlg.GetPaths()
            for path in paths:
                if os.path.splitext(path)[1] == '.gpx':
                    gpxLoad(path,Geocacher.db,mode="replace",
                            userId=Geocacher.conf.gc.userId,
                            userName=Geocacher.conf.gc.userName)
                elif os.path.splitext(path)[1] == '.loc':
                    locLoad(path,Geocacher.db,mode="replace")
            self.cacheGrid.reloadCaches()

        dlg.Destroy()


    def OnPrefs(self, event=None):
        print "Editing preferences"

    def OnQuit(self, event=None):
        """Exit application."""
        (Geocacher.conf.common.mainWiidth,Geocacher.conf.common.mainHeight) = self.GetSizeTuple()
        Geocacher.conf.save()
        Geocacher.db.save()
        self.Destroy()


def main (debug, canModify):
    app = wx.PySimpleApp()
    locked = not Geocacher.lockOn()
    if locked:
        dlg = wx.MessageDialog(None,
                               message=_("Geocacher appears to already be running are you sure you wish to run another copy"),
                               caption=_("Geocacher Already Running"),
                               style=wx.YES_NO|wx.ICON_WARNING
                               )
        if dlg.ShowModal() == wx.ID_YES:
##        if InputQuestion (None,
##                _("Geocacher appears to already be running are you sure you wish to run another copy"),
##                title=_("Geocacher Already Running"),
##                buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK)):
            locked = False
    if not locked:
        try:
            #sys.excepthook = myExceptHook
            Geocacher.init(debug, canModify)

# TODO: Add icon
#            gtk.window_set_default_icon_from_file("data/gfx/ico.ico")
            #window = Window()

            #window.loop()

            frame = MainWindow(None,-1,"Geocacher")
            app.MainLoop()

        finally:
            Geocacher.lockOff()
    else:
        logging.warn(_('Geocacher appears to already be running, if not delete the file listed above.'))
        sys.exit(1)
USAGE = """%s [options]
Geocacher %s by Rob Wallace (c)2009, Licence GPL2
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
