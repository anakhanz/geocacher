#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# TODO: Add export to GPS (using gpsBabel)
# TODO: Add selection of Current home location
# TODO: Add icon to main Window
# TODO: Add configuration of User Data Column names
# TODO: Add viewing of data that is not displayed in the table
# TODO: Add view only mode

from datetime import datetime
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
from libs.gpx import gpxLoad, gpxExport, zipLoad, zipExport
from libs.loc import locLoad, locExport
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
        ImageRenderer.__init__(self, table, conf)
        self._images = {'Micro':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-micro.gif'), wx.BITMAP_TYPE_GIF),
                        'Small':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-small.gif'), wx.BITMAP_TYPE_GIF),
                        'Regular':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-regular.gif'), wx.BITMAP_TYPE_GIF),
                        'Large':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-large.gif'), wx.BITMAP_TYPE_GIF),
                        'Not chosen':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-not_chosen.gif'), wx.BITMAP_TYPE_GIF),
                        'Virtual':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-virtual.gif'), wx.BITMAP_TYPE_GIF),
                        'Other':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-other.gif'), wx.BITMAP_TYPE_GIF)}
        self._default='Not chosen'

class CacheTypeRenderer(ImageRenderer):
    def __init__(self, table, conf):
        ImageRenderer.__init__(self, table, conf)
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
        # TODO: Add Travel Bugs to columns
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

    def ReloadRow(self, row):
        cache = self.GetRowCache(row)
        self.data.pop(row)
        self.data.insert(row, self.__buildRow(cache))

    def __addRow(self, cache):
        self.data.append(self.__buildRow(cache))

    def __buildRow(self, cache):

        location = self.db.getLocationByName(self.conf.common.currentLoc or 'Default')
        hLat = location.lat
        hLon = location.lon

        if self.conf.common.miles or False:
            dist = '%0.2f Mi' % distance(hLat,hLon,cache.currentLat,
                                         cache.currentLon,miles=True)
        else:
            dist = '%0.2f km' % distance(hLat,hLon,cache.currentLat,
                                         cache.currentLon,miles=True)
        cBear = cardinalBearing(hLat,hLon,cache.currentLat,cache.currentLon)

        row = {'code':cache.code,'id':cache.id,'lon':cache.currentLon,'lat':cache.currentLat,
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
        return row

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

    def GetRowCode(self, row):
        return self.data[row]['code']

    def GetRowCache(self, row):
        return self.db.getCacheByCode(self.GetRowCode(row))

    def GetRowCaches(self, rows):
        caches = []
        for row in rows:
            caches.append(self.GetRowCache(row))
        return caches

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
        toDelStr =""
        for row in rows:
            if toDelStr == "":
                toDelStr = self.data[row]['code']
            else:
                toDelStr = toDelStr + ', ' + self.data[row]['code']

        dlg = wx.MessageDialog(None,
                               message=_("Are you sure you wish to delete the following: ") + toDelStr,
                               caption=_("Geocacher Delete Caches?"),
                               style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            for row in rows:
                self.db.getCacheByCode(self.data[row]['code']).delete()
                self.data.pop(row-deleteCount)
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
        self.conf = conf
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

        self.SetRowLabelSize(20)
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
        '''(row, evt) -> display a popup menu when a row label is right clicked'''

        cache = self._table.GetRowCache(row)

        addID = wx.NewId()
        deleteID = wx.NewId()
        correctID = wx.NewId()
        rmCorrID = wx.NewId()
        x = self.GetRowSize(row)/2

        if not self.GetSelectedRows():
            self.SelectRow(row)

        menu = wx.Menu()
        xo, yo = evt.GetPosition()
        menu.Append(addID, _('Add Cache'))
        menu.Append(deleteID, _('Delete Cache(s)'))
        if cache.corrected:
            menu.Append(correctID, _('Edit Cordinate Correction'))
            menu.Append(rmCorrID, _('Remove Cordinate Correction'))
        else:
            menu.Append(correctID, _('Correct Cordinates'))

        def add(event, self=self, row=row):
            # TODO implement manually adding cache
            #self._table.AddCache(cache)
            #self.Reset()
            print "adding cache not yet implemented"

        def delete(event, self=self, row=row):
            rows = self.GetSelectedRows()
            self._table.DeleteRows(rows)
            self.Reset()

        def correct(event, self=self, row=row, cache=cache):
            self.SelectRow(row)
            dlg = CorrectLatLon(self, wx.ID_ANY,self._table.GetRowCache(row), self.conf)
            if dlg.ShowModal() == wx.ID_OK:
                self._table.ReloadRow(row)
                self.Reset()
            dlg.Destroy()

        def remCorrection(event, self=self, row=row, cache=cache):
            self.SelectRow(row)
            dlg = wx.MessageDialog(None,
                message=_('Are you sure you want to remove the cordinate correction for ')+cache.code,
                caption=_('Remove Cordinate Correction'),
                style=wx.YES_NO|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                cache.clat = 0.0
                cache.clon = 0.0
                cache.corrected = False
                cache.cnote = ''
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()

        self.Bind(wx.EVT_MENU, add, id=addID)
        self.Bind(wx.EVT_MENU, delete, id=deleteID)
        self.Bind(wx.EVT_MENU, correct, id=correctID)
        self.Bind(wx.EVT_MENU, remCorrection, id=rmCorrID)
        self.PopupMenu(menu)
        menu.Destroy()
        return

    def NumSelectedRows(self):
        return len(self.GetSelectedRows())

    def GetSelectedCaches(self):
        return self._table.GetRowCaches(self.GetSelectedRows())

    def ColPopup(self, col, evt):
        """(col, evt) -> display a popup menu when a column label is
        right clicked"""
        x = self.GetColSize(col)/2
        appMenu = wx.Menu()
        activeColNames = self._table.GetCols()
        colIds={}
        colDispName=[]
        for colName in self._table.GetAllCols():
            if colName not in activeColNames:
                colDispName.append([self._table.GetColLabelValueByName(colName), colName])
        colDispName.sort()
        for colDisp,colName in colDispName:
            colId = wx.NewId()
            colIds[colId]=colName
            appMenu.Append(colId, colDisp)
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
        self._prefs.gc.userName = self.gcUserName.GetValue()
        self._prefs.gc.userId = self.gcUserId.GetValue()
        self.Destroy()

class ExportOptions(wx.Dialog):
    '''Get the import options from the user'''
    def __init__(self,parent,id,type='simple',gc=False,logs=False,tbs=False,addWpts=False,sepAddWpts=True,zip=False):
        '''Creates the Preferences Frame'''
        wx.Dialog.__init__(self,parent,wx.ID_ANY,_('GPX File Export options'),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.zip = zip
        self.options = [[  'simple',    'full',    'custom'],
                        [_('Simple'), _('Full'), _('Custom')]]

        self.type= wx.RadioBox(self, wx.ID_ANY,
                                label=_("Export Type"),
                                choices = self.options[1],
                                style=wx.RA_VERTICAL)

        extsStaticBox = wx.StaticBox(self, wx.ID_ANY, 'Additional infromation')
        self.gc = wx.CheckBox(self, wx.ID_ANY, _('Geocaching.com Extensions'))

        self.logs = wx.CheckBox(self, wx.ID_ANY, _('Include Logs'))
        self.tbs = wx.CheckBox(self, wx.ID_ANY, _('Include Travel Bugs'))
        self.addWpts = wx.CheckBox(self, wx.ID_ANY, _('Include Additional Waypoints'))
        self.sepAddWpts = wx.CheckBox(self, wx.ID_ANY, _('Additioal Waypoints in seperate file'))

        extsBox = wx.StaticBoxSizer(extsStaticBox, wx.VERTICAL)
        extsBox.Add(self.logs,    0, wx.EXPAND, 5)
        extsBox.Add(self.tbs,     0, wx.EXPAND, 5)
        extsBox.Add(self.addWpts, 0, wx.EXPAND, 5)

        mainBox = wx.BoxSizer(orient=wx.VERTICAL)
        mainBox.Add(self.type, 0, wx.EXPAND)
        mainBox.Add(self.gc, 0, wx.EXPAND)
        mainBox.Add(extsBox, 0, wx.EXPAND, 15)
        mainBox.Add(self.sepAddWpts, 0, wx.EXPAND)

        # Ok and Cancel Buttons
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonBox = wx.StdDialogButtonSizer()
        buttonBox.AddButton(okButton)
        buttonBox.AddButton(cancelButton)
        buttonBox.Realize()

        self.Bind(wx.EVT_BUTTON,   self.OnExit,          okButton)
        self.Bind(wx.EVT_BUTTON,   self.OnExit,          cancelButton)
        self.Bind(wx.EVT_RADIOBOX, self.OnChangeType,    self.type)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleGc,      self.gc)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleAddWpts, self.addWpts)

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

        self.gc.Disable()
        self.logs.Disable()
        self.tbs.Disable()
        self.addWpts.Disable()
        self.sepAddWpts.Disable()
        if type == self.options[0][0]:
            self.type.SetSelection(0)
        elif type == self.options[0][1]:
            self.type.SetSelection(1)
            if zip:
                self.sepAddWpts.Enable()
                self.sepAddWpts.SetValue(sepAddWpts)
        else:
            self.type.SetSelection(2)
            self.gc.Enable()
            self.gc.SetValue(gc)
            if self.gc.GetValue():
                self.logs.Enable()
                self.logs.SetValue(logs)
                self.tbs.Enable()
                self.tbs.SetValue(tbs)
                self.addWpts.Enable()
                self.addWpts.SetValue(addWpts)
                if zip and self.addWpts.GetValue():
                    self.sepAddWpts.Enable()
                    self.sepAddWpts.SetValue(sepAddWpts)

    def OnChangeType(self, event=None):
        if self.type.GetSelection() == 2:
            self.gc.Enable()
        else:
            self.gc.SetValue(False)
            self.gc.Disable()
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()
            self.addWpts.SetValue(False)
            self.addWpts.Disable()
            if self.type.GetSelection() == 1 and self.zip:
                self.sepAddWpts.Enable()
            else:
                self.sepAddWpts.SetValue(False)
                self.sepAddWpts.Disable()

    def OnToggleGc(self, event=None):
        if self.gc.GetValue():
            self.logs.Enable()
            self.tbs.Enable()
            self.addWpts.Enable()
        else:
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()
            self.addWpts.SetValue(False)
            self.addWpts.Disable()
            self.sepAddWpts.SetValue(False)
            self.sepAddWpts.Disable()

    def OnToggleAddWpts(self, event=None):
        if self.zip and self.addWpts.GetValue():
            self.sepAddWpts.Enable()

    def OnExit(self, event=None):
        self.Destroy()
        wx.Dialog.EndModal(self, event.GetId())

    def GetType(self):
        return self.options[0][self.type.GetSelection()]

    def GetGc(self):
        return self.gc.GetValue()

    def GetLogs(self):
        return self.logs.GetValue()

    def GetTbs(self):
        return self.tbs.GetValue()

    def GetAddWpts(self):
        return self.addWpts.GetValue()

    def GetSepAddWpts(self):
        return self.sepAddWpts.GetValue()

class CorrectLatLon(wx.Dialog):
    '''Get the import options from the user'''
    def __init__(self,parent,id, cache, conf):
        """Creates the Preferences Frame"""
        self.cache = cache
        wx.Dialog.__init__(self,parent,id,_('Lat/Lon Correction for ')+cache.code,#size = (300,300),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.latName = wx.StaticText(self, wx.ID_ANY, _('Latitude'))
        self.lonName = wx.StaticText(self, wx.ID_ANY, _('Longitude'))
        self.origName = wx.StaticText(self, wx.ID_ANY, _('Origional'))
        self.corName = wx.StaticText(self, wx.ID_ANY, _('Corrected'))
        self.commName = wx.StaticText(self, wx.ID_ANY, _('Comment'))

        self.oLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1))
        self.oLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1))
        self.cLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1))# TODO: add validator
        self.cLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1))# TODO: add validator

        self.comment = wx.TextCtrl(self, wx.ID_ANY, size=(200, 100),
                                    style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)



        coordGrid = wx.GridBagSizer(3, 3)
        coordGrid.Add(self.latName, (0,1), (1,1), wx.ALL, 1)
        coordGrid.Add(self.lonName, (0,2), (1,1), wx.ALL, 1)
        coordGrid.Add(self.origName, (1,0), (1,1), wx.ALL, 1)
        coordGrid.Add(self.corName, (2,0), (1,1), wx.ALL, 1)

        coordGrid.Add(self.oLat, (1,1), (1,1), wx.ALL, 1)
        coordGrid.Add(self.oLon, (1,2), (1,1), wx.ALL, 1)
        coordGrid.Add(self.cLat, (2,1), (1,1), wx.ALL, 1)
        coordGrid.Add(self.cLon, (2,2), (1,1), wx.ALL, 1)

        coordSbox = wx.StaticBox(self, wx.ID_ANY, 'Cordinates')
        coordSboxSizer = wx.StaticBoxSizer(coordSbox, wx.VERTICAL)
        coordSboxSizer.Add(coordGrid, 0, 0, 0)

        mainBox = wx.BoxSizer(orient=wx.VERTICAL)
        mainBox.Add(coordSboxSizer)
        mainBox.Add(self.commName, 0, wx.EXPAND)
        mainBox.Add(self.comment, 0, wx.EXPAND)

        # Ok and Cancel Buttons
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonBox = wx.StdDialogButtonSizer()
        buttonBox.AddButton(okButton)
        buttonBox.AddButton(cancelButton)
        buttonBox.Realize()

        self.Bind(wx.EVT_BUTTON,   self.OnExit,          okButton)
        self.Bind(wx.EVT_BUTTON,   self.OnExit,          cancelButton)

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

        # Stop the orogional Lat/Lon values being edited
        self.oLat.SetEditable(False)
        self.oLon.SetEditable(False)

        # Load the values
        self.oLat.SetValue(str(cache.lat))
        self.oLon.SetValue(str(cache.lon))
        if cache.corrected:
            self.cLat.SetValue(str(cache.clat))
            self.cLon.SetValue(str(cache.clon))
            self.comment.SetValue(cache.cnote)

        self.Show(True)

    def OnExit(self, event=None):
        print 'Exit'
        if event.GetId() == wx.ID_OK:
            print 'OK'
            self.cache.clat = float(self.cLat.GetValue())
            self.cache.clon = float(self.cLon.GetValue())
            self.cache.corrected = True
            self.cache.cnote = self.comment.GetValue()
            self.cache.user_date = datetime.now()
        self.Destroy()
        wx.Dialog.EndModal(self, event.GetId())

class MainSplitter(wx.SplitterWindow):
    def __init__(self,parent,id):
        wx.SplitterWindow.__init__(self, parent, id,
            style=wx.SP_LIVE_UPDATE | wx.SP_BORDER)


class MainWindow(wx.Frame):
    """Main Frame"""
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

        self.buildMenu()

        self.splitter = MainSplitter(self, wx.ID_ANY)
        self.cacheGrid = CacheGrid(self.splitter, self.conf, self.db)
        panel2 = wx.Window(self.splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.cacheGrid, panel2, conf.common.mainSplit or 400)

        wx.StaticText(panel2, -1, "TestText", (5,5))


        self.Show(True)

    def buildMenu(self):
        '''Builds the menu'''
        MenuBar = wx.MenuBar()

        # Build file menu and bind functions
        FileMenu = wx.Menu()

        # TODO: add option to add folder of files (as seperate menu Item)
        item = FileMenu.Append(wx.ID_ANY, text=_("&Load Waypoints"))
        self.Bind(wx.EVT_MENU, self.OnLoadWpt, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Export Waypoints"))
        self.Bind(wx.EVT_MENU, self.OnExportWpt, item)

        item = FileMenu.Append(wx.ID_EXIT, text=_("&Quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, _("&File"))

        # Build preferences menu and bind functions
        PrefsMenu = wx.Menu()

        item = PrefsMenu.Append(wx.ID_ANY, text=_("&Preferences"))
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        MenuBar.Append(PrefsMenu, _("&Edit"))

        # Build Help menu and bind functions
        HelpMenu = wx.Menu()

        item = HelpMenu.Append(wx.ID_ABOUT, text=_("&About"))
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, item)

        MenuBar.Append(HelpMenu, _("&Help"))

        # Add the menu bar to the frame
        self.SetMenuBar(MenuBar)

    def selectCaches(self, scope, destText):
        options = [_('All'),_('Marked with User Flag')]
        if self.cacheGrid.NumSelectedRows() > 0:
            options += ([_('Selected'),_('Selected and marked with User Flag')])
            selection = True
        else:
            selection = False
        dlg = wx.SingleChoiceDialog(self, _('Export Option'),
                                    _('Caches to export to ') + destText,
                                    choices=options,
                                    style=wx.CHOICEDLG_STYLE)
        if scope == 'userFlag':
            dlg.SetSelection(1)
        elif scope == 'selection' and selection:
            dlg.SetSelection(2)
        elif scope == 'selection_userFlag' and selection:
            dlg.SetSelection(3)
        else:
            dlg.SetSelection(0)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetSelection() == 2:
                scope = 'selection'
                caches = self.cacheGrid.GetSelectedCaches()
            elif dlg.GetSelection() == 1 or dlg.GetSelection() == 3:
                if dlg.GetSelection() == 1:
                    scope = 'userFlag'
                    cachesTmp = self.db.getCacheList()
                else:
                    scope = 'selection_userFlag'
                    cachesTmp = self.cacheGrid.GetSelectedCaches()
                caches = []
                for cache in cachesTmp:
                    if cache.user_flag:
                        caches.append(cache)
            else:
                scope = 'all'
                caches = self.db.getCacheList()
            if len(caches) == 0:
                msg = wx.MessageDialog(self,
                    caption=_('No caches selected'),
                    message=_('No caches selected to export to ') + destText,
                    style=wx.OK | wx.ICON_HAND)
                msg.ShowModal()
                msg.Destroy()
                scope = None
                caches = None
        else:
            scope = None
            caches = None
        dlg.Destroy()
        return (scope, caches)

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
        # TODO: split file processing & import type selection from file selection
        wildcard = "GPX File (*.gpx)|*.gpx|"\
                   "LOC file (*.loc)|*.loc|"\
                   "Compressed GPX File (*.zip)|*.zip|"\
                   "All files (*.*)|*.*"

        if os.path.isdir(self.conf.load.lastFolder):
            dir = self.conf.load.lastFolder
        else:
            dir = os.getcwd()

        dlg = wx.FileDialog(
            self, message=_("Choose a file to load"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE
            )
        if os.path.isfile(self.conf.load.lastFile):
            dlg.SetPath(self.conf.load.lastFile)
        ext = os.path.splitext(self.conf.load.lastFile)[1]
        if ext != '':
            if ext == '.gpx':
                dlg.SetFilterIndex(0)
            elif ext == '.loc':
                dlg.SetFilterIndex(1)
            elif ext == '.zip':
                dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            self.conf.load.lastFolder = dlg.GetDirectory()
            paths = dlg.GetPaths()
            self.conf.load.lastFile = paths[0]
            options = [_('Update'),_('Replace')]
            dlg = wx.SingleChoiceDialog(self, _('Load option'),
                                        _('Type of file load'),
                                        choices=options,
                                        style=wx.CHOICEDLG_STYLE)
            if self.conf.load.type == 'replace':
                dlg.SetSelection(1)
            else:
                dlg.SetSelection(0)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    self.conf.load.type = 'update'
                else:
                    self.conf.load.type = 'replace'

                for path in paths:
                    if os.path.splitext(path)[1] == '.gpx':
                        gpxLoad(path,self.db,mode=self.conf.load.type,
                                userId=self.conf.gc.userId,
                                userName=self.conf.gc.userName)
                    elif os.path.splitext(path)[1] == '.loc':
                        locLoad(path,self.db,mode=self.conf.load.type)
                    elif os.path.splitext(path)[1] == '.zip':
                        zipLoad(path,self.db,mode=self.conf.load.type,
                                userId=self.conf.gc.userId,
                                userName=self.conf.gc.userName)
                self.cacheGrid.ReloadCaches()
            dlg.Destroy()

    def OnExportWpt(self, event=None):
        '''Function to export waypoints to a file'''

        (scope, caches) = self.selectCaches(self.conf.export.scope, _('file'))
        if scope == None:
            return

        wildcard = "GPX File (*.gpx)|*.gpx|"\
                   "LOC file (*.loc)|*.loc|"\
                   "Compressed GPX File (*.zip)|*.zip|"\

        if os.path.isdir(self.conf.export.lastFolder):
            dir = self.conf.export.lastFolder
        else:
            dir = os.getcwd()

        dlg = wx.FileDialog(
            self, message=_("Choose a file to export as"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.SAVE
            )
        if os.path.isfile(self.conf.export.lastFile):
            dlg.SetPath(self.conf.export.lastFile)
        ext = os.path.splitext(self.conf.export.lastFile)[1]
        if ext != '':
            if ext == '.gpx':
                dlg.SetFilterIndex(0)
            elif ext == '.loc':
                dlg.SetFilterIndex(1)
            elif ext == '.zip':
                dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            self.conf.export.lastFolder = dlg.GetDirectory()
            path = dlg.GetPath()
            if dlg.GetFilterIndex() == 0:
                ext = '.gpx'
                zip = False
            elif dlg.GetFilterIndex() == 1:
                ext = '.loc'
            elif dlg.GetFilterIndex() == 2:
                ext = '.zip'
                zip = True
            if os.path.splitext(path)[1] != ext:
                    path = path + ext

            if os.path.isfile(path):
                question = wx.MessageDialog(None,
                               message=path + _(" already exists are you sure you want to replace it ?"),
                               caption=_("File Already Exists"),
                               style=wx.YES_NO|wx.ICON_WARNING
                               )
                if question.ShowModal() == wx.ID_NO:
                    question.destroy()
                    return
            if ext == '.loc':
                locExport(path, caches)
            else:
                opts = ExportOptions(self, wx.ID_ANY,
                        type       = self.conf.export.type        or 'simple',
                        gc         = self.conf.export.gc          or False,
                        logs       = self.conf.export.logs        or False,
                        tbs        = self.conf.export.tbs         or False,
                        addWpts    = self.conf.export.addWpts     or False,
                        sepAddWpts = self.conf.export.sepAddWptsv or True,
                        zip = zip)
                if opts.ShowModal() ==wx.ID_OK:
                    if opts.GetType() == 'full':
                        full   = True
                        simple = False
                    elif opts.GetType() == 'simple':
                        full   = False
                        simple = True
                    else:
                        full   = False
                        simple = False
                    self.conf.export.lastFile = path
                    self.conf.export.type     = opts.GetType()
                    self.conf.export.gc       = opts.GetGc()
                    self.conf.export.logs     = opts.GetLogs()
                    self.conf.export.tbs      = opts.GetTbs()
                    self.conf.export.addWpts  = opts.GetAddWpts()

                    if ext == '.gpx':
                        gpxExport(path, caches,
                                        full       = full,
                                        simple     = simple,
                                        gc         = opts.GetGc(),
                                        logs       = opts.GetLogs(),
                                        tbs        = opts.GetTbs(),
                                        addWpts    = opts.GetAddWpts())
                    elif ext == '.zip':
                        self.conf.export.sepAddWpts = opts.GetSepAddWpts()
                        zipExport(path, caches,
                                        full       = full,
                                        simple     = simple,
                                        gc         = opts.GetGc(),
                                        logs       = opts.GetLogs(),
                                        tbs        = opts.GetTbs(),
                                        addWpts    = opts.GetAddWpts(),
                                        sepAddWpts = opts.GetSepAddWpts())
                opts.Destroy()
        dlg.Destroy()
        self.conf.export.scope = scope


    def OnPrefs(self, event=None):
        print "Editing preferences"
        prefsFrame = PreferencesWindow(self,wx.ID_ANY,self.conf)

    def OnQuit(self, event=None):
        """Exit application."""
        (self.conf.common.mainWiidth,self.conf.common.mainHeight) = self.GetSizeTuple()
        self.conf.common.mainSplit = self.splitter.GetSashPosition()
        self.conf.common.cacheCols = self.cacheGrid.GetCols()
        self.conf.common.sortCol = self.cacheGrid.GetSortCol()
        self.conf.save()
        self.db.save()
        self.Destroy()


def main (canModify):
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
            Geocacher.init(canModify)

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
        parser.add_option("-v","--view",action="store_true",dest="view",
                            help="run in only view mode")
        parser.set_defaults(viewOnly=False)

        (options, args) = parser.parse_args()

        main(not(options.viewOnly))

    except KeyboardInterrupt:
        pass
    sys.exit(0)
