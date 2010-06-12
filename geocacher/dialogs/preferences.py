# -*- coding: UTF-8 -*-

import os

import wx
import wx.grid             as  Grid

import geocacher

from geocacher.editors.deg import LatEditor, LonEditor

from geocacher.renderers.deg import LatRenderer, LonRenderer

from geocacher.validators.deg import LatValidator, LonValidator
from geocacher.validators.locName import LocNameValidator


class Preferences(wx.Dialog):
    '''
    Preferences Dialog
    '''
    def __init__(self,parent,id, db):
        '''
        Creates the Preferences Frame.

        Arguments
        parent: The parent window.
        id:     ID to give this dialog.
        db:     Application database.
        '''
        self.db = db
        self.labelWidth = 150
        self.entryWidth = 200
        wx.Dialog.__init__(self,parent,wx.ID_ANY,_("Preferences"),
                           size = (400,350),
                           style = wx.DEFAULT_FRAME_STYLE |
                            wx.NO_FULL_REPAINT_ON_RESIZE)

        nb = wx.Notebook(self)

        # Create the page windows as children of the notebook.
        self.Display   = self.__buildDisplayPanel(nb)
        self.GC        = self.__buildGCPanel(nb)
        self.GPS       = self.__buildGPSPanel(nb)
        self.Locations = self.__buildLocationsPanel(nb)

        # Add the pages to the notebook with the label to show on the tab.
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

        # finally, put the notebook and buttons in a sizer to manage the
        # layout.
        mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        mainSizer.Add(nb, 1, wx.EXPAND)
        mainSizer.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainSizer)

    def __buildDisplayPanel(self, parent):
        '''
        Builds the display preferences panel.

        Argument
        parent: the parent window for this panel.
        '''
        panel = wx.Panel(parent, wx.ID_ANY)

        displayGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('Units'),
            size = (self.labelWidth,-1))
        displayGrid.Add(label, (0,0))
        self.dispUnitsChoices = [_('Kilometers'), _('Miles')]
        if geocacher.config().imperialUnits:
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
            value=geocacher.config().coordinateFormat,
            choices=['hdd.ddddd', 'hdd mm.mmm', 'hdd mm ss.s'],
            style=wx.CB_READONLY,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispCoordFmt, (1,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('Icon Theme'))
        displayGrid.Add(label, (2,0))
        iconThemes=[]
        for folder in os.listdir(os.path.join(os.path.curdir,'gfx')):
            if os.path.isdir(os.path.join(os.path.curdir,'gfx',folder)):
                iconThemes.append(folder)
            iconThemes.sort()
        iconTheme = geocacher.config().iconTheme
        if iconTheme not in iconThemes:
            iconTheme = iconThemes[0]
        self.iconThemeSel = wx.ComboBox(panel, wx.ID_ANY,
            value=iconTheme,
            choices=iconThemes,
            style=wx.CB_READONLY,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.iconThemeSel, (2,1))

        label = wx.StaticText(panel,wx.ID_ANY,
            _('User Data Column Names'))
        displayGrid.Add(label, (3,0), (1,2))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 1'))
        displayGrid.Add(label, (4,0))
        self.dispUserData1 = wx.TextCtrl(panel, wx.ID_ANY,
            geocacher.config().userData1Label,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData1, (4,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 2'))
        displayGrid.Add(label, (5,0))
        self.dispUserData2 = wx.TextCtrl(panel, wx.ID_ANY,
            geocacher.config().userData2Label,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData2, (5,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 3'))
        displayGrid.Add(label, (6,0))
        self.dispUserData3 = wx.TextCtrl(panel, wx.ID_ANY,
            geocacher.config().userData4Label,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData3, (6,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User Data 4'))
        displayGrid.Add(label, (7,0))
        self.dispUserData4 = wx.TextCtrl(panel, wx.ID_ANY,
            geocacher.config().userData4Label,
            size = (self.entryWidth,-1))
        displayGrid.Add(self.dispUserData4, (7,1))

        panel.SetSizer(displayGrid)
        return panel

    def __saveDisplayConf(self):
        '''
        Saves the preferences from the display preferences panel.
        '''
        if self.dispUnits.GetValue() == self.dispUnitsChoices[0]:
            geocacher.config().imperialUnits = False
        else:
            geocacher.config().imperialUnits = True
        geocacher.config().coordinateFormat = self.dispCoordFmt.GetValue()
        geocacher.config().iconTheme = self.iconThemeSel.GetValue()
        geocacher.config().userData1Label = self.dispUserData1.GetValue()
        geocacher.config().userData2Label = self.dispUserData2.GetValue()
        geocacher.config().userData3Label = self.dispUserData3.GetValue()
        geocacher.config().userData4Label = self.dispUserData4.GetValue()

    def __buildGCPanel(self, parent):
        '''
        Builds the geocaching.com preferences panel.

        Argument
        parent: the parent window for this panel.
        '''
        panel = wx.Panel(parent, wx.ID_ANY)
        gcGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('User Name'),
            size = (self.labelWidth,-1))
        gcGrid.Add(label, (0,0))
        self.gcUserName = wx.TextCtrl(panel,
            wx.ID_ANY,geocacher.config().GCUserName,
            size = (self.entryWidth,-1))
        gcGrid.Add(self.gcUserName, (0,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('User ID'))
        gcGrid.Add(label, (1,0))
        self.gcUserId = wx.TextCtrl(panel,wx.ID_ANY,
            geocacher.config().GCUserID,
            size = (self.entryWidth,-1))
        gcGrid.Add(self.gcUserId, (1,1))

        panel.SetSizer(gcGrid)
        return panel

    def __saveGCConf(self):
        '''
        Saves the preferences from the geocaching.com preferences panel.
        '''
        geocacher.config().GCUserName = self.gcUserName.GetValue()
        geocacher.config().GCUserID = self.gcUserId.GetValue()

    def __buildGPSPanel(self,parent):
        '''
        Builds the GPS preferences panel.

        Argument
        parent: the parent window for this panel.
        '''
        panel = wx.Panel(parent, wx.ID_ANY)
        gpsGrid = wx.GridBagSizer(5, 5)

        label = wx.StaticText(panel,wx.ID_ANY,_('Type'),
            size = (self.labelWidth,-1))
        gpsGrid.Add(label, (0,0))
        self.gpsType = wx.ComboBox(panel, wx.ID_ANY,
            value=geocacher.config().gpsType,
            choices=['garmin'],
            style=wx.CB_SORT|wx.CB_READONLY,
            size = (self.entryWidth,-1))
        gpsGrid.Add(self.gpsType, (0,1))

        label = wx.StaticText(panel,wx.ID_ANY,_('Port'))
        gpsGrid.Add(label, (1,0))
        self.gpsConnection = wx.ComboBox(panel, wx.ID_ANY,
            value=geocacher.config().gpsConnection,
            choices=['usb:'],
            style=wx.CB_SORT,
            size = (self.entryWidth,-1))
        gpsGrid.Add(self.gpsConnection, (1,1))

        panel.SetSizer(gpsGrid)
        return panel

    def __saveGPSConf(self):

        '''
        Saves the preferences from the GPS preferences panel.
        '''
        geocacher.config().gpsType = self.gpsType.GetValue()
        geocacher.config().gpsConnection = self.gpsConnection.GetValue()

    def __buildLocationsPanel(self, parent):
        '''
        Builds the locations preferences panel.

        Argument
        parent: The parent window for this panel.
        '''
        grid = LocationsGrid(parent, self.db)
        return grid

    def __saveLocationsConf(self):
        '''
        Saves the preferences from the locations preferences panel.
        '''
        self.Locations.Save()

    def OnCancel(self, event=None):
        '''
        Handles the Cancel button
        '''
        self.Destroy()

    def OnOk(self, event=None):
        '''
        Handles the OK button and saves the preferences
        '''
        self.__saveDisplayConf()
        self.__saveGCConf()
        self.__saveGPSConf()
        self.__saveLocationsConf()

        event.Skip()


class LocationsDataTable(Grid.PyGridTableBase):
    def __init__(self, db):
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
        if geocacher.config().currentLocation not in newNames:
            geocacher.config().currentLocation = newNames[0]

    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the data set
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
            (self._rows, self.GetNumberRows(),
             Grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
             Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(),
             Grid.GRIDTABLE_NOTIFY_COLS_DELETED,
             Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),]:

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

    def _updateColAttrs(self, grid):
        """
        wx.Grid -> update the column attributes to add the
        appropriate renderer given the column name.
        """
        for col in range(len(self.colLabels)):
            attr = Grid.GridCellAttr()
            if self.renderers[col] != None:
                renderer = self.renderers[col](self)
                attr.SetRenderer(renderer)

                if renderer.colSize:
                    grid.SetColSize(col, renderer.colSize)

                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)

            if self.editors[col] != None:
                attr.SetEditor(self.editors[col]())

            grid.SetColAttr(col, attr)


class LocationsGrid(Grid.Grid):
    def __init__(self, parent, db):
        Grid.Grid.__init__(self, parent, wx.ID_ANY)

        self._table = LocationsDataTable(db)

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

        menu = wx.Menu()
        menu.Append(addID, _('Add Location'))
        if row != -1:
            menu.Append(editID, _('Edit Location'))
            if self._table.GetNumberRows() > 1:
                menu.Append(deleteID, _('Delete Location'))

        def add(event, self=self, row=row):
            data = {'name':'',
                    'lat' :0,
                    'lon' :0}
            names = self._table.GetNames()
            dlg = EditLocation(self, wx.ID_ANY, data, names, True)
            if dlg.ShowModal() == wx.ID_OK:
                self._table.AddRow([data['name'], data['lat'], data['lon']])
                self.Reset()

        def edit(event, self=self, row=row):
            data = {'name':self._table.GetValue(row,0),
                    'lat' :self._table.GetValue(row,1),
                    'lon' :self._table.GetValue(row,2)}
            names = self._table.GetNames()
            dlg = EditLocation(self, wx.ID_ANY, data, names, False)
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
    def __init__(self,parent,id, data, names, new):
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
            validator=LatValidator(data, 'lat', new))
        lon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(data, 'lon', new))

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
