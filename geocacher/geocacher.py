#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import shutil

STATUS_MAIN = 0
STATUS_SHOWN = 1
STATUS_TOTAL = 2
STATUS_FILTERED = 3

from datetime import datetime
import logging #@UnusedImport
import optparse
import os
import sys
import tempfile
import zipfile

try:
    os.chdir(os.path.split(sys.argv[0])[0])
except:
    pass

import wx
import wx.grid             as  Grid
import wx.lib.gridmovers   as  Gridmovers
import wx.html             as Html

from libs.i18n import createGetText

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("geocaching",os.path.join(os.path.dirname(__file__), 'po'))
#def _ (t):
#    return t

from libs.common import nl2br, listFiles, dateCmp, wxDateTimeToPy
from libs.cacheStats import cacheStats
from libs.db import Geocacher
from libs.gpsbabel import GpsCom
from libs.gpx import gpxLoad, gpxExport, zipLoad, zipExport
from libs.loc import locLoad, locExport
from libs.latlon import distance, cardinalBearing

from dialogs.correctLatLon import CorrectLatLon
from dialogs.export import ExportOptions
from dialogs.foundCache import FoundCache
from dialogs.preferences import Preferences
from dialogs.viewHtml import ViewHtml
from dialogs.viewLogs import ViewLogs
from dialogs.viewTravelBugs import ViewTravelBugs

from renderers.deg import LatRenderer, LonRenderer
from renderers.dist import DistRenderer
from renderers.image import CacheBearingRenderer
from renderers.image import CacheSizeRenderer
from renderers.image import CacheTypeRenderer

try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"


class CacheDataTable(Grid.PyGridTableBase):
    '''
    Provides the Grid Table implementation for the cache data display grid
    '''
    def __init__(self, conf, db):
        '''
        Initialisation function for the cache grid.

        Arguments
        conf: configuration object for the program
        db:   database containing the cache information
        '''
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
            'difficulty'  :_('Difficulty'),
            'terrain'     :_('Terrain'),
            'distance'    :_('Distance'),
            'bearing'     :_('Bearing'),
            'oLat'        :_('Original Latitude'),
            'oLon'        :_("Original Longitude"),
            'cLat'        :_('Corrected Latitude'),
            'cLon'        :_("Corrected Longitude"),
            'corrected'   :_('Corrected Coordinates'),
            'available'   :_('Available'),
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
            'ftf'         :_('FTF'),
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
            'difficulty'  :Grid.GRID_VALUE_FLOAT + ':1,1',
            'terrain'     :Grid.GRID_VALUE_FLOAT + ':1,1',
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
            'ftf'         :Grid.GRID_VALUE_BOOL,
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
            'type'        :CacheTypeRenderer,
            'distance'    :DistRenderer,
            'bearing'     :CacheBearingRenderer}

        self._sortCol = self.conf.common.sortCol or 'code'
        self._sortDescend = self.conf.common.sortDescend or False

        self.ReloadCaches()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def ReloadCaches(self):
        '''
        Reloads all of the caches in the table from the database.
        '''
        self.data = []
        for cache in self.db.getCacheList():
            self.__addRow(cache)
        self.DoSort()

    def ReloadRow(self, row):
        '''
        Reloads the given row in the table from the database.

        Argument
        row: The row number to reload.
        '''
        cache = self.GetRowCache(row)
        self.data.pop(row)
        if not self.__cacheFilter(cache):
            self.data.insert(row, self.__buildRow(cache))

    def __addRow(self, cache):
        '''
        Adds the given cache to the table.
        cache: Cache to add to the table
        '''
        if not self.__cacheFilter(cache):
            self.data.append(self.__buildRow(cache))

    def __buildRow(self, cache):
        '''
        Builds a set of row data form the given cache ready for adding to the
        table.

        Argument
        cache: Cache to build row data from.
        '''
        dist, cBear = self.__calcDistBearing(cache)

        row = {'code':cache.code,
               'id':cache.id,
               'lon':cache.currentLon,
               'lat':cache.currentLat,
               'name':cache.name,
               'url':cache.url,
               'found':cache.found,
               'type':cache.type,
               'size':cache.container,
               'terrain':cache.terrain,
               'difficulty':cache.difficulty,
               'distance':dist,
               'bearing':cBear,
               'oLat':cache.lat,
               'oLon':cache.lon,
               'cLat':cache.clat,
               'cLon':cache.clon,
               'corrected':cache.corrected,
               'available':cache.available,
               'archived':cache.archived,
               'state':cache.state,
               'country':cache.country,
               'owner':cache.owner,
               'placedBy':cache.placed_by,
               'placed':cache.placed,
               'user_date':cache.user_date,
               'gpx_date':cache.gpx_date,
               'num_logs':cache.getNumLogs(),
               'last_log':cache.getLastLogDate(),
               'last_found':cache.getLastFound(),
               'found_count' :cache.getFoundCount(),
               'has_tb':cache.hasTravelBugs(),
               'locked':cache.locked,
               'ftf':cache.ftf,
               'found':cache.found,
               'found_date':cache.found_date,
               'dnf':cache.dnf,
               'dnf_date':cache.dnf_date,
               'source':cache.source,
               'user_flag':cache.user_flag,
               'user_data1':cache.user_data1,
               'user_data2':cache.user_data2,
               'user_data3':cache.user_data3,
               'user_data4':cache.user_data4}
        return row

    def __calcDistBearing(self, cache):
        '''
        Calculates the distance and cardinal Bearing of the given cache and
        returns it as a tuple

        Argument
        cache: Cache to perform calculations on.
        '''
        location = self.db.getLocationByName(self.conf.common.currentLoc or 'Default')
        hLat = location.lat
        hLon = location.lon

        dist = distance(hLat,hLon,cache.currentLat,cache.currentLon)
        cBear = cardinalBearing(hLat,hLon,cache.currentLat,cache.currentLon)
        return dist, cBear

    def __cacheFilter(self, cache):
        '''
        Returns true if the given cache should be filtered out of the list.

        Argument
        cache: cache to evaluate filter for.
        '''
        mine = cache.owner == self.conf.gc.userName or\
               cache.owner_id == self.conf.gc.userId
        dist, cBear = self.__calcDistBearing(cache) #@UnusedVariable
        return (bool(self.conf.filter.archived) and cache.archived) or\
               (bool(self.conf.filter.disabled) and (not cache.available)) or\
               (bool(self.conf.filter.found) and cache.found) or\
               (bool(self.conf.filter.mine) and mine)or\
               ((self.conf.filter.overDist) and ((self.conf.filter.maxDistVal or 50.0) <= dist))

    def UpdateLocation(self):
        '''
        Updates the location based information in all cache rows.
        '''
        if self.conf.filter.overDist:
            self.ReloadCaches()
        else:
            for row in self.data:
                row['distance'], row['bearing'] = self.__calcDistBearing(self.db.getCacheByCode(row['code']))
            if self._sortCol in ['distance','bearing']:
                self.DoSort()

    def UpdateUserDataLabels(self):
        '''
        Updates the user data column labels from the program configuration.
        '''
        self.colLabels['user_data1'] = \
            self.conf.common.userData1 or _('User Data 1')
        self.colLabels['user_data2'] = \
            self.conf.common.userData2 or _('User Data 2')
        self.colLabels['user_data3'] = \
            self.conf.common.userData3 or _('User Data 3')
        self.colLabels['user_data4'] = \
            self.conf.common.userData4 or _('User Data 4')

    def GetNumberRows(self):
        '''
        Returns the number of rows in the table.
        '''
        return len(self.data)

    def GetNumberCols(self):
        '''
        Returns the number of columns in the table.
        '''
        return len(self.colNames)

    def IsEmptyCell(self, row, col):
        '''
        Returns True if the cell at the given coordinates is empty.
        otherwise False.

        Arguments
        row: Row coordinate the cell to check.
        col: Column coordinate the cell to check
        '''
        id = self.colNames[col]
        return self.data[row][id] is not None

    def GetValue(self, row, col):
        '''
        Returns the value in the cell at the given coordinates.
        otherwise False.

        Arguments
        row: Row coordinate of the cell to return the value for.
        col: Column coordinate of the cell to return the value for.
        '''
        id = self.colNames[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        '''
        Sets the cell at the given coordinates to the given value.

        Arguments:
        row:   Row coordinate of the cell to change the value for.
        col:   Column coordinate of the cell to change the value for.
        value: Value to set the cell to.
        '''
        id = self.colNames[col]
        cache = self.GetRowCache(row)
        changed = False
        if self.dataTypes[id] == Grid.GRID_VALUE_BOOL:
            value = bool(value)
        if not cache.locked:
            if id == 'ftf':
                cache.ftf = value
                changed = True
            elif id == 'user_data1':
                cache.user_data1 = value
                changed = True
            elif id == 'user_data2':
                cache.user_data1 = value
                changed = True
            elif id == 'user_data3':
                cache.user_data1 = value
                changed = True
            elif id == 'user_data4':
                cache.user_data1 = value
                changed = True
            elif id == 'user_flag':
                cache.user_flag = value
                changed = True
        if id == 'locked':
            cache.locked = value
            changed = True
        if changed:
            now = datetime.now()
            cache.user_date = now
            self.data[row]['user_date'] = now
            self.data[row][id] = value
            self.GetView().ForceRefresh()

    def GetRowCode(self, row):
        '''
        Returns the code of the cache on the given row.

        Argument
        row: Row to get the cache code for.
        '''
        return self.data[row]['code']

    def GetRowCache(self, row):
        '''
        Returns the cache object associated with the given row.

        Argument
        row: Row to get the cache object for.
        '''
        return self.db.getCacheByCode(self.GetRowCode(row))

    def GetRowCaches(self, rows):
        '''
        Returns a list of the cache objects associated with the given list of
        rows.

        Argument
        rows: List of rows to return the cache objects for.
        '''
        caches = []
        for row in rows:
            caches.append(self.GetRowCache(row))
        return caches

    def GetDisplayedCaches(self):
        '''
        Returns a list containing the cache objects for the selected rows in
        the table.
        '''
        caches = []
        for row in self.data:
            caches.append(self.db.getCacheByCode(row['code']))
        return caches

    def GetRowLabelValue(self, row):
        '''
        Returns the label for the given row.

        Argument
        row: Row number to return the label for.
        '''
        return self.GetRowCode(row)

    def GetColLabelValue(self, col):
        '''
        Returns the label for the given column.

        Argument
        row: Column number to return the label for.
        '''
        id = self.colNames[col]
        return self.colLabels[id]

    def GetColLabelValueByName(self, name):
        '''
        Returns the label for the given column name.

        Argument
        name: Column name to return the label for.
        '''
        return self.colLabels[name]

    def GetTypeName(self, row, col):
        '''
        Returns the type of the data in the cell at the given coordinates.

        Arguments
        row:    Row coordinate of the cell to return the data type of.
        column: Column coordinate of the cell to return the data type of.
        '''
        id = self.colNames[col]
        return self.dataTypes[id]

    def CanGetValueAs(self, row, col, typeName):
        '''
        Returns True if the data in the cell at the given coordinates can be
        fetched as the given type.

        Arguments
        row:      Roe coordinate of the cell to be checked.
        col:      Column coordinate of the cell to be checked.
        typeName: Name of the type the compare the cell data to.
        '''
        id = self.colNames[col]
        colType = self.dataTypes[id].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        '''
        Returns True if the data in the cell at the given coordinates can be
        set using the given type.

        Arguments
        row:      Roe coordinate of the cell to be checked.
        col:      Column coordinate of the cell to be checked.
        typeName: Name of the type the compare the cell data to.
        '''
        id = self.cols[col]
        return self.CanGetValueAs(row, id, typeName)

    def AppendColumn(self,col):
        '''
        Appends the given column to the table.

        Argument
        col: The name of the column to append to the table.
        '''
        self.colNames.append(col)
        if len(self.colNames) == 1:
            self.ReloadCaches()

    def InsertColumn(self,pos,col):
        '''
        Inserts a column into the table at the given position.

        Arguments:
        pos: Position at which to insert the column.
        col: The name of the column to insert into the table.
        '''
        self.colNames.insert(pos,col)

    def MoveColumn(self,frm,to):
        '''
        Moves a column from one given location to another.

        Arguments
        frm: Location to move the column from.
        to:  Location to move the column.
        '''
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
        Delete the given list of columns form the table.

        Argument
        cols: List containing the positions of the columns to delete.
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
        Resets (Updates) the GridView associated with the data table when rows
        or columns are added or deleted.

        Argument
        grid: The GirdView to be updated.
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(),
             Grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
             Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(),
             Grid.GRIDTABLE_NOTIFY_COLS_DELETED,
             Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
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
        # update the column rendering plug-ins
        self._updateColAttrs(grid)

        # update the scroll bars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def DeleteRows(self, rows):
        """
        Delete the given list of rows form the table.

        Argument
        rows: List containing the positions of the columns to delete.
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

    def SortColumn(self, col, descending=None):
        """
        Sorts the data in the table based on the given column and in the given
        direction

        Arguments
        col:       Position of the column to sort by.
        decending: Controls the direction of the sort as follows:
                        None: Toggle the direction of the sort
                        False: Ascending sort.
                        True:  Descending sort.
        """
        self.SortColumnName(self.colNames[col], descending)

    def SortColumnName(self, name, descending=None):
        """
        Sorts the data in the table based on the given column and in the given
        direction

        Arguments
        name:      Name of the column to sort by.
        decending: Controls the direction of the sort as follows:
                        None: Toggle the direction of the sort
                        False: Ascending sort.
                        True:  Descending sort.
        """
        if self.colLabels.has_key(name):
            if descending == None:
                descending = (not self._sortDescend) and self._sortCol == name
            if self._sortCol != name or self._sortDescend != descending:
                self._sortCol = name
                self._sortDescend = descending
                self.DoSort()

    def SortDataItem(self, rowData):
        '''
        Returns the data item to be sorted by for a given table row.

        Argument
        rowData: The row data set to return the data item to sort by.
        '''
        return rowData[self._sortCol]

    def DoSort(self):
        '''
        Performs the actual data sort on the table based on the stored
        parameters.
        '''

        # Fix the comparison function for dates
        if self.dataTypes[self._sortCol] == Grid.GRID_VALUE_DATETIME:
            cmp = dateCmp
        else:
            cmp = None

        self.data.sort(cmp=cmp, key=self.SortDataItem, reverse=self._sortDescend)

    def _updateColAttrs(self, grid):
        """
        Update the column attributes for the given Grid and add the
        appropriate renderer.

        Argument
        grid: The grid view to update.
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
        '''
        Returns a dictionary of the names of the visible columns.
        '''
        return self.colNames

    def GetAllCols(self):
        '''
        Returns a list of all of the column identifiers.
        '''
        return self.colLabels.keys()

    def GetSort(self):
        '''
        Returns a tuple containing the sort column and the sort direction.
        '''
        return (self._sortCol, self._sortDescend)


class CacheGrid(Grid.Grid):
    '''
    Grid to display the cache information.
    '''
    def __init__(self, parent, conf, db, mainWin):
        '''
        Initialisation function for the grid

        Argumnets
        parent:  Parent window for the grid.
        conf:    Program configuration object
        db:      Database to build table data form.
        mainWin: Reference to the main application window for call back
                 functions.
        '''
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
        self.Bind(Grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClicked)
        self.Bind(Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClicked)
        self.Bind(Grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClicked)
        self.Bind(Grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClicked)

        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.SetMargins(0,0)
        self.Reset()

    # Event method called when a column move needs to take place
    def OnColMove(self,evt):
        '''
        Event handler for grid column moves.

        Argumnet
        evt: Event object.
        '''
        frm = evt.GetMoveColumn()       # Column being moved
        to = evt.GetBeforeColumn()      # Before which column to insert
        self._table.MoveColumn(frm,to)
        self.Reset()

    # Event method called when a row move needs to take place
    def OnRowMove(self,evt):
        '''
        Event handler for grid row moves.

        Argumnet
        evt: Event object.
        '''
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self._table.MoveRow(frm,to)

    def OnLabelLeftClicked(self, evt):
        '''
        Event handler for left click events on grid labels.

        Argumnet
        evt: Event object.
        '''
        # Did we click on a row or a column?
        if evt.GetRow() != -1:
            self.mainWin.updateDetail(self._table.GetRowCode(evt.GetRow()))
        evt.Skip()

    def OnCellLeftClicked(self, evt):
        '''
        Event handler for left click events on grid cells.

        Argumnet
        evt: Event object.
        '''
        self.mainWin.updateDetail(self._table.GetRowCode(evt.GetRow()))
        evt.Skip()

    def OnLabelRightClicked(self, evt):
        '''
        Event handler for right click events on grid labels.

        Argumnet
        evt: Event object.
        '''
        self.Popup(evt)

    def OnCellRightClicked(self, evt):
        '''
        Event handler for right click events on grid cells.

        Argumnet
        evt: Event object.
        '''
        self.Popup(evt)

    def Popup (self, evt):
        '''
        Handler caled form all gid right click handlers to perform the actual
        event handling and generate the the context sensitive menu.

        Argumnet
        evt: Event object.
        '''
        row, col = evt.GetRow(), evt.GetCol()
        if row != -1:
            cache = self._table.GetRowCache(row)
        else:
            cache = None

        #---Build Append/Insert Column sub-menus---#000000#FFFFAA------------------------------------------------------
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

        #---Column pop-up functions---#000000#FFFFAA------------------------------------------------------
        def colDelete(event, self=self, col=col):
            '''Delete (Hide) the selected columns'''
            cols = self.GetSelectedCols()
            if len(cols) == 0:
                cols = [col]
            self._table.DeleteCols(cols)
            self.Reset()

        def colSortAscending(event, self=self, col=col):
            '''Perform an ascending sort on the selected column'''
            self.mainWin.pushStatus(_('Sorting caches'))
            self._table.SortColumn(col, False)
            self.Reset()
            self.mainWin.popStatus()

        def colSortDescending(event, self=self, col=col):
            '''Perform an descending sort on the selected column'''
            self.mainWin.pushStatus(_('Sorting caches'))
            self._table.SortColumn(col, True)
            self.Reset()
            self.mainWin.popStatus()

        def colInsert(event, self=self, colIds=insColIds, col=col):
            '''Insert the given column before the currently selected column'''
            if col == -1:
                self._table.AppendColumn(colIds[event.Id])
            else:
                self._table.InsertColumn(col, colIds[event.Id])
            self.Reset()

        def colAppend(event, self=self, colIds=appColIds):
            '''Append the given column to the end of the grid'''
            self._table.AppendColumn(colIds[event.Id])
            self.Reset()

        #---Row pop-up functions---#000000#FFFFAA------------------------------------------------------
        def cacheAdd(event, self=self, row=row):
            '''Add a new cache to the grid/database'''
            dlg = wx.MessageDialog(None,
                message=_('Manualy adding cache not yet implemented!'),
                caption=_('Not Implemented'),
                style=wx.CANCEL|wx.ICON_HAND)
            dlg.ShowModal()
            dlg.Destroy()
            #self._table.AddCache(cache)
            #self.Reset()
            print "adding cache not yet implemented"

        def cacheDelete(event, self=self, row=row):
            '''Delete the selected cache(s) (row(s))'''
            self.mainWin.pushStatus(_('Deleting caches'))
            rows = self.GetSelectedRows()
            if len(rows) == 0:
                rows = [row]
            self._table.DeleteRows(rows)
            self.Reset()
            self.mainWin.popStatus()

        def cacheCorrect(event, self=self, row=row, cache=cache):
            '''Add/Edit Correction of the Lat/Lon for the selected cache (row)'''
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
                self.mainWin.pushStatus(_('Correcting cache: %s') % cache.code)
                cache.clat = data['clat']
                cache.clon = data['clon']
                cache.cnote = data['cnote']
                cache.corrected = True
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()
                self.mainWin.popStatus()
            dlg.Destroy()

        def cacheRemCorrection(event, self=self, row=row, cache=cache):
            '''Remove the Lat/Lon correction for the selected cache (row)'''
            self.SelectRow(row)
            dlg = wx.MessageDialog(None,
                message=_('Are you sure you want to remove the cordinate correction for ')+cache.code,
                caption=_('Remove Cordinate Correction'),
                style=wx.YES_NO|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.mainWin.pushStatus(_('Removing correction from cache: %s') % cache.code)
                cache.clat = 0.0
                cache.clon = 0.0
                cache.corrected = False
                cache.cnote = ''
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()
                self.mainWin.popStatus()
            dlg.Destroy()

        def cacheViewLogs(event, self=self, cache=cache):
            '''View the logs for the selected cache (row).'''
            self.SelectRow(row)
            dlg = ViewLogs(self.mainWin, cache)
            dlg.ShowModal()
            dlg.Destroy()

        def cacheViewBugs(event, self=self, cache=cache):
            '''View the travel bugs for the selected cache (row).'''
            self.SelectRow(row)
            dlg = ViewTravelBugs(self.mainWin, cache)
            dlg.ShowModal()
            dlg.Destroy()

        def cacheAsHome(event, self=self, cache=cache):
            self.mainWin.NewLocation(cache.lat, cache.lon,
                                     'cache ' + cache.code,
                                     'cache ' + cache.code)

        def cacheSetFound(event, self=self, cache=cache):
            dlg = FoundCache(self.mainWin,cache.code,_('found'),
                             cache.found_date,cache.own_log,
                             cache.own_log_encoded)
            if dlg.ShowModal() == wx.ID_OK:
                self.mainWin.pushStatus(_('Marking cache %s as found') % cache.code)
                cache.found_date = wxDateTimeToPy(dlg.date.GetValue())
                cache.own_log = dlg.logText.GetValue()
                cache.own_log_encoded = dlg.encodeLog.GetValue()
                cache.found = True
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()
                self.mainWin.popStatus()
            dlg.Destroy()

        def cacheSetDnf(event, self=self, cache=cache):
            dlg = FoundCache(self.mainWin,cache.code,_('found'),
                             cache.dnf_date,cache.own_log,
                             cache.own_log_encoded)
            if dlg.ShowModal() == wx.ID_OK:
                self.mainWin.pushStatus(_('Marking cache %s as did not find') % cache.code)
                cache.dnf_date = wxDateTimeToPy(dlg.date.GetValue())
                cache.own_log = dlg.logText.GetValue()
                cache.own_log_encoded = dlg.encodeLog.GetValue()
                cache.dnf = True
                cache.user_date = datetime.now()
                self._table.ReloadRow(row)
                self.Reset()
                self.mainWin.popStatus()
            dlg.Destroy()

        #---Non row/col pop-up functions---#000000#FFFFAA-------------------------------
        def sortByCodeAscending(event, self=self):
            '''Perform an ascending sort based on the cache code'''
            self.mainWin.pushStatus(_('Sorting caches'))
            self._table.SortColumnName('code', False)
            self.Reset()
            self.mainWin.popStatus()

        def sortByCodeDescending(event, self=self):
            '''Perform an descending sort based on the cache code'''
            self.mainWin.pushStatus(_('Sorting caches'))
            self._table.SortColumnName('code', True)
            self.Reset()
            self.mainWin.popStatus()

        #---Menu ID's---#000000#FFFFAA------------------------------------------------------
        cacheAddID      = wx.NewId()
        cacheDeleteID   = wx.NewId()
        cacheCorrectID  = wx.NewId()
        cacheRmCorrID   = wx.NewId()
        cacheViewLogsID = wx.NewId()
        cacheViewBugsID = wx.NewId()
        cacheAsHomeID   = wx.NewId()
        cacheSetFoundID = wx.NewId()
        cacheSetDnfID   = wx.NewId()
        colDeleteID     = wx.NewId()
        colSortAsID     = wx.NewId()
        colSortDsID     = wx.NewId()
        sortByCodeAsID  = wx.NewId()
        sortByCodeDsID  = wx.NewId()

        #---Build the pop-up menu---#000000#FFFFAA--------------------------------------
        menu = wx.Menu()
        if col == -1:
            menu.Append(sortByCodeAsID, _('Ascending Sort By Cache Code'))
            menu.Append(sortByCodeDsID, _('Descending Sort By Cache Code'))
        else:
            menu.Append(colSortAsID, _('Ascending Sort By Column'))
            menu.Append(colSortDsID, _('Descending Sort By Column'))
        menu.AppendSeparator()
        menu.AppendMenu(wx.ID_ANY, _('Append Column'), appMenu)
        menu.AppendMenu(wx.ID_ANY, _('Insert Column'), insMenu)
        menu.Append(colDeleteID, _('Delete Column(s)'))
        menu.AppendSeparator()
        menu.Append(cacheAddID, _('Add Cache'))
        if row >= 0:
            menu.Append(cacheDeleteID, _('Delete Cache(s)'))
            menu.AppendSeparator()
            if cache.corrected:
                menu.Append(cacheCorrectID, _('Edit Cordinate Correction'))
                menu.Append(cacheRmCorrID, _('Remove Cordinate Correction'))
            else:
                menu.Append(cacheCorrectID, _('Correct Cordinates'))
            if cache.getNumLogs() > 0: menu.Append(cacheViewLogsID, _('View Logs'))
            if cache.hasTravelBugs(): menu.Append(cacheViewBugsID, _('View Travel Bugs'))
            menu.Append(cacheAsHomeID, _('Add cache as Home location'))
            menu.Append(cacheSetFoundID, _('Set cache as Found'))
            menu.Append(cacheSetDnfID, _('Set cache as Did Not Find'))

        #---Bind functions---#000000#FFFFAA---------------------------------------------
        self.Bind(wx.EVT_MENU, cacheAdd, id=cacheAddID)
        self.Bind(wx.EVT_MENU, cacheDelete, id=cacheDeleteID)
        self.Bind(wx.EVT_MENU, cacheCorrect, id=cacheCorrectID)
        self.Bind(wx.EVT_MENU, cacheRemCorrection, id=cacheRmCorrID)
        self.Bind(wx.EVT_MENU, cacheViewLogs, id=cacheViewLogsID)
        self.Bind(wx.EVT_MENU, cacheViewBugs, id=cacheViewBugsID)
        self.Bind(wx.EVT_MENU, cacheAsHome, id=cacheAsHomeID)
        self.Bind(wx.EVT_MENU, cacheSetFound, id=cacheSetFoundID)
        self.Bind(wx.EVT_MENU, cacheSetDnf, id=cacheSetDnfID)

        self.Bind(wx.EVT_MENU, colDelete, id=colDeleteID)
        self.Bind(wx.EVT_MENU, colSortAscending, id=colSortAsID)
        self.Bind(wx.EVT_MENU, colSortDescending, id=colSortDsID)
        for colId in appColIds:
            self.Bind(wx.EVT_MENU, colAppend, id=colId)
        for colId in insColIds:
            self.Bind(wx.EVT_MENU, colInsert, id=colId)

        self.Bind(wx.EVT_MENU, sortByCodeAscending, id=sortByCodeAsID)
        self.Bind(wx.EVT_MENU, sortByCodeDescending, id=sortByCodeDsID)

        self.PopupMenu(menu)
        menu.Destroy()
        return

    def NumSelectedRows(self):
        '''
        Returns the number of selected rows int he grid
        '''
        return len(self.GetSelectedRows())

    def GetDisplayedCaches(self):
        '''
        Returns a list of the cache objects associated with the caches
        displayed in the entire grid
        '''
        return self._table.GetDisplayedCaches()

    def GetSelectedCaches(self):
        '''
        Returns a list of the cache objects associated with the selected rows
        in the grid.
        '''
        return self._table.GetRowCaches(self.GetSelectedRows())

    def Reset(self):
        '''
        reset the view based on the data in the table.  Call
        this when rows are added or destroyed
        '''
        self._table.ResetView(self)
        # Use AutoSizeColumns() followed by AutoSizeRows() to avoid issues with
        # AutoSize() doing both and causing the splittter and scroll bars to
        # disapear
        self.AutoSizeColumns()
        self.AutoSizeRows()
        self.mainWin.updateStatus(self.GetNumberRows())

    def ReloadCaches(self):
        '''
        Reloads the grid cache data from the database.
        '''
        self._table.ReloadCaches()
        self.Reset()

    def UpdateUserDataLabels(self):
        '''
        Updates the displayed labels for the user data columns.
        '''
        self._table.UpdateUserDataLabels()
        self.Reset()

    def UpdateLocation(self):
        '''
        Updates the grid data for the current home location.
        '''
        self._table.UpdateLocation()
        self.Reset()

    def GetCols(self):
        '''
        Returns the names of columns in the grid
        '''
        return self._table.GetCols()

    def GetNumberCols(self):
        '''
        Returns the number of columns in the grid.
        '''
        return self._table.GetNumberCols()

    def GetNumberRows(self):
        '''
        Returns the number of rows in the grid.
        '''
        return self._table.GetNumberRows()

    def GetSort(self):
        '''
        Returns the sort column and type for the grid
        '''
        return self._table.GetSort()


class MainSplitter(wx.SplitterWindow):
    '''
    Provides the splitter for the main window.
    '''
    def __init__(self,parent,id):
        '''
        Initialises the splitter for the main window.

        Arguments
        parent: parent window for the splitter.
        id:     ID to give the splitter.
        '''

        wx.SplitterWindow.__init__(self, parent, id,
            style=wx.SP_LIVE_UPDATE | wx.SP_BORDER)


class MainWindow(wx.Frame):
    '''
    The main frome for the application.
    '''
    def __init__(self,parent,id, conf, db):
        '''
        Initialisation for the main frame.

        Arguments
        parent: The parent window of the frame.
        id:     The ID to give the frame.
        conf:   The configuration object for the program.
        db:     The application database.
        '''
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
        self.cacheGrid = CacheGrid(self.splitter, self.conf, self.db, self)
        self.Description = Html.HtmlWindow(self.splitter, wx.ID_ANY, name="Description Pannel")
        #panel2 = wx.Window(self.splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.cacheGrid, self.Description, conf.common.mainSplit or 400)

        self.updateStatus()

        self.displayedCache = None
        self.updateDetail(self.conf.common.dispCache or '')

    def buildMenu(self):
        '''
        Builds the menu bar for the main window
        '''
        MenuBar = wx.MenuBar()

        # Build file menu and bind functions
        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_ANY,
                               text=_("&Load Waypoints from File"))
        self.Bind(wx.EVT_MENU, self.OnLoadWpt, item)

        item = FileMenu.Append(wx.ID_ANY,
                               text=_("&Load Waypoints from Folder"))
        self.Bind(wx.EVT_MENU, self.OnLoadWptDir, item)

        item = FileMenu.Append(wx.ID_ANY,
                               text=_("&Export Waypoints"))
        self.Bind(wx.EVT_MENU, self.OnExportWpt, item)

        item = FileMenu.Append(wx.ID_ANY, text=_("&Back-up Database"))
        self.Bind(wx.EVT_MENU, self.OnBackupDb, item)

        item = FileMenu.Append(wx.ID_ANY,
                               text=_("&Restore Database"))
        self.Bind(wx.EVT_MENU, self.OnRestoreDb, item)

        item = FileMenu.Append(wx.ID_EXIT,
                               text=_("&Quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, _("&File"))

        # Build preferences menu and bind functions
        PrefsMenu = wx.Menu()

        item = PrefsMenu.Append(wx.ID_ANY,
                                text=_("&Preferences"))
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        MenuBar.Append(PrefsMenu, _("&Edit"))

        # Build view menu and bind functions
        ViewMenu = wx.Menu()

        self.miShowFilter = ViewMenu.Append(wx.ID_ANY,
                                            text=_('Show Filter Bar'),
                                            kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnShowFilter, self.miShowFilter)
        self.miShowFilter.Check(self.conf.common.showFilter or False)
        item = ViewMenu.Append(wx.ID_ANY,
                               text=_('Statistics'))
        self.Bind(wx.EVT_MENU, self.OnViewStats, item)

        MenuBar.Append(ViewMenu, _("&View"))

        # Build filter menu and bind functions
        FilterMenu = wx.Menu()

        self.miHideMine = FilterMenu.Append(wx.ID_ANY,
                                            text=_('Hide &Mine'),
                                            kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideMine, self.miHideMine)
        self.miHideMine.Check(self.conf.filter.mine or False)

        self.miHideFound = FilterMenu.Append(wx.ID_ANY,
                                             text=_('Hide &Found'),
                                             kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideFound, self.miHideFound)
        self.miHideFound.Check(self.conf.filter.found or False)

        self.miHideDisabled = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Disabled'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideDisabled, self.miHideDisabled)
        self.miHideDisabled.Check(self.conf.filter.disabled or False)

        self.miHideArchived = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Archived'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideArchived, self.miHideArchived)
        self.miHideArchived.Check(self.conf.filter.archived or False)

        self.miHideOverDist = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Over Max Dist'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideOverDist, self.miHideOverDist)
        self.miHideOverDist.Check(self.conf.filter.overDist or False)

        item = FilterMenu.Append(wx.ID_ANY, text=_('Set Max Distance'))
        self.Bind(wx.EVT_MENU, self.OnMaxDistVal, item)

        MenuBar.Append(FilterMenu, _("&Filter"))

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
        '''
        Builds the toolbar for the main window.
        '''
        TBFLAGS = ( wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)

        tb = self.CreateToolBar(TBFLAGS)
        self.tb = tb

        self.tbFilterName = wx.StaticText(tb, wx.ID_ANY, _('Fiter:'), style=wx.TEXT_ATTR_FONT_ITALIC)
        tb.AddControl(self.tbFilterName)

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

        self.cbHideOverDist = wx.CheckBox(tb, wx.ID_ANY, _('Hide Over'))
        tb.AddControl(self.cbHideOverDist)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideOverDist, self.cbHideOverDist)
        self.cbHideOverDist.SetValue(self.conf.filter.overDist or False)

        self.tbMaxDistance = wx.TextCtrl(tb, wx.ID_ANY,
            value=str(self.conf.filter.maxDistVal or 50.0), size=[100,-1])
        tb.AddControl(self.tbMaxDistance)
        self.tbMaxDistance.Bind(wx.EVT_LEFT_DCLICK, self.OnMaxDistVal)

        tb.AddSeparator()

        tb.AddControl(wx.StaticText(tb,
                                    wx.ID_ANY,
                                    _('Home location'),
                                    style=wx.TEXT_ATTR_FONT_ITALIC))
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

        self.ShowHideFilterBar(self.conf.common.showFilter or False)

    def buildStatusBar(self):
        '''
        Builds the status bar for the main window
        '''
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(4)
        self.statusbar.SetStatusWidths([-1,180,80,120])
        self.statusbar.SetStatusText(_('Geocacher - idle'),STATUS_MAIN)

    def pushStatus(self, text):
        '''
        Pushes the given text onto the stack for the current activity part of
        the ststus bar.

        Argument
        test: Text to push onto the stack.
        '''
        self.statusbar.PushStatusText(text, STATUS_MAIN)

    def popStatus(self):
        '''
        Removes the top item form the stack for the current activity part of
        the status bar.
        '''
        self.statusbar.PopStatusText(STATUS_MAIN)

    def updateStatus(self, rows=None):
        '''
        Updates the total number of caches and the number of caches after the
         filter the status bar.

         Keyword Arguments
         rows: the number of rows to use as the number of records after
               filtering.
        '''
        self.statusbar.SetStatusText(_('Total: %i') %
                                     self.db.getNumberCaches(),
                                     STATUS_TOTAL)
        if rows==None:
            self.statusbar.SetStatusText(_('After Filter: %i') %
                                         self.cacheGrid.GetNumberRows(),
                                         STATUS_FILTERED)
        else:
            self.statusbar.SetStatusText(_('After Filter: %i') %
                                         rows,
                                         STATUS_FILTERED)

    def updateDetail(self, newCache=''):
        '''
        Updates the cache detail panel with the details of the selected cache.

        Keyword Argument
        newCache: code of the cache to display the details of.
        '''

        if newCache == self.displayedCache:
            return

        self.displayedCache = newCache

        self.pushStatus(_('Loading cache: ') + newCache)
        newCacheObj = self.db.getCacheByCode(newCache)
        if newCacheObj != None:
            self.displayCache = newCacheObj
        if self.displayCache == None:
            self.statusbar.SetStatusText('',STATUS_SHOWN)
            descText = _('Select a Cache to display from the table above')
        else:
            self.statusbar.SetStatusText(_('Veiwing cache: ')+newCache,STATUS_SHOWN)
            descText = '<h1>' + self.displayCache.code + ' - ' + self.displayCache.name + '</h1>'
            if self.displayCache.url != '':
                descText = descText + '<p><a href="' + self.displayCache.url + '">View online page</a></p>'
            if self.displayCache.short_desc != None:
                if self.displayCache.short_desc_html:
                    descText = descText + self.displayCache.short_desc
                else:
                    descText = descText + '<p>' + nl2br(self.displayCache.short_desc) + '</p>'
            if self.displayCache.long_desc != None:
                if self.displayCache.long_desc_html:
                    descText = descText + self.displayCache.long_desc
                else:
                    descText = descText + '<p>' + nl2br(self.displayCache.long_desc) + '</p>'
            if len(self.displayCache.encoded_hints) > 0:
                descText = descText + '<h2>Encoded Hints</h2><p>' + nl2br(self.displayCache.encoded_hints.encode('rot13','ignore')) + '</p>'
        self.Description.SetPage(descText)
        self.popStatus()

    def selectCaches(self):
        '''
        Returns a list of cache objets for export based on the stored export
        preferences
        '''
        if self.conf.export.filterSel or False:
            caches = self.cacheGrid.GetSelectedCaches()
        elif self.conf.export.filterDisp or False:
            caches = self.cacheGrid.GetDisplayedCaches()
        else:
            caches = self.db.getCacheList()
        if self.conf.export.filterUser or False:
            filteredCaches = []
            for cache in caches:
                if cache.user_flag:
                    print cache.code
                    filteredCaches.append(cache)
            return filteredCaches
        else:
            return caches

    def updateFilter(self):
        '''
        Updates the data in the cache table/grid after a change of the filter
        criteria.
        '''
        self.pushStatus(_('Updating filter'))
        self.cacheGrid.ReloadCaches()
        self.updateStatus()
        self.popStatus()

    def updateLocations(self):
        '''
        Updates the location selector after a change to lt list of loactions.
        '''
        for i in range(0,self.selLocation.GetCount()): #@UnusedVariable
            self.selLocation.Delete(0)
        for location in self.db.getLocationNameList():
            self.selLocation.Append(location)

    def updateCurrentLocation(self, name):
        '''
        Updates the cache data in the table/grid when a new location is
        selected.

        Argument
        name: name of the new home loaction to be used.
        '''
        self.pushStatus(_('Updating home location to: %s') % name)
        self.selLocation.SetValue(name)
        self.conf.common.currentLoc = name
        self.cacheGrid.UpdateLocation()
        self.updateStatus()
        self.popStatus()


    def GpsError(self, message):
        '''
        Displays the given GPS error message to the user.

        Argument
        message: The GPS error message to be displayed.
        '''
        wx.MessageBox(parent = self,
            message = _('Error communicating with GPS, GPSBabel said:\n')+message,
            caption = _('GPS Error'),
            style = wx.OK | wx.ICON_ERROR)

    def OnHelpAbout(self, event=None):
        '''
        Handles the event from the "Help About" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
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
        '''
        Handles the event from the "Load Waypoint" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Loading caches from file'))
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
                    self.pushStatus(_('Loading caches from file: %s')% path)
                    self.LoadFile(path, self.conf.load.mode)
                    self.popStatus()
                self.cacheGrid.ReloadCaches()
            dlg.Destroy()
            self.popStatus()

    def OnLoadWptDir(self, event=None):
        '''
        Handles the event from the "Load Waypoints from file" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Loading caches from folder'))
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
                    if file.rfind('-wpts') >= 0:
                        addWptFiles.append(file)
                    else:
                        self.pushStatus(_('Loading caches from folder, processing file: %s') % file)
                        self.LoadFile(file, self.conf.load.mode)
                        self.popStatus()
                for file in addWptFiles:
                    self.pushStatus(_('Loading caches from folder, processing file: %s') % file)
                    self.LoadFile(file, self.conf.load.mode)
                    self.popStatus()
                self.cacheGrid.ReloadCaches()
            dlg.Destroy()
            self.popStatus()

    def LoadFile(self, path, mode):
        '''
        Handles the loading/importing of a waypoint file.

        Arguments
        path: Path to the file to be loaded/imported.
        mode" Mode to addthe file in (merge or Replace).
        '''
        ext = os.path.splitext(path)[1]
        if ext == '.gpx':
            ret = gpxLoad(path,self.db,mode=mode,
                          userId=self.conf.gc.userId,
                          userName=self.conf.gc.userName)
        elif ext == '.loc':
            ret = locLoad(path,self.db,mode=mode)
        elif ext == '.zip':
            ret = zipLoad(path,self.db,mode=mode,
                          userId=self.conf.gc.userId,
                          userName=self.conf.gc.userName)
        if ret == False:
            wx.MessageDialog(self,
                             _('Could not import "%s" due to an error accessing the file') % path,
                             caption=_("File import error"),
                             style=wx.OK|wx.ICON_WARNING)

    def OnExportWpt(self, event=None):
        '''
        Handles the event from the "Export Waypoints to file" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Exporting caches to file'))
        opts = ExportOptions(self, self.conf, False)
        if opts.ShowModal() == wx.ID_OK:
            opts.SaveConf()
            path = opts.GetPath()
            self.popStatus()
            self.pushStatus(_('Exporting caches to file: %s') % path)
            if os.path.isfile(path):
                question = wx.MessageDialog(None,
                               message=_('"%s" already exists are you sure you want to replace it ?') % path,
                               caption=_('File Already Exists'),
                               style=wx.YES_NO|wx.ICON_WARNING
                               )
                if question.ShowModal() == wx.ID_NO:
                    question.destroy()
                    self.popStatus()
                    return
            ext = os.path.splitext(path)[1]
            caches = self.selectCaches()
            if len(caches) == 0:
                wx.MessageBox(parent = self,
                                  message = _('With the current settings there is nothing to export!'),
                                  caption = _('Nothing to export'),
                                  style = wx.OK | wx.ICON_ERROR)
            else:
                if ext == '.loc':
                    ret = locExport(path, caches)
                elif ext == '.gpx':
                    ret = gpxExport(path, caches,
                                    full       = opts.GetType() == 'full',
                                    simple     = opts.GetType() == 'simple',
                                    gc         = opts.GetGc(),
                                    logs       = opts.GetLogs(),
                                    tbs        = opts.GetTbs(),
                                    addWpts    = opts.GetAddWpts())
                elif ext == '.zip':
                    self.conf.export.sepAddWpts = opts.GetSepAddWpts()
                    ret = zipExport(path, caches,
                                    full       = opts.GetType() == 'full',
                                    simple     = opts.GetType() == 'simple',
                                    gc         = opts.GetGc(),
                                    logs       = opts.GetLogs(),
                                    tbs        = opts.GetTbs(),
                                    addWpts    = opts.GetAddWpts(),
                                    sepAddWpts = opts.GetSepAddWpts())
                if not ret:
                    wx.MessageBox(parent = self,
                                  message = _('Error exporting to file: %s') % path,
                                  caption = _('Way point export Error'),
                                  style = wx.OK | wx.ICON_ERROR)
            self.popStatus()

    def OnBackupDb(self, event=None):
        '''
        Handles the event from the "Backup Database" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Backing up the Database'))
        wildcard = "Zip (*.zip)|*.zip|"\
                   "XML (*.xml)|*.xml|"\
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
            self.popStatus()
            self.pushStatus(_('Backing up the Database to: %s') % path)
            if os.path.isfile(path):
                question = wx.MessageDialog(None,
                               message=path + _(" already exists are you sure you want to replace it ?"),
                               caption=_("File Already Exists"),
                               style=wx.YES_NO|wx.ICON_WARNING
                               )
                if question.ShowModal() == wx.ID_NO:
                    question.Destroy()
                    dlg.Destroy()
                    self.popStatus()
                    return
                question.Destroy()

            zip = os.path.splitext(path)[1] == '.zip'
            if zip:
                realPath = path
                tempDir = tempfile.mkdtemp()
                path = os.path.join(tempDir,'backup.xml')
                archive = zipfile.ZipFile(realPath, mode='w', compression=zipfile.ZIP_DEFLATED)
            self.db.backup(path)
            if zip:
                archive.write(path, os.path.basename(path).encode("utf_8"))
                archive.close()
                shutil.rmtree(tempDir)
        dlg.Destroy()
        self.popStatus()

    def OnRestoreDb(self, event=None):
        '''
        Handles the event from the "Restore Database" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Restoring database from file'))
        wildcard = "Zip (*.zip)|*.zip|"\
                   "XML (*.xml)|*.xml|"\
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
            error = False
            self.popStatus()
            self.pushStatus(_('Restoring database from file: %s') % path)
            question = wx.MessageDialog(None,
                           message=_("Are you sure you want to replace the contents of the DB with ") + path + '?',
                           caption=_("Replace DB?"),
                           style=wx.YES_NO|wx.ICON_WARNING
                           )
            if question.ShowModal() == wx.ID_YES:
                zip = os.path.splitext(path)[1] == '.zip'
                if zip:
                    tempDir = tempfile.mkdtemp()
                    try:
                        archive = zipfile.ZipFile(path, mode='r')
                        archive.extractall(tempDir)
                        archive.close()
                        path = os.path.join(tempDir,'backup.xml')
                    except:
                        error = True
                    error = error or not os.path.isfile(path)
                if not error:
                    error = not self.db.restore(path)
                if zip:
                    shutil.rmtree(tempDir)
            question.Destroy()
        dlg.Destroy()
        if error:
            dlg = wx.MessageDialog(None,
                           message=_("Problem restoring database from ") + path + '?',
                           caption=_(" DB?"),
                           style=wx.OK|wx.ICON_ERROR
                           )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.cacheGrid.ReloadCaches()
        self.popStatus()


    def OnPrefs(self, event=None):
        '''
        Handles the event from the "Preferences" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        dlg = Preferences(self, wx.ID_ANY, self.conf, self.db)
        if dlg.ShowModal() == wx.ID_OK:
            self.cacheGrid.UpdateUserDataLabels()
            self.updateLocations()
            self.updateCurrentLocation(
                self.conf.common.currentLoc or 'Default')
        dlg.Destroy()

    def ShowHideFilterBar(self, show):
        '''
        Shows (or hides) the filter control items on the toolbar

        Argument
        show: Tells the function if the toolbar items are to be shown.
        '''
        self.tbFilterName.Show(show)
        self.cbHideArchived.Show(show)
        self.cbHideDisabled.Show(show)
        self.cbHideFound.Show(show)
        self.cbHideMine.Show(show)
        self.cbHideOverDist.Show(show)
        self.tbMaxDistance.Show(show)

    def OnShowFilter(self, event=None):
        '''
        Handles the event from the "Show Filter" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        show = self.miShowFilter.IsChecked()
        self.conf.common.showFilter = show
        self.ShowHideFilterBar(show)

    def OnGpsUpload(self, event=None):
        '''
        Uploads caches to GPS
        '''
        self.pushStatus(_('Uploading caches to GPS'))
        opts = ExportOptions(self, self.conf, True)
        if opts.ShowModal() == wx.ID_OK:
            opts.SaveConf()
            caches = self.selectCaches()
            if len(caches) == 0:
                wx.MessageBox(parent = self,
                                  message = _('With the current settings there is nothing to export!'),
                                  caption = _('Nothing to export'),
                                  style = wx.OK | wx.ICON_ERROR)
            else:
                fd,tmpFile = tempfile.mkstemp() #@UnusedVariable
                if gpxExport(tmpFile, caches,
                            full       = opts.GetType() == 'full',
                            simple     = opts.GetType() == 'simple',
                            gc         = opts.GetGc(),
                            logs       = opts.GetLogs(),
                            tbs        = opts.GetTbs(),
                            addWpts    = opts.GetAddWpts()):
                    gpsCom = GpsCom(gps=self.conf.gps.type or 'garmin',
                                    port=self.conf.gps.connection or 'usb:')
                    ok, message = gpsCom.gpxToGps(tmpFile)
                    if not ok:
                        self.GpsError( message)
                os.remove(tmpFile)
        self.popStatus()

    def OnGpsLocation(self, event=None):
        '''
        Handles the event from the "Location from GPS" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Loading new loaction form GPS'))
        gpsCom = GpsCom(gps=self.conf.gps.type or 'garmin',
                        port=self.conf.gps.connection or 'usb:')
        ok, lat, lon, message = gpsCom.getCurrentPos()
        if ok:
            self.NewLocation(lat, lon, _('the GPS'), _('GPS Point'))
        else:
            self.GpsError(message)
        self.popStatus()

    def NewLocation(self, lat, lon, source, name=''):
        '''
        Handles the creation of a new home loaction.

        Arguments
        lat:    Lattitude of the new location.
        lon:    Longitude of the new location.
        source: Text describing the source that the new location has come
                from.

        Keyword Argument
        name:   Default name for the new location.
        '''
        dlg = wx.TextEntryDialog(self,
            _('Please enter a name for the new Location from ') + source,
            caption=_('Location Name'),
            defaultValue = name)
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
        '''
        Handles the event from the select location toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.updateCurrentLocation(self.selLocation.GetValue())

    def OnHideArchived(self, state):
        '''
        Handles the event from the toggling of the "Hide Archived"
        toolbar or menu item.

        Argument
        state: The state of the checkbox causing the function to be called.
        '''
        self.conf.filter.archived = state
        self.miHideArchived.Check(state)
        self.cbHideArchived.SetValue(state)
        self.updateFilter()

    def OnCbHideArchived(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Archived"
        toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideArchived(self.cbHideArchived.GetValue())

    def OnMiHideArchived(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Archived"
        menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideArchived(self.miHideArchived.IsChecked())

    def OnHideDisabled(self, state):
        '''
        Handles the event from the toggling of the "Hide Disabled"
        toolbar or menu item.

        Argument
        state: The state of the checkbox causing the function to be called.
        '''
        self.conf.filter.disabled = state
        self.miHideDisabled.Check(state)
        self.cbHideDisabled.SetValue(state)
        self.updateFilter()

    def OnCbHideDisabled(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Disabled"
        toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideDisabled(self.cbHideDisabled.GetValue())

    def OnMiHideDisabled(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Disabled"
        menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideDisabled(self.miHideDisabled.IsChecked())

    def OnHideFound(self, state):
        '''
        Handles the event from the toggling of the "Hide Found"
        toolbar or menu item.

        Argument
        state: The state of the checkbox causing the function to be called.
        '''
        self.conf.filter.found = state
        self.miHideFound.Check(state)
        self.cbHideFound.SetValue(state)
        self.updateFilter()

    def OnCbHideFound(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Found"
        toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideFound(self.cbHideFound.GetValue())

    def OnMiHideFound(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Found"
        menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideFound(self.miHideFound.IsChecked())

    def OnHideMine(self, state):
        '''
        Handles the event from the toggling of the "Hide Mine"
        toolbar or menu item.

        Argument
        state: The state of the checkbox causing the function to be called.
        '''
        self.conf.filter.mine = state
        self.miHideMine.Check(state)
        self.cbHideMine.SetValue(state)
        self.updateFilter()

    def OnCbHideMine(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Mine
        toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideMine(self.cbHideMine.GetValue())

    def OnMiHideMine(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Mine"
        menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideMine(self.miHideMine.IsChecked())

    def OnHideOverDist(self, state):
        '''
        Handles the event from the toggling of the "Hide Over Distance"
        toolbar or menu item.

        Argument
        state: The state of the checkbox causing the function to be called.
        '''
        self.conf.filter.overDist = state
        self.miHideOverDist.Check(state)
        self.cbHideOverDist.SetValue(state)
        self.updateFilter()

    def OnCbHideOverDist(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Over Distance"
        toolbar item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideOverDist(self.cbHideOverDist.GetValue())

    def OnMiHideOverDist(self, event=None):
        '''
        Handles the event from the toggling of the "Hide Over Distance"
        menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.OnHideOverDist(self.miHideOverDist.IsChecked())

    def OnMaxDistVal(self, event=None):
        '''
        Handles the event from double clicking on the maximum distance box or
        selecting the "Set Maximum Distance" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        dlg = wx.TextEntryDialog(self,
            _('Please enter the maximum distance from your home location to display caches from'),
            caption=_('Maximum Distance'),
            defaultValue=str(self.conf.filter.maxDistVal or 50.0),
            style=wx.OK | wx.CANCEL)
        bad = True
        while bad:
            response = dlg.ShowModal() == wx.ID_OK
            if response:
                try:
                    dist = float(dlg.GetValue())
                    bad = False
                except:
                    errdlg = wx.MessageDialog(
                        self, 'Please enter a decimal number for the maximum distance',
                        caption='Bad Maximum Distance',
                        style=wx.OK)
                    errdlg.ShowModal()
                    errdlg.Destroy()
            else:
                bad = False
        dlg.Destroy()
        if response:
            self.conf.filter.maxDistVal = dist
            self.tbMaxDistance.SetValue(str(dist))
            self.updateFilter()
    def OnViewStats(self, event=None):
        '''
        Handles view statistics menu event.
        exiting.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        stats = cacheStats(self.db, self.conf)
        dlg = ViewHtml(self, wx.ID_ANY,stats.html(), 'Geocaching Stats')
        dlg.ShowModal()

    def OnQuit(self, event=None):
        '''
        Handles the exit application event saving the necessary data before
        exiting.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        (self.conf.common.mainWidth,self.conf.common.mainHeight) = self.GetSizeTuple()
        self.conf.common.mainSplit = self.splitter.GetSashPosition()
        self.conf.common.cacheCols = self.cacheGrid.GetCols()
        (self.conf.common.sortCol,self.conf.common.sortDecending) = self.cacheGrid.GetSort()
        if self.displayCache != None:
            self.conf.common.dispCache = self.displayCache.code
        else:
            self.conf.common.dispCache = ''
        self.conf.save()
        self.db.save()
        self.Destroy()

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
            geocacher = Geocacher(True)
            conf = geocacher.conf
            db = geocacher.db
            frame = MainWindow(None,-1,conf, db)
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
