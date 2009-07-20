#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# TODO: Add icon to main Window
# TODO: Add view only mode

from datetime import datetime
import logging
import optparse
import os
import string
import sys
import time
import traceback
import tempfile

try:
    os.chdir(os.path.split(sys.argv[0])[0])
except:
    pass

import wx
import wx.grid             as  Grid
import wx.lib.gridmovers   as  Gridmovers
import wx.html

import locale

from libs.i18n import createGetText

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("geocaching",os.path.join(os.path.dirname(__file__), 'po'))

from libs.common import nl2br, listFiles, dateCmp
from libs.db import Geocacher
from libs.gpsbabel import GpsCom
from libs.gpx import gpxLoad, gpxExport, zipLoad, zipExport
from libs.loc import locLoad, locExport
from libs.latlon import distance, cardinalBearing
from libs.latlon import degToStr, strToDeg

try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"

class DegRenderer(Grid.PyGridCellRenderer):
    '''Renderer for cells containing measurements in degrees'''
    def __init__(self, table, conf, mode = 'pure'):
        Grid.PyGridCellRenderer.__init__(self)
        self.conf = conf
        self.table = table
        self.mode = mode

        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        #print value, self.mode, type(value)
        try: text = degToStr(value, format, self.mode)
        except: text = ''
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = grid.GetDefaultCellBackgroundColour()
            fg = grid.GetDefaultCellTextColour()

        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

    def GetBestSize(self, grid, attr, dc, row, col):
        value = self.table.GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        text = degToStr(value, format, self.mode)
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def clone(self):
        return DegRenderer(self.table, self.conf, self.mode)

class LatRenderer(DegRenderer):
    '''Renderer for cells containiny Latitudes (subcalss of DegRenderer)'''
    def __init__(self, table, conf):
        DegRenderer.__init__(self, table, conf, 'lat')

class LonRenderer(DegRenderer):
    '''Renderer for cells containiny Longitudes (subcalss of DegRenderer)'''
    def __init__(self, table, conf):
        DegRenderer.__init__(self, table, conf, 'lon')

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

class DegEditor(Grid.PyGridCellEditor):
    def __init__(self, conf, mode = 'pure'):
        Grid.PyGridCellEditor.__init__(self)
        self.conf = conf
        self.mode = mode

    def Create(self, parent, id, evtHandler):
        self.newValue = [0]

        self._tc = wx.TextCtrl(parent, id,'')
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)

        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        self._tc.SetValue(degToStr(self.startValue, format, self.mode))
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()
        self._tc.SetSelection(0, self._tc.GetLastPosition())

    def EndEdit(self, row, col, grid):
        changed = False

        value = strToDeg(self._tc.GetValue(), self.mode)

        if value != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, value)

        return changed

    def Reset(self):
        self._tc.SetValue(degToStr(self.startValue, format, self.mode))
        self._tc.SetInsertionPointEnd()

    def Clone(self):
        return DegEditor(conf, mode)

    def StartingKey(self, evt):
        self.OnChar(evt)
        if evt.GetSkipped():
            self._tc.EmulateKeyPress(evt)

class LatEditor(DegEditor):
    '''Editor for cells containiny Latitudes (subcalss of DegEditor)'''
    def __init__(self, conf):
        DegEditor.__init__(self, conf, 'lat')

class LonEditor(DegEditor):
    '''Editor for cells containiny Longitudes (subcalss of DegEditor)'''
    def __init__(self, conf):
        DegEditor.__init__(self, conf, 'lon')

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
            'num_logs'    :_('Number Of Logs'),
            'last_log'    :_('Last Log Date'),
            'last_found'  :_('Last Found'),
            'found_count' :_('Found Count'),
            'has_tb'      :_('Has Travel Bugs'),
            'locked'      :_('Locked'),
            'found'       :_('Found'),
            'found_date'  :_('Date Found'),
            'dnf'         :_('DNF'),
            'dnf_date'    :_('DNF Date'),
            'source'      :_('Source'),
            'user_flag'   :_('User Flag')}
        self.UpdateUserDataLabels()

        self.dataTypes = {
            'code'        :Grid.GRID_VALUE_STRING,
            'id'          :Grid.GRID_VALUE_STRING,
            'lat'         :Grid.GRID_VALUE_FLOAT + ':6,6',
            'lon'         :Grid.GRID_VALUE_FLOAT + ':6,6',
            'name'        :Grid.GRID_VALUE_STRING,
            'url'         :Grid.GRID_VALUE_STRING,
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
            'num_logs'    :Grid.GRID_VALUE_NUMBER,
            'last_log'    :Grid.GRID_VALUE_DATETIME,
            'last_found'  :Grid.GRID_VALUE_DATETIME,
            'found_count' :Grid.GRID_VALUE_NUMBER,
            'has_tb'      :Grid.GRID_VALUE_BOOL,
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
            'lat'         :LatRenderer,
            'lon'         :LonRenderer,
            'cLat'        :LatRenderer,
            'cLon'        :LonRenderer,
            'oLat'        :LatRenderer,
            'oLon'        :LonRenderer,
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
        if not self.__cacheFilter(cache):
            self.data.insert(row, self.__buildRow(cache))

    def __addRow(self, cache):
        if not self.__cacheFilter(cache):
            self.data.append(self.__buildRow(cache))

    def __buildRow(self, cache):

        dist, cBear = self.__calcDistBearing(cache)

        row = {'code':cache.code,'id':cache.id,'lon':cache.currentLon,'lat':cache.currentLat,
                'name':cache.name,'url':cache.url,'found':cache.found,
                'type':cache.type,'size':cache.container,'distance':dist,
                'bearing':cBear,'oLat':cache.lat,'oLon':cache.lon,
                'cLat':cache.clat,'cLon':cache.clon,'corrected':cache.corrected,
                'available':cache.available,'archived':cache.archived,
                'state':cache.state,'country':cache.country,
                'owner':cache.owner,'placedBy':cache.placed_by,'placed':cache.placed,
                'user_date':cache.user_date,'gpx_date':cache.gpx_date,
                'num_logs':cache.getNumLogs(),'last_log':cache.getLastLogDate(),
                'last_found':cache.getLastFound(),'found_count' :cache.getFoundCount(),
                'has_tb':cache.hasTravelBugs(),'locked':cache.locked,
                'found':cache.found,'found_date':cache.found_date,
                'dnf':cache.dnf,'dnf_date':cache.dnf_date,'source':cache.source,
                'user_flag':cache.user_flag,'user_data1':cache.user_data1,
                'user_data2':cache.user_data2,'user_data3':cache.user_data3,
                'user_data4':cache.user_data4}
        return row

    def __calcDistBearing(self, cache):
        '''
        Calculates the distance and cardinalBearing of the given cache and
        returns it as a tuple
        '''
        location = self.db.getLocationByName(self.conf.common.currentLoc or 'Default')
        hLat = location.lat
        hLon = location.lon

        if self.conf.common.miles or False:
            dist = '%0.2f Mi' % distance(hLat,hLon,cache.currentLat,
                                         cache.currentLon,miles=True)
        else:
            dist = '%0.2f km' % distance(hLat,hLon,cache.currentLat,
                                         cache.currentLon,miles=False)
        cBear = cardinalBearing(hLat,hLon,cache.currentLat,cache.currentLon)
        return dist, cBear

    def __cacheFilter(self, cache):
        mine = cache.owner == self.conf.gc.userName or\
               cache.owner_id == self.conf.gc.userId
        return (bool(self.conf.filter.archived) and cache.archived) or\
               (bool(self.conf.filter.disabled) and (not cache.available)) or\
               (bool(self.conf.filter.found) and cache.found) or\
               (bool(self.conf.filter.mine) and mine)

    def UpdateLocation(self):
        '''Updates the location based information in all cache rows'''
        for row in self.data:
            row['distance'], row['bearing'] = self.__calcDistBearing(self.db.getCacheByCode(row['code']))
        if self._sortCol in ['distance','bearing']:
            self.DoSort()

    def UpdateUserDataLabels(self):
        self.colLabels['user_data1'] = \
            self.conf.common.userData1 or _('User Data 1')
        self.colLabels['user_data2'] = \
            self.conf.common.userData2 or _('User Data 2')
        self.colLabels['user_data3'] = \
            self.conf.common.userData3 or _('User Data 3')
        self.colLabels['user_data4'] = \
            self.conf.common.userData4 or _('User Data 4')

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colNames)

    def IsEmptyCell(self, row, col):
        id = self.colNames[col]
        return self.data[row][id] is not None

    def GetValue(self, row, col):
        id = self.colNames[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        pass # leave this as pass until the editable elements are implemented
##        id = self.colNames[col]
##        self.data[row][id] = value

    def GetRowCode(self, row):
        return self.data[row]['code']

    def GetRowCache(self, row):
        return self.db.getCacheByCode(self.GetRowCode(row))

    def GetRowCaches(self, rows):
        caches = []
        for row in rows:
            caches.append(self.GetRowCache(row))
        return caches

    def GetRowLabelValue(self, row):
        return self.GetRowCode(row)

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
        if len(self.colNames) == 1:
            self.ReloadCaches()

    def InsertColumn(self,pos,col):
        self.colNames.insert(pos,col)

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
                self.db.getCacheByCode(self.data[row-deleteCount]['code']).delete()
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

    def SortDataItem(self, rowData):
        return rowData[self._sortCol]

    def DoSort(self):

        # Fix the comparison function for dates
        if self.dataTypes[self._sortCol] == Grid.GRID_VALUE_DATETIME:
            cmp = dateCmp
        else:
            cmp = None

        self.data.sort(cmp=cmp, key=self.SortDataItem)

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
    def __init__(self, parent, conf, db, mainWin):
        self.conf = conf
        self.mainWin = mainWin
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
        self.Bind(Grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClicked)
        self.Bind(Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClicked)

        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
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

    def OnLabelLeftClicked(self, evt):
        # Did we click on a row or a column?
        if evt.GetRow() != -1:
            self.mainWin.updateDetail(self._table.GetRowCode(evt.GetRow()))
        evt.Skip()

    def OnCellLeftClicked(self, evt):
        self.mainWin.updateDetail(self._table.GetRowCode(evt.GetRow()))
        evt.Skip()

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
            '''Delete the selected cache'''
            rows = self.GetSelectedRows()
            self._table.DeleteRows(rows)
            self.Reset()

        def correct(event, self=self, row=row, cache=cache):
            '''Add/Edit Correction of the Lat/Lon for the selected row'''
            self.SelectRow(row)
            cache = self._table.GetRowCache(row)
            # create data dictionary for the dialog and it's validators
            data = {'lat': cache.lat, 'lon': cache.lon,
                    'clat': cache.clat, 'clon': cache.clon,
                    'cnote': cache.cnote}
            dlg = CorrectLatLon(self, wx.ID_ANY, self.conf, cache.code, data,
                not cache.corrected)
            # show the dialog and update the cache if OK clicked and there
            # where changes
            if dlg.ShowModal() == wx.ID_OK and (data['clat'] != cache.clat or
                                                data['clon'] != cache.clon or
                                                data['cnote'] != cache.cnote):
                cache.clat = data['clat']
                cache.clon = data['clon']
                cache.cnote = data['cnote']
                cache.corrected = True
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()
            dlg.Destroy()

        def remCorrection(event, self=self, row=row, cache=cache):
            '''Remoce the Lat/Lon correction for the slected row'''
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
        activeColNames = self._table.GetCols()

        # Build a list mapping column display names to table cloum names
        colDispName=[]
        for colName in self._table.GetAllCols():
            if colName not in activeColNames:
                colDispName.append([self._table.GetColLabelValueByName(colName), colName])
        colDispName.sort()
        # build the append column menu and the dictionary mapping the ID of the
        # selected menu item to the table column name

        appMenu = wx.Menu()
        appColIds={}
        for colDisp,colName in colDispName:
            colId = wx.NewId()
            appColIds[colId]=colName
            appMenu.Append(colId, colDisp)

        # build the insert column menu and the dictionary mapping the ID of the
        # selected menu item to the table column name
        insMenu = wx.Menu()
        insColIds={}
        for colDisp,colName in colDispName:
            colId = wx.NewId()
            insColIds[colId]=colName
            insMenu.Append(colId, colDisp)
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
        menu.AppendMenu(wx.ID_ANY, _("Insert Column"), insMenu)

        def delete(event, self=self, col=col):
            cols = self.GetSelectedCols()
            self._table.DeleteCols(cols)
            self.Reset()

        def sort(event, self=self, col=col):
            self._table.SortColumn(col)
            self.Reset()

        def insert(event, self=self, colIds=insColIds, col=col):
            if col == -1:
                self._table.AppendColumn(colIds[event.Id])
            else:
                self._table.InsertColumn(col, colIds[event.Id])
            self.Reset()

        def append(event, self=self, colIds=appColIds):
            self._table.AppendColumn(colIds[event.Id])
            self.Reset()

        self.Bind(wx.EVT_MENU, delete, id=id1)

        if len(colNames) == 1:
            self.Bind(wx.EVT_MENU, sort, id=sortID)
        for colId in appColIds:
            self.Bind(wx.EVT_MENU, append, id=colId)
        for colId in insColIds:
            self.Bind(wx.EVT_MENU, insert, id=colId)


        self.PopupMenu(menu)
        menu.Destroy()
        return

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self._table.ResetView(self)
        # Use AutoSizeColumns() followed by AutoSizeRows() to avoid issues with
        # AutoSize() doing both and causing the splittter and scroll bars to
        # disapear
        self.AutoSizeColumns()
        self.AutoSizeRows()

    def ReloadCaches(self):
        self._table.ReloadCaches()
        self.Reset()

    def UpdateUserDataLabels(self):
        self._table.UpdateUserDataLabels()
        self.Reset()

    def UpdateLocation(self):
        self._table.UpdateLocation()
        self.Reset()

    def GetCols(self):
        return self._table.GetCols()

    def GetSortCol(self):
        return self._table.GetSortCol()

class PreferencesWindow(wx.Dialog):
    """Preferences Dialog"""
    def __init__(self,parent,id,conf, db):
        """Creates the Preferences Frame"""
        self.conf = conf
        self.db = db
        self.labelWidth = 150
        self.entryWidth = 200
        wx.Dialog.__init__(self,parent,wx.ID_ANY,_("Preferences"),size = (400,500),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        nb = wx.Notebook(self)

        # create the page windows as children of the notebook
        self.Display   = self.__buildDisplayPanel(nb)
        self.GC        = self.__buildGCPanel(nb)
        self.GPS       = self.__buildGpsPanel(nb)
        self.Locations = self.__buildLocationsPanel(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(self.Display,   _('Display'))
        nb.AddPage(self.GC,        _('Geocaching.Com'))
        nb.AddPage(self.GPS,        _('GPS'))
        nb.AddPage(self.Locations, _('Locations'))

        # Ok and Cancel Buttons
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)

        self.Bind(wx.EVT_BUTTON, self.OnOk,okButton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel,cancelButton)

        buttonBox = wx.BoxSizer(orient=wx.HORIZONTAL)
        buttonBox.Add(okButton, 0, wx.EXPAND)
        buttonBox.Add(cancelButton, 0, wx.EXPAND)

        # finally, put the notebook and buttons in a sizerto manage the layout
        mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        mainSizer.Add(nb, 1, wx.EXPAND)
        mainSizer.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainSizer)

    def __buildDisplayPanel(self, parent):
        panel = wx.Panel(parent, wx.ID_ANY)

        displayGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('Units'),
            size = (self.labelWidth,-1))
        displayGrid.Add(label, (0,0))
        self.dispUnitsChoices = [_('Kilometers'), _('Miles')]
        if self.conf.common.miles or False:
            value = self.dispUnitsChoices[1]
        else:
            value = self.dispUnitsChoices[0]
        self.dispUnits = wx.ComboBox(panel, wx.ID_ANY,
            value=value,
            choices=self.dispUnitsChoices,
            style=wx.CB_READONLY,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUnits, (0,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('Coordinate Format'))
        displayGrid.Add(label, (1,0))
        self.dispCoordFmt = wx.ComboBox(panel, wx.ID_ANY,
            value=self.conf.common.coordFmt or 'hdd mm.mmm',
            choices=['hdd.ddddd', 'hdd mm.mmm', 'hdd mm ss.s'],
            style=wx.CB_READONLY,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispCoordFmt, (1,1))

        label = wx.StaticText(panel,wx.ID_ANY,
            _('User Data Column Names'))
        displayGrid.Add(label, (2,0), (1,2))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 1'))
        displayGrid.Add(label, (3,0))
        self.dispUserData1 = wx.TextCtrl(panel, wx.ID_ANY,
            self.conf.common.userData1 or label.GetLabel(),
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData1, (3,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 2'))
        displayGrid.Add(label, (4,0))
        self.dispUserData2 = wx.TextCtrl(panel, wx.ID_ANY,
            self.conf.common.userData2 or label.GetLabel(),
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData2, (4,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 3'))
        displayGrid.Add(label, (5,0))
        self.dispUserData3 = wx.TextCtrl(panel, wx.ID_ANY,
            self.conf.common.userData3 or label.GetLabel(),
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData3, (5,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 4'))
        displayGrid.Add(label, (6,0))
        self.dispUserData4 = wx.TextCtrl(panel, wx.ID_ANY,
            self.conf.common.userData4 or label.GetLabel(),
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData4, (6,1))


        panel.SetSizer(displayGrid)
        return panel

    def __saveDisplayConf(self):
        if self.dispUnits.GetValue() == self.dispUnitsChoices[0]:
            self.conf.common.miles = False
        else:
            self.conf.common.miles = True
        self.conf.common.coordFmt = self.dispCoordFmt.GetValue()
        self.conf.common.userData1 = self.dispUserData1.GetValue()
        self.conf.common.userData2 = self.dispUserData2.GetValue()
        self.conf.common.userData3 = self.dispUserData3.GetValue()
        self.conf.common.userData4 = self.dispUserData4.GetValue()

    def __buildGCPanel(self, parent):
        panel = wx.Panel(parent, wx.ID_ANY)
        gcGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('User Name'),
            size = (self.labelWidth,-1))
        gcGrid.Add(label, (0,0))
        self.gcUserName = wx.TextCtrl(panel,
            wx.ID_ANY,self.conf.gc.userName or '',
            size = (self.entryWidth,-1))
        gcGrid.Add(self.gcUserName, (0,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User ID'))
        gcGrid.Add(label, (1,0))
        self.gcUserId = wx.TextCtrl(panel,wx.ID_ANY,
            self.conf.gc.userId or '',
            size = (self.entryWidth,-1))
        gcGrid.Add(self.gcUserId, (1,1))

        panel.SetSizer(gcGrid)
        return panel

    def __saveGCConf(self):
        self.conf.gc.userName = self.gcUserName.GetValue()
        self.conf.gc.userId = self.gcUserId.GetValue()

    def __buildGpsPanel(self,parent):
        panel = wx.Panel(parent, wx.ID_ANY)
        gpsGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('Type'),
            size = (self.labelWidth,-1))
        gpsGrid.Add(label, (0,0))
        self.gpsType = wx.ComboBox(panel, wx.ID_ANY,
            value=self.conf.gps.type or 'garmin',
            choices=['garmin'],
            style=wx.CB_SORT|wx.CB_READONLY,
            size = (self.entryWidth,-1))
        gpsGrid.Add(self.gpsType, (0,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('Port'))
        gpsGrid.Add(label, (1,0))
        self.gpsConnection = wx.ComboBox(panel, wx.ID_ANY,
            value=self.conf.gps.connection or 'usb:',
            choices=['usb:'],
            style=wx.CB_SORT,
            size = (self.entryWidth,-1))
        gpsGrid.Add(self.gpsConnection, (1,1))

        panel.SetSizer(gpsGrid)
        return panel

    def __saveGpsConf(self):
        self.conf.gps.type = self.gpsType.GetValue()
        self.conf.gps.connection = self.gpsConnection.GetValue()

    def __buildLocationsPanel(self, parent):
        grid = LocationsGrid(parent, self.conf, self.db)
        return grid

    def __saveLocationsConf(self):
        self.Locations.Save()

    def OnCancel(self, event=None):
        self.Destroy()

    def OnOk(self, event=None):
        self.__saveDisplayConf()
        self.__saveGCConf()
        self.__saveGpsConf()
        self.__saveLocationsConf()

        event.Skip()

class LocationsDataTable(Grid.PyGridTableBase):
    def __init__(self, conf, db):
        self.conf = conf
        self.db = db
        Grid.PyGridTableBase.__init__(self)
        self.colLabels = [_('Name'), _('Latitude'), _('Longitude')]
        self.renderers=[None, LatRenderer, LonRenderer]
        self.editors = [None, LatEditor, LonEditor]
        self.data = []
        locationNames = self.db.getLocationNameList()
        for locationName in locationNames:
            location = self.db.getLocationByName(locationName)
            self.data.append([location.name, location.lat, location.lon])

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def Save(self):
        existingNames = self.db.getLocationNameList()
        newNames = self.GetNames()
        for row in self.data:
            if row[0] in existingNames:
                location = self.db.getLocationByName(row[0])
                location.lat = row[1]
                location.lon = row[2]
            else:
                self.db.addLocation(row[0], row[1], row[2])
        for name in existingNames:
            if name not in newNames:
                location = self.db.getLocationByName(name)
                location.delete()
        if (self.conf.common.currentLoc or 'Default') not in newNames:
            self.conf.common.currentLoc = newNames[0]

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
                toDelStr = self.data[row][0]
            else:
                toDelStr = toDelStr + ', ' + self.data[row][0]

        dlg = wx.MessageDialog(None,
                               message=_("Are you sure you wish to delete the following: ") + toDelStr,
                               caption=_("Geocacher Delete Caches?"),
                               style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            for row in rows:
                self.data.pop(row-deleteCount)
                # we need to advance the delete count
                # to make sure we delete the right rows
                deleteCount += 1

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return 3

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        otherLocations = []
        for i in range(len(self.data)):
            if i != row:
                otherLocations.append(self.data[i][0])
        if col in [1,2] and value == None:
            message = _('The active cell must be in one of the following formats:')
            if col == 1:
                message = message + '''
    N12 34.345
    S12 34 45.6
    S12.34567
    -12.34567'''
            elif col == 2:
                message = message + '''
    E12 34.345
    W12 34 45.6
    W12.34567
    -12.34567'''
            wx.MessageBox(message, _('Input Error'))
        elif col == 0 and value == '':
            wx.MessageBox(_('The Location name must not be empty'),
                          _('Input Error'))
        elif col == 0 and value in otherLocations:
            wx.MessageBox(_('Each location must have a different name'),
                          _('Input Error'))
        else:
            self.data[row][col] = value

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return ''

    def AddRow(self, data):
        self.data.append(data)
        self.data.sort()

    def GetNames(self):
        names = []
        for row in self.data:
            names.append(row[0])
        names.sort()
        return names

    def ReplaceRow(self, row, data):
        self.data.pop(row)
        self.AddRow(data)

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

    def _updateColAttrs(self, grid):
        """
        wx.Grid -> update the column attributes to add the
        appropriate renderer given the column name.
        """
        for col in range(len(self.colLabels)):
            attr = Grid.GridCellAttr()
            if self.renderers[col] != None:
                renderer = self.renderers[col](self, self.conf)
                attr.SetRenderer(renderer)

                if renderer.colSize:
                    grid.SetColSize(col, renderer.colSize)

                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)

            if self.editors[col] != None:
                attr.SetEditor(self.editors[col](self.conf))

            grid.SetColAttr(col, attr)

class LocationsGrid(Grid.Grid):
    def __init__(self, parent, conf, db):
        self.conf = conf
        Grid.Grid.__init__(self, parent, wx.ID_ANY)

        self._table = LocationsDataTable(conf, db)

        self.SetTable(self._table, True)
        self.Bind(Grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnRightClicked)
        self.Bind(Grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClicked)

        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.SetMargins(0,0)

        self.Reset()

    def Save(self):
        self._table.Save()

    def OnRightClicked(self, evt):
        # Did we click on a row or a column?
        row = evt.GetRow()
        if row != -1:
            self.SelectRow(row)

        addID = wx.NewId()
        editID = wx.NewId()
        deleteID = wx.NewId()
        x = self.GetRowSize(row)/2

        menu = wx.Menu()
        xo, yo = evt.GetPosition()
        menu.Append(addID, _('Add Location'))
        if row != -1:
            menu.Append(editID, _('Edit Location'))
            if self._table.GetNumberRows() > 1:
                menu.Append(deleteID, _('Delete Location'))

        def add(event, self=self, row=row):
            name = self._table.GetValue(row,0)
            data = {'name':'',
                    'lat' :0,
                    'lon' :0}
            names = self._table.GetNames()
            dlg = EditLocation(self, wx.ID_ANY, self.conf, data, names, True)
            if dlg.ShowModal() == wx.ID_OK:
                self._table.AddRow([data['name'], data['lat'], data['lon']])
                self.Reset()

        def edit(event, self=self, row=row):
            data = {'name':self._table.GetValue(row,0),
                    'lat' :self._table.GetValue(row,1),
                    'lon' :self._table.GetValue(row,2)}
            names = self._table.GetNames()
            dlg = EditLocation(self, wx.ID_ANY, self.conf, data, names, False)
            if dlg.ShowModal() == wx.ID_OK:
                self._table.ReplaceRow(row,
                                       [data['name'], data['lat'], data['lon']])
                self.Reset()

        def delete(event, self=self, row=row):
            '''Delete the selected cache'''
            rows = self.GetSelectedRows()
            self._table.DeleteRows(rows)
            self.Reset()

        self.Bind(wx.EVT_MENU, add, id=addID)
        self.Bind(wx.EVT_MENU, edit, id=editID)
        self.Bind(wx.EVT_MENU, delete, id=deleteID)
        self.PopupMenu(menu)
        menu.Destroy()
        return

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self._table.ResetView(self)
        # Use AutoSizeColumns() followed by AutoSizeRows() to avoid issues with
        # AutoSize() doing both and causing the splittter and scroll bars to
        # disapear
        self.AutoSizeColumns()
        self.AutoSizeRows()

class EditLocation(wx.Dialog):
    '''Add/Edit a new location'''
    def __init__(self,parent,id, conf, data, names, new):
        '''Creates the Add/Edit Location Frame'''
        if new:
            caption = _('Add New Location')
        else:
            caption = _('Edit location ')+ data['name']
        wx.Dialog.__init__(self,parent,id,
            caption,size = (400,90),
           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create labels for controls
        nameName = wx.StaticText(self, wx.ID_ANY, _('Name'), size=(80,-1))
        latName = wx.StaticText(self, wx.ID_ANY, _('Latitude'), size=(80,-1))
        lonName = wx.StaticText(self, wx.ID_ANY, _('Longitude'), size=(80,-1))

        # Create controls
        name = wx.TextCtrl(self, wx.ID_ANY, size=(290, -1),
            #style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            validator=LocNameValidator(data, 'name', names))
        lat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LatValidator(conf, data, 'lat', new))
        lon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(conf, data, 'lon', new))

        # Create Grid for coordinate information and add the controls
        detailGrid = wx.GridBagSizer(3, 3)
        detailGrid.Add(nameName, (0,0), (1,1), wx.ALL, 1)
        detailGrid.Add(name, (0,1), (1,3), wx.ALL, 1)
        detailGrid.Add(latName, (1,0), (1,1), wx.ALL, 1)
        detailGrid.Add(lat, (1,1), (1,1), wx.ALL, 1)
        detailGrid.Add(lonName, (1,2), (1,1), wx.ALL, 1)
        detailGrid.Add(lon, (1,3), (1,1), wx.ALL, 1)

        # place the Location information in the vertical box
        mainBox = wx.BoxSizer(orient=wx.VERTICAL)
        mainBox.Add(detailGrid)

        # Ok and Cancel Buttons to the bottom of the form
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonBox = wx.StdDialogButtonSizer()
        buttonBox.AddButton(okButton)
        buttonBox.AddButton(cancelButton)
        buttonBox.Realize()

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

        self.Show(True)

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

class NotEmptyValidator(wx.PyValidator):
    def __init__(self, data, key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key

    def Clone(self):
        return NotEmptyValidator(self.data, self.key)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if len(text) == 0:
            textCtrl.SetBackgroundColour('pink')
            message = _('The highlighted field must contain some text!')
            wx.MessageBox(message, _('Input Error'))
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        textCtrl.SetValue(self.data.get(self.key, ""))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = textCtrl.GetValue()
        return True

class LocNameValidator(wx.PyValidator):
    def __init__(self, data, key, names):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key
        self.names = names

    def Clone(self):
        return LocNameValidator(self.data, self.key, self.names)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        ok = False
        if len(text) == 0:
            message = _('The Location Name field must not be empty')
        elif text != self.data[self.key] and text in self.names:
            message = _('The Location Name can not be the same as another Location Name')
        else:
            ok = True
        if ok:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True
        else:
            textCtrl.SetBackgroundColour('pink')
            wx.MessageBox(message, _('Input Error'))
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        textCtrl.SetValue(self.data.get(self.key, ""))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = textCtrl.GetValue()
        return True

class DegValidator(wx.PyValidator):
    def __init__(self, mode, conf, data, key, new=False):
        wx.PyValidator.__init__(self)
        self.mode = mode
        self.conf = conf
        self.data = data
        self.key = key
        self.new = new

    def Clone(self):
        return DegValidator(self.mode, self.conf , self.data, self.key, self.new)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        if strToDeg(textCtrl.GetValue(), self.mode) == None:
            textCtrl.SetBackgroundColour('pink')
            message = _('The highlighted field must be in one of the following formats:')
            if self.mode == 'lat':
                message = message + '''
    N12 34.345
    S12 34 45.6
    S12.34567
    -12.34567'''
            elif self.mode == 'lon':
                message = message + '''
    E12 34.345
    W12 34 45.6
    W12.34567
    -12.34567'''
            else:
                message = message + '''
    12 34.345
    12 34 45.6
    12.34567'''
            wx.MessageBox(message, _('Input Error'))
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        value = self.data.get(self.key, 0)
        if self.new:
            textCtrl.SetValue('')
        else:
            format = self.conf.common.coordFmt or 'hdd mm.mmm'
            textCtrl.SetValue(degToStr(value, format, self.mode))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = strToDeg(textCtrl.GetValue(), self.mode)
        return True

class LatValidator(DegValidator):
    def __init__(self, conf, data, key, new=False):
        DegValidator.__init__(self, 'lat', conf, data, key, new)

class LonValidator(DegValidator):
    def __init__(self, conf, data, key, new=False):
        DegValidator.__init__(self, 'lon', conf, data, key, new)

class CorrectLatLon(wx.Dialog):
    '''Get the import options from the user'''
    def __init__(self,parent,id, conf, code, data, new):
        '''Creates the Lat/Lon correction Frame'''
        wx.Dialog.__init__(self,parent,id,
            _('Lat/Lon Correction for ')+code,#size = (300,300),
           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create labels for controls
        latName = wx.StaticText(self, wx.ID_ANY, _('Latitude'))
        lonName = wx.StaticText(self, wx.ID_ANY, _('Longitude'))
        origName = wx.StaticText(self, wx.ID_ANY, _('Origional'))
        corName = wx.StaticText(self, wx.ID_ANY, _('Corrected'))
        commName = wx.StaticText(self, wx.ID_ANY, _('Comment'))

        # Create controls
        oLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LatValidator(conf, data, 'lat'))
        oLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(conf, data, 'lon'))
        cLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LatValidator(conf, data, 'clat', new))
        cLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(conf, data, 'clon', new))

        comment = wx.TextCtrl(self, wx.ID_ANY, size=(200, 100),
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            validator=NotEmptyValidator(data, 'cnote'))

        # Create Grid for coordinate information and add the controls
        coordGrid = wx.GridBagSizer(3, 3)
        coordGrid.Add(latName, (0,1), (1,1), wx.ALL, 1)
        coordGrid.Add(lonName, (0,2), (1,1), wx.ALL, 1)
        coordGrid.Add(origName, (1,0), (1,1), wx.ALL, 1)
        coordGrid.Add(corName, (2,0), (1,1), wx.ALL, 1)

        coordGrid.Add(oLat, (1,1), (1,1), wx.ALL, 1)
        coordGrid.Add(oLon, (1,2), (1,1), wx.ALL, 1)
        coordGrid.Add(cLat, (2,1), (1,1), wx.ALL, 1)
        coordGrid.Add(cLon, (2,2), (1,1), wx.ALL, 1)

        # Put a box around the coordinates section
        coordSbox = wx.StaticBox(self, wx.ID_ANY, _('Coordinates'))
        coordSboxSizer = wx.StaticBoxSizer(coordSbox, wx.VERTICAL)
        coordSboxSizer.Add(coordGrid, 0, 0, 0)

        # place the coordinates section and th ecomment in the vertical box
        mainBox = wx.BoxSizer(orient=wx.VERTICAL)
        mainBox.Add(coordSboxSizer)
        mainBox.Add(commName, 0, wx.EXPAND)
        mainBox.Add(comment, 0, wx.EXPAND)

        # Ok and Cancel Buttons to the bottom of the form
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonBox = wx.StdDialogButtonSizer()
        buttonBox.AddButton(okButton)
        buttonBox.AddButton(cancelButton)
        buttonBox.Realize()

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

        # Stop the orogional Lat/Lon values being edited
        oLat.SetEditable(False)
        oLon.SetEditable(False)

        self.Show(True)

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
        self.displayCache = None
        w = self.conf.common.mainWidth or 700
        h = self.conf.common.mainHeight or 500
        # check that the Current location is in the db
        if (self.conf.common.currentLoc or 'Default') not in self.db.getLocationNameList():
            self.conf.common.currentLoc = self.db.getLocationNameList()[0]
        wx.Frame.__init__(self,parent,wx.ID_ANY,_("Geocacher"),size = (w,h),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        self.buildStatusBar()

        self.buildMenu()

        self.buildToolBar()

        self.splitter = MainSplitter(self, wx.ID_ANY)
        self.cacheGrid = CacheGrid(self.splitter, self.conf, self.db,  self)
        self.Description = wx.html.HtmlWindow(self.splitter, wx.ID_ANY, name="Description Pannel")
        panel2 = wx.Window(self.splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.cacheGrid, self.Description, conf.common.mainSplit or 400)

        self.updateDetail(self.conf.common.dispCache or '')

    def buildMenu(self):
        '''Builds the menu'''
        MenuBar = wx.MenuBar()

        # Build file menu and bind functions
        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_ANY, text=_("&Load Waypoints from File"))
        self.Bind(wx.EVT_MENU, self.OnLoadWpt, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Load Waypoints from Folder"))
        self.Bind(wx.EVT_MENU, self.OnLoadWptDir, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Export Waypoints"))
        self.Bind(wx.EVT_MENU, self.OnExportWpt, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Back-up Database"))
        self.Bind(wx.EVT_MENU, self.OnBackupDb, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Restore Database"))
        self.Bind(wx.EVT_MENU, self.OnRestoreDb, item)

        item = FileMenu.Append(wx.ID_EXIT, text=_("&Quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, _("&File"))

        # Build preferences menu and bind functions
        PrefsMenu = wx.Menu()

        item = PrefsMenu.Append(wx.ID_ANY, text=_("&Preferences"))
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        MenuBar.Append(PrefsMenu, _("&Edit"))

        # Build GPS menu and bind functions
        GpsMenu = wx.Menu()

        item = GpsMenu.Append(wx.ID_ANY, text=_("&Upload to GPS"))
        self.Bind(wx.EVT_MENU, self.OnGpsUpload, item)

        item = GpsMenu.Append(wx.ID_ANY, text=_("&Location From GPS"))
        self.Bind(wx.EVT_MENU, self.OnGpsLocation, item)

        MenuBar.Append(GpsMenu, _("&GPS"))

        # Build Help menu and bind functions
        HelpMenu = wx.Menu()

        item = HelpMenu.Append(wx.ID_ABOUT, text=_("&About"))
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, item)

        MenuBar.Append(HelpMenu, _("&Help"))

        # Add the menu bar to the frame
        self.SetMenuBar(MenuBar)

    def buildToolBar(self):
        TBFLAGS = ( wx.TB_HORIZONTAL
                    | wx.NO_BORDER
                    | wx.TB_FLAT
                    #| wx.TB_TEXT
                    #| wx.TB_HORZ_LAYOUT
                    )

        tsize = (24,24)

        tb = self.CreateToolBar(TBFLAGS)

        tb.AddControl(wx.StaticText(tb, -1, _('Fiter Options'), style=wx.TEXT_ATTR_FONT_ITALIC))

        self.cbHideMine = wx.CheckBox(tb, wx.ID_ANY, _('Hide Mine'))
        tb.AddControl(self.cbHideMine)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideMine, self.cbHideMine)
        self.cbHideMine.SetValue(self.conf.filter.mine or False)

        self.cbHideFound = wx.CheckBox(tb, wx.ID_ANY, _('Hide Found'))
        tb.AddControl(self.cbHideFound)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideFound, self.cbHideFound)
        self.cbHideFound.SetValue(self.conf.filter.found or False)

        self.cbHideDisabled = wx.CheckBox(tb, wx.ID_ANY, _('Hide Disabled'))
        tb.AddControl(self.cbHideDisabled)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideDisabled, self.cbHideDisabled)
        self.cbHideDisabled.SetValue(self.conf.filter.disabled or False)

        self.cbHideArchived = wx.CheckBox(tb, wx.ID_ANY, _('Hide Archived'))
        tb.AddControl(self.cbHideArchived)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideArchived, self.cbHideArchived)
        self.cbHideArchived.SetValue(self.conf.filter.archived or False)

        tb.AddSeparator()

        tb.AddControl(wx.StaticText(tb, -1, _('Home location'), style=wx.TEXT_ATTR_FONT_ITALIC))
        choices = self.db.getLocationNameList()
        if self.conf.common.currentLoc in choices:
            current = self.conf.common.currentLoc
        else:
            current = choices[0]
        self.selLocation = wx.ComboBox(tb, wx.ID_ANY,current,
                                       choices = choices,
                                       size=[150,-1],
                                       style=wx.CB_DROPDOWN|wx.CB_SORT)
        tb.AddControl(self.selLocation)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelLocation, self.selLocation)
        tb.Realize()

    def buildStatusBar(self):
        self.CreateStatusBar()

    def updateDetail(self, newCache=''):
        # TODO: add further information to display
        # TODO: add option to view actual webpage
        newCacheObj = self.db.getCacheByCode(newCache)
        if newCacheObj != None:
            self.displayCache = newCacheObj
        if self.displayCache == None:
            descText = _('Select a Cache to display from the table above')
        else:
            descText = "<h1>" + self.displayCache.code + "</h1>"
            if self.displayCache.short_desc != None:
                if self.displayCache.short_desc_html:
                    descText = descText + self.displayCache.short_desc
                else:
                    descText = descText + '<p>' + nl2br(self.displayCache.short_desc) + '<p>'
            if self.displayCache.long_desc != None:
                if self.displayCache.long_desc_html:
                    descText = descText + self.displayCache.long_desc
                else:
                    descText = descText + '<p>' + nl2br(self.displayCache.long_desc) + '<p>'
            if len(self.displayCache.encoded_hints) > 0:
                descText = descText + '<h2>Encoded Hints</h2><p>' + nl2br(self.displayCache.encoded_hints.encode('rot13')) + '</p>'
        self.Description.SetPage(descText)

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

    def updateFilter(self):
        self.cacheGrid.ReloadCaches()

    def updateLocations(self):
        for i in range(0,self.selLocation.GetCount()):
            self.selLocation.Delete(0)
        for location in self.db.getLocationNameList():
            self.selLocation.Append(location)

    def updateCurrentLocation(self, name):
        self.selLocation.SetValue(name)
        self.conf.common.currentLoc = name
        self.cacheGrid.UpdateLocation()


    def GpsError(self, message):
        wx.MessageBox(parent = self,
            message = _('Error communicating with GPS, GPSBabel said:\n')+message,
            caption = _('GPS Error'),
            style = wx.OK | wx.ICON_ERROR)

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
            if self.conf.load.mode == 'replace':
                dlg.SetSelection(1)
            else:
                dlg.SetSelection(0)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    self.conf.load.mode = 'update'
                else:
                    self.conf.load.mode = 'replace'

                for path in paths:
                    self.LoadFile(path, self.conf.load.mode)
                self.cacheGrid.ReloadCaches()
            dlg.Destroy()

    def OnLoadWptDir(self, event=None):

        if os.path.isdir(self.conf.load.lastFolder):
            dir = self.conf.load.lastFolder

        else:
            dir = os.getcwd()

        dlg = wx.DirDialog(self, _('Select Folder to import waypoint files from'),
                                 defaultPath=dir,
                                 style=wx.DD_DEFAULT_STYLE
                                 | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            self.conf.load.lastFolder = dir

            options = [_('Update'),_('Replace')]
            dlg = wx.SingleChoiceDialog(self, _('Load option'),
                                        _('Type of file load'),
                                        choices=options,
                                        style=wx.CHOICEDLG_STYLE)
            if self.conf.load.mode == 'replace':
                dlg.SetSelection(1)
            else:
                dlg.SetSelection(0)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    self.conf.load.mode = 'update'
                else:
                    self.conf.load.mode = 'replace'

                addWptFiles = []
                for file in listFiles(dir):
                    if path.rfind('-wpts') >= 0:
                        addWptFiles.append(file)
                    else:
                        self.LoadFile(file, self.conf.load.mode)
                for file in addWptFiles:
                    self.LoadFile(file, self.conf.load.mode)
                self.cacheGrid.ReloadCaches()
            dlg.Destroy()

    def LoadFile(self, path, mode):
        ext = os.path.splitext(path)[1]
        if ext == '.gpx':
            gpxLoad(path,self.db,mode=mode,
                    userId=self.conf.gc.userId,
                    userName=self.conf.gc.userName)
        elif ext == '.loc':
            locLoad(path,self.db,mode=mode)
        elif ext == '.zip':
            zipLoad(path,self.db,mode=mode,
                    userId=self.conf.gc.userId,
                    userName=self.conf.gc.userName)

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

    def OnBackupDb(self, event=None):
        wildcard = "XML (*.xml)|*.xml|"\
                   "Any Type (*.*)|*.*|"
        dir = os.getcwd()
        dlg = wx.FileDialog(
            self, message=_("Select file to backup the DB to"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.isfile(path):
                question = wx.MessageDialog(None,
                               message=path + _(" already exists are you sure you want to replace it ?"),
                               caption=_("File Already Exists"),
                               style=wx.YES_NO|wx.ICON_WARNING
                               )
                if question.ShowModal() == wx.ID_NO:
                    question.Destroy()
                    return
                question.Destroy()
            self.db.backup(path)
        dlg.Destroy()

    def OnRestoreDb(self, event=None):
        wildcard = "XML (*.xml)|*.xml|"\
                   "Any Type (*.*)|*.*|"
        dir = os.getcwd()
        dlg = wx.FileDialog(
            self, message=_("Select file to restore the DB from"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            question = wx.MessageDialog(None,
                           message=_("Are you sure you want to replace the contents of the DB with ") + path + '?',
                           caption=_("Replace DB?"),
                           style=wx.YES_NO|wx.ICON_WARNING
                           )
            if question.ShowModal() == wx.ID_YES:
                self.db.restore(path)
                self.cacheGrid.ReloadCaches()
            question.Destroy()
        dlg.Destroy()


    def OnPrefs(self, event=None):
        dlg = PreferencesWindow(self, wx.ID_ANY, self.conf, self.db)
        if dlg.ShowModal() == wx.ID_OK:
            self.cacheGrid.UpdateUserDataLabels()
            self.updateLocations()
            self.updateCurrentLocation(
                self.conf.common.currentLoc or 'Default')
        dlg.Destroy()

    def OnGpsUpload(self, event=None):
        (scope, caches) = self.selectCaches(self.conf.export.scope, _('file'))
        if scope == None:
            return
        fd,tmpFile = tempfile.mkstemp()
        dlg = wx.MessageDialog(None,
            message=_("Do you want to include the additional waypoints?"),
            caption=_("GPS Upload"),
            style=wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            addWpts = True
        else:
            addWpts = False
        gpxExport(tmpFile, caches, addWpts = addWpts)
        gpsCom = GpsCom(gps=self.conf.gps.type or 'garmin',
                        port=self.conf.gps.connection or 'usb:')
        ok, message = gpsCom.gpxToGps(tmpFile)
        if not ok:
            self.GpsError( message)
        os.remove(tmpFile)

    def OnGpsLocation(self, event=None):
        gpsCom = GpsCom(gps=self.conf.gps.type or 'garmin',
                        port=self.conf.gps.connection or 'usb:')
        ok, lat, lon, message = gpsCom.getCurrentPos()
        if not ok:
            self.GpsError(message)
            return
        dlg = wx.TextEntryDialog(self,
            _('Please enter a name for the new Location from the GPS'),
            caption=_('Location Name'))
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        name = dlg.GetValue()
        dlg.Destroy()
        if name in self.db.getLocationNameList():
            dlg = wx.MessageDialog(self,
                message=_('Are you sure you want to replace the existing laocation named ')+name,
                caption=_('Replace Existing Location'),
                style=wx.YES_NO|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                location = self.db.getLocationByName(name)
                location.lat = lat
                location.lon = lon
            else:
                dlg.Destroy()
                return
        else:
            self.db.addLocation(name, lat, lon)
        self.updateLocations()
        self.updateCurrentLocation(name)

    def OnSelLocation(self, event=None):
        self.updateCurrentLocation(self.selLocation.GetValue())

    def OnCbHideArchived(self, event=None):
        self.conf.filter.archived = self.cbHideArchived.GetValue()
        self.updateFilter()

    def OnCbHideDisabled(self, event=None):
        self.conf.filter.disabled = self.cbHideDisabled.GetValue()
        self.updateFilter()

    def OnCbHideFound(self, event=None):
        self.conf.filter.found = self.cbHideFound.GetValue()
        self.updateFilter()

    def OnCbHideMine(self, event=None):
        self.conf.filter.mine = self.cbHideMine.GetValue()
        self.updateFilter()

    def OnQuit(self, event=None):
        """Exit application."""
        (self.conf.common.mainWidth,self.conf.common.mainHeight) = self.GetSizeTuple()
        self.conf.common.mainSplit = self.splitter.GetSashPosition()
        self.conf.common.cacheCols = self.cacheGrid.GetCols()
        self.conf.common.sortCol = self.cacheGrid.GetSortCol()
        if self.displayCache != None:
            self.conf.common.dispCache = self.displayCache.code
        else:
            self.conf.common.dispCache = ''
        self.conf.save()
        self.db.save()
        self.Destroy()

class GeocacherApp (wx.App):
    '''Application Class'''
    def OnInit(self):
        self.checker = wx.SingleInstanceChecker(".Geocacher_"+wx.GetUserId())
        if self.checker.IsAnotherRunning():
            dlg = wx.MessageDialog(None,
                message=_("Geocacher is already running, please switch to that instance."),
                caption=_("Geocacher Already Running"),
                style=wx.CANCEL|wx.ICON_HAND)
            dlg.ShowModal()
            return False
        else:
            Geocacher.init(True)
            frame = MainWindow(None,-1,Geocacher.conf, Geocacher.db)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    def OnExit(self):
        pass

USAGE = """%s [options]
Geocacher %s by Rob Wallace (c)2009, Licence GPL2
http://www.example.com""" % ("%prog",__version__)

if __name__ == "__main__":
    parser = optparse.OptionParser(usage=USAGE, version=("Geocaching "+__version__))
    parser.add_option("-v","--view",action="store_true",dest="view",
                        help="run in only view mode")
    parser.set_defaults(viewOnly=False)

    (options, args) = parser.parse_args()

    app = GeocacherApp(False)
    app.MainLoop()
