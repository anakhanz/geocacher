# -*- coding: UTF-8 -*-
'''
Module to implement the cache information grid data table
'''

from datetime import datetime

import wx
import wx.grid             as  Grid

import geocacher

from geocacher.renderers.deg import LatRenderer, LonRenderer
from geocacher.renderers.dist import DistRenderer
from geocacher.renderers.image import CacheBearingRenderer
from geocacher.renderers.image import CacheSizeRenderer
from geocacher.renderers.image import CacheTypeRenderer

class CacheDataTable(Grid.PyGridTableBase):
    '''
    Provides the Grid Table implementation for the cache data display grid
    '''
    def __init__(self):
        '''
        Initialisation function for the cache grid.
        '''

        Grid.PyGridTableBase.__init__(self)

        self.colNames = geocacher.config().cacheColumnOrder

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

        self.ReloadCaches()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetCacheRows(self, cache_id=None):
        '''
        Reloads all of the caches in the table from the database.
        '''
        sql = '''
SELECT * FROM(
SELECT c.id AS id,
       c.code AS code,
       CASE WHEN c.corrected = 1 THEN c.cLat
            ELSE c.lat
       END AS lat,
       CASE WHEN c.corrected = 1 THEN c.cLon
            ELSE c.lon
       END AS lon,
       c.name AS name,
       c.url AS url,
       c.found AS found,
       c.type AS type,
       c.container AS size,
       c.difficulty AS difficulty,
       c.terrain AS terrain,
       CASE WHEN c.corrected = 1 THEN distance(c.cLat, c.cLon)
            ELSE distance(c.lat, c.lon)
       END AS distance,
       CASE WHEN c.corrected = 1 THEN bearing(c.cLat, c.cLon)
            ELSE bearing(c.lat, c.lon)
       END AS bearing,
       c.lat AS oLat,
       c.lon AS oLon,
       c.cLat AS cLat,
       c.cLon AS con,
       c.corrected AS corrected,
       c.available AS available,
       c.archived AS archived,
       c.state AS state,
       c.country AS country,
       c.owner AS owner,
       c.placed_by as placedBy,
       c.placed AS placed,
       c.user_date AS user_date,
       c.gpx_date AS gpx_date,
       (SELECT count(l.cache_id) FROM Logs l where l.cache_id = c.id) AS num_logs,
       (SELECT max(l.date) FROM Logs l where l.cache_id = c.id) AS last_log,
       (SELECT max(l.date) FROM Logs l where l.cache_id = c.id AND l.type = "Found it") AS last_found,
       (SELECT count(l.cache_id) FROM Logs l where l.cache_id = c.id AND l.type = "Found it") AS found_count,
       (SELECT count(t.cache_id) FROM Travelbugs t WHERE t.cache_id = c.id) = 0 AS has_tb,
       c.locked AS locked,
       c.ftf AS ftf,
       c.found AS found,
       c.found_date AS found_date,
       c.dnf AS dnf,
       c.dnf_date AS nf_date,
       c.source AS source,
       c.user_flag AS user_flag,
       c.user_data1 AS user_data1,
       c.user_data2 AS user_data2,
       c.user_data3 AS user_data3,
       c.user_data4 AS user_data4
FROM Caches c)
'''
        sqlParameters = []
        sqlConditions = []
        if cache_id is not None:
            sqlConditions.append('id = ?')
            sqlParameters.append(cache_id)
        if geocacher.config().filterMine:
            sqlConditions.append('owner != ?')
            sqlParameters.append(geocacher.config().GCUserName)
        if geocacher.config().filterFound:
            sqlConditions.append('found = 0')
        if geocacher.config().filterOverDist:
            sqlConditions.append('distance <= ?')
            sqlParameters.append(geocacher.config().filterMaxDist)
        if geocacher.config().filterArchived:
            sqlConditions.append('archived = 0')
        if geocacher.config().filterDisabled:
            sqlConditions.append('available = 1')
        first = True
        for condition in sqlConditions:
            if first:
                sql = sql + ' WHERE ' + condition
                first = False
            else:
                sql = sql + ' AND ' + condition
        sql = sql + ' ORDER BY ' + geocacher.config().cacheSortColumn
        if geocacher.config().cacheSortDescend:
            sql = sql + ' DESC'
        cur = geocacher.db().cursor()
        cur.execute(sql, sqlParameters)
        if cache_id is None:
            return cur.fetchall()
        else:
            return cur.fetchone()

    def ReloadCaches(self):
        self.data = self.GetCacheRows()

    def ReloadRow(self, row):
        '''
        Reloads the given row in the table from the database.

        Argument
        row: The row number to reload.
        '''
        rowData = self.GetCacheRows(self.data[row]['id'])
        if rowData is None:
            self.data.pop(row)
        else:
            self.data[row] = rowData

    def UpdateLocation(self):
        '''
        Updates the location based information in all cache rows.
        '''
        self.ReloadCaches()

    def UpdateUserDataLabels(self):
        '''
        Updates the user data column labels from the program configuration.
        '''
        self.colLabels['user_data1'] = geocacher.config().userData1Label
        self.colLabels['user_data2'] = geocacher.config().userData1Label
        self.colLabels['user_data3'] = geocacher.config().userData1Label
        self.colLabels['user_data4'] = geocacher.config().userData1Label

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
        if self.dataTypes[id] == Grid.GRID_VALUE_BOOL:
            value = bool(value)
        if id == 'locked':
            changed = (cache.locked != value)
            cache.locked = value
        elif not cache.locked:
            if id == 'ftf':
                changed = cache.ftf
                cache.ftf = value
            elif id == 'user_data1':
                changed = (cache.user_data1 != value)
                cache.user_data1 = value
            elif id == 'user_data2':
                changed = (cache.user_data2 != value)
                cache.user_data2 = value
            elif id == 'user_data3':
                changed = (cache.user_data3 != value)
                cache.user_data3 = value
            elif id == 'user_data4':
                changed = (cache.user_data4 != value)
                cache.user_data4 = value
            elif id == 'user_flag':
                changed = (cache.user_flag != value)
                cache.user_flag = value
            else:
                changed = False
        else:
            changed = False
        if changed:
            cache.user_date = datetime.now()
            cache.save()
            geocacher.db().commit()
            ## TODO check if moified column is sorted of filtered by, if so do a complete refresh
            self.ReloadRow(row)
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
        return geocacher.db().getCacheByCode(self.GetRowCode(row))

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
            caches.append(geocacher.db().getCacheByCode(row['code']))
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
                geocacher.db().getCacheByCode(self.data[row-deleteCount]['code']).delete()
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
                descending = (not geocacher.config().cacheSortDescend) and (geocacher.config().cacheSortColumn == name)
            if (geocacher.config().cacheSortColumn != name) or (geocacher.config().cacheSortDescend != descending):
                geocacher.config().cacheSortColumn = name
                geocacher.config().cacheSortDescend = descending
                self.ReloadCaches()

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
                renderer = self.renderers[colName](self)

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