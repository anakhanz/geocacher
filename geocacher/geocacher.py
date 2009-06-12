#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# TODO: Add GPX export
# TODO: Add geocaching.com zip file import (either loc or GPX)
# TODO: Add export to GPS (using gpsBabel)
# TODO: Add lat/lon correction tool
# TODO: Add selection of Current home location
# TODO: Add icon to main Window
# TODO: Add configuration of User Data Column names
# TODO: Add viewing of data that is not displayed in the table

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
import wx.grid             as  Grid
import wx.lib.gridmovers   as  Gridmovers

import locale

from libs.i18n import createGetText

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

from libs.db import Geocacher
from libs.gpx import gpxLoad
from libs.loc import locLoad
from libs.latlon import distance, cardinalBearing

try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"


class ImageRenderer(Grid.PyGridCellRenderer):
    def __init__(self, table, conf):
        Grid.PyGridCellRenderer.__init__(self)
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
    def __init__(self, table, conf):
        Grid.PyGridCellRenderer.__init__(self)
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
    def __init__(self, table, conf):
        Grid.PyGridCellRenderer.__init__(self)
        self.table = table
        self._images = {'Traditional Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-traditional.gif'), wx.BITMAP_TYPE_GIF),
                        'Ape':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-ape.gif'), wx.BITMAP_TYPE_GIF),
                        'CITO':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-cito.gif'), wx.BITMAP_TYPE_GIF),
                        'Earthcache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-earthcache.gif'), wx.BITMAP_TYPE_GIF),
                        'Event Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-event.gif'), wx.BITMAP_TYPE_GIF),
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

class CacheDataTable(Grid.PyGridTableBase):
    def __init__(self, conf, db):
        self.conf = conf
        self.db = db
        Grid.PyGridTableBase.__init__(self)

        self.colNames = self.conf.common.cacheCols or \
                           ['code','id','lat','lon','name','found','type',
                            'size','distance','bearing']

        # TODO: Add 'Number of logs' to table columns
        # TODO: Add 'Last Found' to table columns
        # TODO: Add 'Found Count' to table columns
        # TODO: Add 'Last Log Date' to table columns
        self.colLabels = {
            'code'        :_('Code'),
            'id'          :_('ID'),
            'lat'         :_('Latitude'),
            'lon'         :_("Longitude"),
            'name'        :_('Name'),
            'url'         :_('URL'),
            'found'       :_('Found By Me'),
            'type'        :_('Type'),
            'size'        :_('Size'),
            'distance'    :_('Distance'),
            'bearing'     :_('Bearing'),
            'oLat'        :_('Origional Latitude'),
            'oLon'        :_("Origional Longitude"),
            'cLat'        :_('Corrected Latitude'),
            'cLon'        :_("Corrected Longitude"),
            'corrected'   :_('Corrected Cordinates'),
            'available'   :_('Avaliable'),
            'archived'    :_('Archived'),
            'state'       :_('State'),
            'country'     :_('Country'),
            'owner'       :_('Owner'),
            'placedBy'    :_('Placed By'),
            'placed'      :_('Date Placed'),
            'user_date'   :_('Last User Update'),
            'gpx_date'    :_('Last GPX Update'),
            'locked'      :_('Locked'),
            'found'       :_('Found'),
            'found_date'  :_('Date Found'),
            'dnf'         :_('DNF'),
            'dnf_date'    :_('DNF Date'),
            'source'      :_('Source'),
            'user_flag'   :_('User Flag'),
            'user_data1'  :self.conf.common.userData1 or _('User Data 1'),
            'user_data2'  :self.conf.common.userData2 or _('User Data 2'),
            'user_data3'  :self.conf.common.userData3 or _('User Data 3'),
            'user_data4'  :self.conf.common.userData4 or _('User Data 4')}

        self.dataTypes = {
            'code'        :Grid.GRID_VALUE_STRING,
            'id'          :Grid.GRID_VALUE_STRING,
            'lat'         :Grid.GRID_VALUE_FLOAT + ':6,6',
            'lon'         :Grid.GRID_VALUE_FLOAT + ':6,6',
            'name'        :Grid.GRID_VALUE_STRING,
            'found'       :Grid.GRID_VALUE_BOOL,
            'type'        :Grid.GRID_VALUE_STRING,
            'size'        :Grid.GRID_VALUE_STRING,
            'distance'    :Grid.GRID_VALUE_STRING,
            'bearing'     :Grid.GRID_VALUE_STRING,
            'oLat'        :Grid.GRID_VALUE_FLOAT + ':6,6',
            'oLon'        :Grid.GRID_VALUE_FLOAT + ':6,6',
            'cLat'        :Grid.GRID_VALUE_FLOAT + ':6,6',
            'cLon'        :Grid.GRID_VALUE_FLOAT + ':6,6',
            'corrected'   :Grid.GRID_VALUE_BOOL,
            'available'   :Grid.GRID_VALUE_BOOL,
            'archived'    :Grid.GRID_VALUE_BOOL,
            'state'       :Grid.GRID_VALUE_STRING,
            'country'     :Grid.GRID_VALUE_STRING,
            'owner'       :Grid.GRID_VALUE_STRING,
            'placedBy'    :Grid.GRID_VALUE_STRING,
            'placed'      :Grid.GRID_VALUE_DATETIME,
            'user_date'   :Grid.GRID_VALUE_DATETIME,
            'gpx_date'    :Grid.GRID_VALUE_DATETIME,
            'locked'      :Grid.GRID_VALUE_BOOL,
            'found'       :Grid.GRID_VALUE_BOOL,
            'found_date'  :Grid.GRID_VALUE_DATETIME,
            'dnf'         :Grid.GRID_VALUE_BOOL,
            'dnf_date'    :Grid.GRID_VALUE_DATETIME,
            'source'      :Grid.GRID_VALUE_STRING,
            'user_flag'   :Grid.GRID_VALUE_BOOL,
            'user_data1'  :Grid.GRID_VALUE_STRING,
            'user_data2'  :Grid.GRID_VALUE_STRING,
            'user_data3'  :Grid.GRID_VALUE_STRING,
            'user_data4'  :Grid.GRID_VALUE_STRING}

        self.renderers = {
            'size'        :CacheSizeRenderer,
            'type'        :CacheTypeRenderer}

        self._sortCol = self.conf.common.sortCol or 'code'

        self.ReloadCaches()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def ReloadCaches(self):
        self.data = []
        for cache in Geocacher.db.getCacheList():
            self.__addRow(cache)
        self.DoSort()

    def __addRow(self, cache):
        # TODO: move cache correction logic into DB module
        if cache.corrected == True:
            lat = cache.cLat
            lon = cache.cLon
        else:
            lat = cache.lat
            lon = cache.lon

        location = self.db.getLocationByName(self.conf.common.currentLoc or 'Default')
        hLat = location.lat
        hLon = location.lon

        if self.conf.common.miles or False:
            dist = '%0.2f Mi' % distance(hLat,hLon,lat,lon,miles=True)
        else:
            dist = '%0.2f km' % distance(hLat,hLon,lat,lon)
        cBear = cardinalBearing(hLat,hLon,lat,lon)

        row = {'code':cache.code,'id':cache.id,'lon':lon,'lat':lat,
                'name':cache.name,'url':cache.url,'found':cache.found,
                'type':cache.type,'size':cache.container,'distance':dist,
                'bearing':cBear,'oLat':cache.lat,'oLon':cache.lon,
                'cLat':cache.clat,'cLon':cache.clon,'corrected':cache.corrected,
                'available':cache.available,'archived':cache.archived,
                'state':cache.state,'country':cache.country,
                'owner':cache.owner,'placedBy':cache.placed_by,'placed':cache.placed,
                'user_date':cache.user_date,'gpx_date':cache.gpx_date,
                'locked':cache.locked,'found':cache.found,'found_date':cache.found_date,
                'dnf':cache.dnf,'dnf_date':cache.dnf_date,'source':cache.source,
                'user_flag':cache.user_flag,'user_data1':cache.user_data1,
                'user_data2':cache.user_data2,'user_data3':cache.user_data3,
                'user_data4':cache.user_data4}
        self.data.append(row)

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colNames)

    def IsEmptyCell(self, row, col):
        id = self.colNames[col]
        return not self.data[row][id]

    def GetValue(self, row, col):
        id = self.colNames[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        id = self.colNames[col]
        self.data[row][id] = value

    def GetColLabelValue(self, col):
        id = self.colNames[col]
        return self.colLabels[id]

    def GetColLabelValueByName(self, name):
        return self.colLabels[name]

    def GetTypeName(self, row, col):
        id = self.colNames[col]
        return self.dataTypes[id]

    def CanGetValueAs(self, row, col, typeName):
        id = self.colNames[col]
        colType = self.dataTypes[id].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        id = self.cols[col]
        return self.CanGetValueAs(row, id, typeName)

    def AppendColumn(self,col):
        self.colNames.append(col)

    def InsertColumn(self,pos,col):
        self.colNames.insert(pos-1,col)

    def MoveColumn(self,frm,to):
        grid = self.GetView()

        if grid:
            # Move the cols
            old = self.colNames[frm]
            del self.colNames[frm]

            if to > frm:
                self.colNames.insert(to-1,old)
            else:
                self.colNames.insert(to,old)

            # Notify the grid
            grid.BeginBatch()

            msg = Grid.GridTableMessage(
                    self, Grid.GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)

            msg = Grid.GridTableMessage(
                    self, Grid.GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)

            grid.EndBatch()

    def DeleteCols(self, cols):
        """
        cols -> delete the columns from the dataset
        cols hold the column indices
        """
        # we'll cheat here and just remove the name from the
        # list of column names.  The data will remain but
        # it won't be shown
        deleteCount = 0
        cols = cols[:]
        cols.sort()

        for i in cols:
            self.colNames.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right columns
            deleteCount += 1

        if not len(self.colNames):
            self.data = []

    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = Grid.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = Grid.GridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # update the column rendering plugins
        self._updateColAttrs(grid)

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the dataset
        rows hold the row indices
        """
        deleteCount = 0
        rows = rows[:]
        rows.sort()

        for i in rows:
            self.data.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right rows
            deleteCount += 1

    def SortColumn(self, col):
        """
        col -> sort the data based on the column indexed by col
        """
        # TODO : Decending sort
        name = self.colNames[col]
        self._sortCol = self.colNames[col]
        self.DoSort()

    def DoSort(self):
        _data = []

        for row in self.data:
            _data.append((row.get(self._sortCol, None), row))

        _data.sort()
        self.data = []

        for sortvalue, row in _data:
            self.data.append(row)

    def _updateColAttrs(self, grid):
        """
        wx.Grid -> update the column attributes to add the
        appropriate renderer given the column name.  (renderers
        are stored in the self.plugins dictionary)

        Otherwise default to the default renderer.
        """
        colNum = 0

        for colName in self.colNames:
            attr = Grid.GridCellAttr()
            if colName in self.renderers:
                renderer = self.renderers[colName](self, self.conf)

                if renderer.colSize:
                    grid.SetColSize(colNum, renderer.colSize)

                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)

                attr.SetReadOnly(True)
                attr.SetRenderer(renderer)

            grid.SetColAttr(colNum, attr)
            colNum += 1

    def GetCols(self):
        return self.colNames

    def GetAllCols(self):
        return self.colLabels.keys()

    def GetSortCol(self):
        return self._sortCol

class CacheGrid(Grid.Grid):
    # TODO: add icon to Sorted Column Name
    def __init__(self, parent, conf, db):
        Grid.Grid.__init__(self, parent, -1)

        self._table = CacheDataTable(conf, db)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self._table, True)

        self._table.ReloadCaches()

        # Enable Column moving
        Gridmovers.GridColMover(self)
        self.Bind(Gridmovers.EVT_GRID_COL_MOVE, self.OnColMove, self)
        self.Bind(Grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClicked)

        self.SetRowLabelSize(10)
        self.SetMargins(0,0)
        self.Reset()

    # Event method called when a column move needs to take place
    def OnColMove(self,evt):
        frm = evt.GetMoveColumn()       # Column being moved
        to = evt.GetBeforeColumn()      # Before which column to insert
        self._table.MoveColumn(frm,to)
        self.Reset()

    # Event method called when a row move needs to take place
    def OnRowMove(self,evt):
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self._table.MoveRow(frm,to)

    def OnLabelRightClicked(self, evt):
        # Did we click on a row or a column?
        row, col = evt.GetRow(), evt.GetCol()
        if row == -1: self.ColPopup(col, evt)
        elif col == -1: self.RowPopup(row, evt)

    def RowPopup(self, row, evt):
        """(row, evt) -> display a popup menu when a row label is right clicked"""
        addID = wx.NewId()
        deleteID = wx.NewId()
        x = self.GetRowSize(row)/2

        if not self.GetSelectedRows():
            self.SelectRow(row)

        menu = wx.Menu()
        xo, yo = evt.GetPosition()
        menu.Append(addID, "Add Cache")
        menu.Append(deleteID, "Delete Cache(s)")

        def add(event, self=self, row=row):
            # TODO implement manually adding cache
            #self._table.AddCache(cache)
            #self.Reset()
            print "adding cache not yet implemented"

        def delete(event, self=self, row=row):
            rows = self.GetSelectedRows()
            self._table.DeleteRows(rows)
            self.reset()

        self.Bind(wx.EVT_MENU, add, id=appendID)
        self.Bind(wx.EVT_MENU, delete, id=deleteID)
        self.PopupMenu(menu)
        menu.Destroy()
        return


    def ColPopup(self, col, evt):
        """(col, evt) -> display a popup menu when a column label is
        right clicked"""
        x = self.GetColSize(col)/2
        appMenu = wx.Menu()
        activeColNames = self._table.GetCols()
        colIds={}
        for colName in self._table.GetAllCols():
            if colName not in activeColNames:
                colId = wx.NewId()
                colIds[colId]=colName
                appMenu.Append(colId, self._table.GetColLabelValueByName(colName))
        menu = wx.Menu()
        id1 = wx.NewId()
        sortID = wx.NewId()

        xo, yo = evt.GetPosition()
        self.SelectCol(col)
        colNames = self.GetSelectedCols()
        self.Refresh()
        menu.Append(id1, _("Delete Col(s)"))
        menu.Append(sortID, _("Sort Column"))
        menu.AppendMenu(wx.ID_ANY, _("Append Column"), appMenu)

        def delete(event, self=self, col=col):
            cols = self.GetSelectedCols()
            self._table.DeleteCols(cols)
            self.Reset()

        def sort(event, self=self, col=col):
            self._table.SortColumn(col)
            self.Reset()

        def append(event, self=self, colIds=colIds):
            print event.Id
            print colIds[event.Id]
            self._table.AppendColumn(colIds[event.Id])
            self.Reset()

        self.Bind(wx.EVT_MENU, delete, id=id1)

        if len(colNames) == 1:
            self.Bind(wx.EVT_MENU, sort, id=sortID)
        for colId in colIds:
            self.Bind(wx.EVT_MENU, append, id=colId)

        self.PopupMenu(menu)
        menu.Destroy()
        return

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self._table.ResetView(self)

    def ReloadCaches(self):
        self.GetTable().ReloadCaches()
        self.Reset()

    def GetCols(self):
        return self._table.GetCols()

    def GetSortCol(self):
        return self._table.GetSortCol()

class PreferencesWindow(wx.Frame):
    """Preferences Dialog"""
    # TODO: Add configuration of home locations
    def __init__(self,parent,id,prefs):
        """Creates the Preferences Frame"""
        self._prefs = prefs
        wx.Frame.__init__(self,parent,wx.ID_ANY,_("Preferences"),#size = (w,h),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        mainBox = wx.BoxSizer(orient=wx.VERTICAL)

        gcGrid = wx.FlexGridSizer(rows=2,cols=2)
        label = wx.StaticText(self,wx.ID_ANY,"User Name")
        gcGrid.Add(label, 0,wx.EXPAND)
        self.gcUserName = wx.TextCtrl(self,wx.ID_ANY,self._prefs.gc.userName)
        gcGrid.Add(self.gcUserName, 0,wx.EXPAND)
        label = wx.StaticText(self,wx.ID_ANY,"User ID")
        gcGrid.Add(label, 0,wx.EXPAND)
        self.gcUserId = wx.TextCtrl(self,wx.ID_ANY,self._prefs.gc.userId)
        gcGrid.Add(self.gcUserId, 0,wx.EXPAND)
        mainBox.Add(gcGrid, 0, wx.EXPAND)
        # Ok and Cancel Buttons
        okButton = wx.Button(self,wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnOk,okButton)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnCancel,cancelButton)
        buttonBox = wx.BoxSizer(orient=wx.HORIZONTAL)
        buttonBox.Add(okButton, 0, wx.EXPAND)
        buttonBox.Add(cancelButton, 0, wx.EXPAND)

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)


        self.Show(True)

    def OnCancel(self, event=None):
        self.Destroy()

    def OnOk(self, event=None):
        print "Ok"
        self._prefs.gc.userName = self.gcUserName.GetValue()
        self._prefs.gc.userId = self.gcUserId.GetValue()
        self.Destroy()

class MainWindow(wx.Frame):
    """Main Frame holding the Panel."""
    def __init__(self,parent,id, conf, db):
        """Create the main frame"""
        self.conf = conf
        self.db = db
        w = self.conf.common.mainWiidth or 700
        h = self.conf.common.mainHeight or 500
        wx.Frame.__init__(self,parent,wx.ID_ANY,_("Geocacher"),size = (w,h),
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

        self.cacheGrid = CacheGrid(self, self.conf, self.db)

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
        if os.path.isdir(self.conf.common.lastFolder):
            dir = self.conf.common.lastFolder
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
            self.conf.common.lastFolder = dlg.GetDirectory()
            paths = dlg.GetPaths()
            for path in paths:
                if os.path.splitext(path)[1] == '.gpx':
                    gpxLoad(path,self.db,mode="replace",
                            userId=self.conf.gc.userId,
                            userName=self.conf.gc.userName)
                elif os.path.splitext(path)[1] == '.loc':
                    locLoad(path,self.db,mode="replace")
            self.cacheGrid.ReloadCaches()

        dlg.Destroy()


    def OnPrefs(self, event=None):
        print "Editing preferences"
        prefsFrame = PreferencesWindow(self,wx.ID_ANY,self.conf)

    def OnQuit(self, event=None):
        """Exit application."""
        (self.conf.common.mainWiidth,self.conf.common.mainHeight) = self.GetSizeTuple()
        self.conf.common.cacheCols = self.cacheGrid.GetCols()
        self.conf.common.sortCol = self.cacheGrid.GetSortCol()
        self.conf.save()
        self.db.save()
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
            locked = False
    if not locked:
        try:
            Geocacher.init(debug, canModify)

            frame = MainWindow(None,-1,Geocacher.conf, Geocacher.db)
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
