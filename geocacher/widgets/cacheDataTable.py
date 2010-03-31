# -*- coding: UTF-8 -*-
'''
Module to implement the cache information grid data table
'''

from datetime import datetime

import wx
import wx.grid             as  Grid

from geocacher.libs.common import dateCmp
from geocacher.libs.latlon import distance, cardinalBearing

from geocacher.renderers.deg import LatRenderer, LonRenderer
from geocacher.renderers.dist import DistRenderer
from geocacher.renderers.image import CacheBearingRenderer
from geocacher.renderers.image import CacheSizeRenderer
from geocacher.renderers.image import CacheTypeRenderer

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
        self._sortDescend = self.conf.common.sortDescending or False

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
        dist, cBear = self.__calcDistBearing(cache)
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