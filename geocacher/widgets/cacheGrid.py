# -*- coding: UTF-8 -*-
'''
Module to implement the cache information grid
'''

from datetime import datetime

import wx
from wx.lib.pubsub import Publisher as Publisher

import wx.grid             as  Grid
import wx.lib.gridmovers   as  Gridmovers

import geocacher

from geocacher.widgets.cacheDataTable import CacheDataTable

from geocacher.libs.common import wxDateTimeToPy

from geocacher.dialogs.correctLatLon import CorrectLatLon
from geocacher.dialogs.foundCache import FoundCache
from geocacher.dialogs.viewLogs import ViewLogs
from geocacher.dialogs.viewTravelBugs import ViewTravelBugs

class CacheGrid(Grid.Grid):
    '''
    Grid to display the cache information.
    '''
    def __init__(self, parent):
        '''
        Initialisation function for the grid

        Argumnets
        parent:  Parent window for the grid.
        '''
        Grid.Grid.__init__(self, parent, -1)

        self._table = CacheDataTable()

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
            Publisher.sendMessage('cache.selected',
                                  self._table.GetRowCode(evt.GetRow()))
        evt.Skip()

    def OnCellLeftClicked(self, evt):
        '''
        Event handler for left click events on grid cells.

        Argumnet
        evt: Event object.
        '''
        Publisher.sendMessage('cache.selected',
                              self._table.GetRowCode(evt.GetRow()))
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
        Handler caled form all grid right click handlers to perform the actual
        event handling and generate the the context sensitive menu.

        Argumnet
        evt: Event object.
        '''
        row, col = evt.GetRow(), evt.GetCol()
        if row != -1:
            cache = self._table.GetRowCache(row)
        else:
            cache = None

        # Build Append/Insert Column
        activeColNames = self._table.GetCols()

        # Build a list mapping column display names to table cloum names
        colDispName=[]
        for colName in self._table.GetAllCols():
            if colName not in activeColNames:
                colDispName.append([self._table.GetColLabelValueByName(colName), colName])
        colDispName.sort()
        # build the append column menu and the dictionary mapping the ID of the
        # selected menu item to the table column name

        if len(colDispName) > 0:
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

        # Column pop-up
        def colDelete(event, self=self, col=col):
            '''Delete (Hide) the selected columns'''
            cols = self.GetSelectedCols()
            if len(cols) == 0:
                cols = [col]
            self._table.DeleteCols(cols)
            self.Reset()

        def colSortAscending(event, self=self, col=col):
            '''Perform an ascending sort on the selected column'''
            Publisher.sendMessage('status.push',_('Sorting caches'))
            self._table.SortColumn(col, False)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def colSortDescending(event, self=self, col=col):
            '''Perform an descending sort on the selected column'''
            Publisher.sendMessage('push.status',_('Sorting caches'))
            self._table.SortColumn(col, True)
            self.Reset()
            Publisher.sendMessage('status.pop')

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

        # Row pop-up

        def cacheDelete(event, self=self, row=row):
            '''Delete the selected cache(s) (row(s))'''
            Publisher.sendMessage('status.push',_('Deleting caches'))
            rows = self.GetSelectedRows()
            if len(rows) == 0:
                rows = [row]
            self._table.DeleteRows(rows)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def cacheAvail(event, self=self, row=row, cache=cache):
            '''Mark the selected cache (row) as available'''
            if cache.archived:
                dlg = wx.MessageDialog(None,
                message=_('Are you sure you want un-archive %s and mark it as available ') % cache.code,
                caption=_('Un-archive cache'),
                style=wx.YES_NO|wx.ICON_QUESTION)
                if dlg.ShowModal() == wx.ID_YES:
                    dlg.Destroy()
                    cache.archived = False
                else:
                    dlg.Destroy()
                    return
            Publisher.sendMessage('status.push',
                                  _('Marking cache %s as available') % cache.code)
            cache.available = True
            cache.user_date = datetime.now()
            cache.save()
            geocacher.db().commit()
            self._table.ReloadRow(row)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def cacheUnAvail(event, self=self, row=row, cache=cache):
            '''Mark the selected cache (row) as un-available'''
            Publisher.sendMessage('status.push',
                                  _('Marking cache %s as un-available') % cache.code)
            cache.available = False
            cache.user_date = datetime.now()
            cache.save()
            geocacher.db().commit()
            self._table.ReloadRow(row)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def cacheArc(event, self=self, row=row, cache=cache):
            '''Mark the selected cache (row) as archived'''
            Publisher.sendMessage('status.push',
                                  _('Archiving cache: %s') % cache.code)
            cache.available = False
            cache.archived = True
            cache.user_date = datetime.now()
            cache.save()
            geocacher.db().commit()
            self._table.ReloadRow(row)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def cacheUnArc(event, self=self, row=row, cache=cache):
            '''Mark the selected cache (row) as un-archived'''
            Publisher.sendMessage('status.push',
                                  _('Un-archiving cache: %s') % cache.code)
            cache.archived = False
            cache.user_date = datetime.now()
            cache.save()
            geocacher.db().commit()
            self._table.ReloadRow(row)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def cacheCorrect(event, self=self, row=row, cache=cache):
            '''Add/Edit Correction of the Lat/Lon for the selected cache (row)'''
            self.SelectRow(row)
            #cache = self._table.GetRowCache(row)
            # create data dictionary for the dialog and it's validators
            data = {'lat': cache.lat, 'lon': cache.lon,
                    'clat': cache.clat, 'clon': cache.clon,
                    'cnote': cache.cnote}
            dlg = CorrectLatLon(self, wx.ID_ANY, cache.code, data,
                not cache.corrected)
            # show the dialog and update the cache if OK clicked and there
            # where changes
            if dlg.ShowModal() == wx.ID_OK and (data['clat'] != cache.clat or
                                                data['clon'] != cache.clon or
                                                data['cnote'] != cache.cnote):
                Publisher.sendMessage('status.push',_('Correcting cache: %s') % cache.code)
                cache.clat = data['clat']
                cache.clon = data['clon']
                cache.cnote = data['cnote']
                cache.corrected = True
                cache.user_date = datetime.now()
                cache.save()
                geocacher.db().commit()
                self._table.ReloadRow(row)
                self.Reset()
                Publisher.sendMessage('status.pop')
            dlg.Destroy()

        def cacheRemCorrection(event, self=self, row=row, cache=cache):
            '''Remove the Lat/Lon correction for the selected cache (row)'''
            self.SelectRow(row)
            dlg = wx.MessageDialog(None,
                message=_('Are you sure you want to remove the cordinate correction for ')+cache.code,
                caption=_('Remove Cordinate Correction'),
                style=wx.YES_NO|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                Publisher.sendMessage('status.push',
                                      _('Removing correction from cache: %s') % cache.code)
                cache.clat = 0.0
                cache.clon = 0.0
                cache.corrected = False
                cache.cnote = ''
                cache.user_date = datetime.now()
                cache.save()
                geocacher.db().commit()
                self._table.ReloadRow(row)
                self.Reset()
                Publisher.sendMessage('status.pop')
            dlg.Destroy()

        def cacheViewLogs(event, self=self, cache=cache):
            '''View the logs for the selected cache (row).'''
            self.SelectRow(row)
            dlg = ViewLogs(self, cache)
            dlg.ShowModal()
            dlg.Destroy()

        def cacheViewBugs(event, self=self, cache=cache):
            '''View the travel bugs for the selected cache (row).'''
            self.SelectRow(row)
            dlg = ViewTravelBugs(self, cache)
            dlg.ShowModal()
            dlg.Destroy()

        def cacheAsHome(event, self=self, cache=cache):
            Publisher.sendMessage('location.new', (cache.lat,
                                                   cache.lon,
                                                   'cache ' + cache.code,
                                                   'cache ' + cache.code))

        def cacheAddLog(found, self=self, cache=cache):
            if found:
                logType = 'Found It'
                logDate = cache.found_date
            else:
                logType = "Didn't find it"
                logDate = cache.dnf_date
            dlg = FoundCache(self, cache.code, logType,
                             logDate, cache.own_log,
                             cache.own_log_encoded)
            if dlg.ShowModal() == wx.ID_OK:
                Publisher.sendMessage('status.push',
                                      _('Marking cache %s as "%s"') % (cache.code, logType))
                newLog = cache.addLog(None,
                                      date        = wxDateTimeToPy(dlg.date.GetValue()),
                                      logType     = logType,
                                      finder_id   = geocacher.config().GCUserID,
                                      finder_name = geocacher.config().GCUserName,
                                      encoded     = dlg.encodeLog.GetValue(),
                                      text        = dlg.logText.GetValue())
                if found:
                    cache.found = True
                    cache.found_date = newLog.date
                else:
                    cache.dnf = True
                    cache.dnf_date = newLog.date
                cache.own_log_id = newLog.logId
                cache.user_date = datetime.now()
                cache.save()
                geocacher.db().commit()
                cache.refreshOwnLog()
                self._table.ReloadRow(row)
                self.Reset()
                Publisher.sendMessage('status.pop')
            dlg.Destroy()

        def cacheSetFound(event, self=self, cache=cache):
            cacheAddLog(True)

        def cacheSetDnf(event, self=self, cache=cache):
            cacheAddLog(False)

        # Non row/col pop-up functions
        def sortByCodeAscending(event, self=self):
            '''Perform an ascending sort based on the cache code'''
            Publisher.sendMessage('status.push', _('Sorting caches'))
            self._table.SortColumnName('code', False)
            self.Reset()
            Publisher.sendMessage('status.pop')

        def sortByCodeDescending(event, self=self):
            '''Perform an descending sort based on the cache code'''
            Publisher.sendMessage('status.push', _('Sorting caches'))
            self._table.SortColumnName('code', True)
            self.Reset()
            Publisher.sendMessage('status.pop')

        # Menu
        cacheDeleteID   = wx.NewId()
        cacheArcID      = wx.NewId()
        cacheUnArcID    = wx.NewId()
        cacheAvailID    = wx.NewId()
        cacheUnAvailID  = wx.NewId()
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

        # Build the pop-up menu
        menu = wx.Menu()
        if col == -1:
            item = menu.Append(sortByCodeAsID, _('Ascending Sort By Cache Code'))
            item.Enable(enable = not geocacher.config().cacheSortDescend)
            item = menu.Append(sortByCodeDsID, _('Descending Sort By Cache Code'))
            item.Enable(enable = geocacher.config().cacheSortDescend)
        else:
            menu.Append(colSortAsID, _('Ascending Sort By Column'))
            menu.Append(colSortDsID, _('Descending Sort By Column'))
        menu.AppendSeparator()
        if len(colDispName) > 0:
            menu.AppendMenu(wx.ID_ANY, _('Append Column'), appMenu)
            menu.AppendMenu(wx.ID_ANY, _('Insert Column'), insMenu)
        menu.Append(colDeleteID, _('Delete Column(s)'))
        if row >= 0:
            menu.AppendSeparator()
            menu.Append(cacheDeleteID, _('Delete Cache(s)'))
            if cache.archived:
                menu.Append(cacheUnArcID,_('Un-archive Cache'))
            else:
                menu.Append(cacheArcID,_('Archive Cache'))
            if cache.available:
                menu.Append(cacheUnAvailID,_('Mark Cache Un-available'))
            else:
                menu.Append(cacheAvailID,_('Mark Cache Available'))
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

        # Bind functions
        self.Bind(wx.EVT_MENU, cacheDelete, id=cacheDeleteID)
        self.Bind(wx.EVT_MENU, cacheArc, id=cacheArcID)
        self.Bind(wx.EVT_MENU, cacheUnArc, id=cacheUnArcID)
        self.Bind(wx.EVT_MENU, cacheAvail, id=cacheAvailID)
        self.Bind(wx.EVT_MENU, cacheUnAvail, id=cacheUnAvailID)
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
        Publisher.sendMessage('status.update', self.GetNumberRows())

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