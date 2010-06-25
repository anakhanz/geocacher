# -*- coding: UTF-8 -*-
'''
Module to implement the main application window
'''

import logging
import optparse
import os
import shutil
import tempfile
import zipfile

import wx
import wx.lib.inspection
from wx.lib.pubsub import Publisher as Publisher
import wx.html as Html

import geocacher
import geocacher.__version__

__version__ = geocacher.__version__.gcVERSION_NUMBER

from geocacher.widgets.cacheGrid import CacheGrid

from geocacher.libs.common import nl2br, listFiles
from geocacher.libs.cacheStats import cacheStats
from geocacher.libs.gpsbabel import GpsCom
from geocacher.libs.gpx import gpxLoad, gpxExport, zipLoad, zipExport
from geocacher.libs.loc import locLoad, locExport

from geocacher.dialogs.cacheChanges import CacheChanges
from geocacher.dialogs.export import ExportOptions
from geocacher.dialogs.preferences import Preferences
from geocacher.dialogs.viewHtml import ViewHtml

STATUS_MAIN = 0
STATUS_SHOWN = 1
STATUS_TOTAL = 2
STATUS_FILTERED = 3

class MainWindow(wx.Frame):
    '''
    The main frome for the application.
    '''
    def __init__(self,parent,id):
        '''
        Initialisation for the main frame.

        Arguments
        parent: The parent window of the frame.
        id:     The ID to give the frame.
        '''
        self.displayCache = None
        size = geocacher.config().mainWinSize
        # check that the Current location is in the db
        if geocacher.config().currentLocation not in geocacher.db().getLocationNameList():
            geocacher.config().currentLocation = geocacher.db().getLocationNameList()[0]
        wx.Frame.__init__(self,parent,wx.ID_ANY,_("Geocacher"),size = (size),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        self.buildStatusBar()

        self.buildMenu()

        self.buildToolBar()

        self.splitter = wx.SplitterWindow(self, wx.ID_ANY,
                                          style=wx.SP_LIVE_UPDATE | wx.SP_BORDER)
        self.cacheGrid = CacheGrid(self.splitter)
        self.Description = Html.HtmlWindow(self.splitter, wx.ID_ANY, name="Description Pannel")
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.cacheGrid,
                                        self.Description,
                                        geocacher.config().detailSplit)

        self.updateStatus()

        self.displayedCache = None
        self.updateDetail(geocacher.config().displayedCache)

        Publisher.subscribe(self.updateDetailMsg, 'cache.selected')
        Publisher.subscribe(self.NewLocationMsg, 'location.new')
        Publisher.subscribe(self.popStatusMsg, 'status.pop')
        Publisher.subscribe(self.pushStatusMsg, 'status.push')
        Publisher.subscribe(self.updateStatusMsg, 'status.update')

    def test(self,message):
        print message

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
        self.miShowFilter.Check(geocacher.config().showFilter)
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
        self.miHideMine.Check(geocacher.config().filterMine)

        self.miHideFound = FilterMenu.Append(wx.ID_ANY,
                                             text=_('Hide &Found'),
                                             kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideFound, self.miHideFound)
        self.miHideFound.Check(geocacher.config().filterFound)

        self.miHideDisabled = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Disabled'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideDisabled, self.miHideDisabled)
        self.miHideDisabled.Check(geocacher.config().filterDisabled)

        self.miHideArchived = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Archived'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideArchived, self.miHideArchived)
        self.miHideArchived.Check(geocacher.config().filterArchived)

        self.miHideOverDist = FilterMenu.Append(wx.ID_ANY,
                                                text=_('Hide &Over Max Dist'),
                                                kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnMiHideOverDist, self.miHideOverDist)
        self.miHideOverDist.Check(geocacher.config().filterOverDist)

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

        item = HelpMenu.Append(wx.ID_ANY, text=_("&Inspector"))
        self.Bind(wx.EVT_MENU, self.OnInspector, item)

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
        self.cbHideMine.SetValue(geocacher.config().filterMine)

        self.cbHideFound = wx.CheckBox(tb, wx.ID_ANY, _('Hide Found'))
        tb.AddControl(self.cbHideFound)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideFound, self.cbHideFound)
        self.cbHideFound.SetValue(geocacher.config().filterFound)

        self.cbHideDisabled = wx.CheckBox(tb, wx.ID_ANY, _('Hide Disabled'))
        tb.AddControl(self.cbHideDisabled)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideDisabled, self.cbHideDisabled)
        self.cbHideDisabled.SetValue(geocacher.config().filterDisabled)

        self.cbHideArchived = wx.CheckBox(tb, wx.ID_ANY, _('Hide Archived'))
        tb.AddControl(self.cbHideArchived)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideArchived, self.cbHideArchived)
        self.cbHideArchived.SetValue(geocacher.config().filterArchived)

        self.cbHideOverDist = wx.CheckBox(tb, wx.ID_ANY, _('Hide Over'))
        tb.AddControl(self.cbHideOverDist)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbHideOverDist, self.cbHideOverDist)
        self.cbHideOverDist.SetValue(geocacher.config().filterOverDist)

        self.tbMaxDistance = wx.TextCtrl(tb, wx.ID_ANY,
            value=str(geocacher.config().filterMaxDist), size=[100,-1])
        tb.AddControl(self.tbMaxDistance)
        self.tbMaxDistance.Bind(wx.EVT_LEFT_DCLICK, self.OnMaxDistVal)

        tb.AddSeparator()

        tb.AddControl(wx.StaticText(tb,
                                    wx.ID_ANY,
                                    _('Home location'),
                                    style=wx.TEXT_ATTR_FONT_ITALIC))
        choices = geocacher.db().getLocationNameList()
        if geocacher.config().currentLocation in choices:
            current = geocacher.config().currentLocation
        else:
            current = choices[0]
            geocacher.config().currentLocation = current
        self.selLocation = wx.ComboBox(tb, wx.ID_ANY,current,
                                       choices = choices,
                                       size=[150,-1],
                                       style=wx.CB_DROPDOWN|wx.CB_SORT)
        tb.AddControl(self.selLocation)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelLocation, self.selLocation)
        tb.Realize()

        self.ShowHideFilterBar(geocacher.config().showFilter)

    def buildStatusBar(self):
        '''
        Builds the status bar for the main window
        '''
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(4)
        self.statusbar.SetStatusWidths([-1,180,80,120])
        self.statusbar.SetStatusText(_('Geocacher - idle'),STATUS_MAIN)

    def pushStatusMsg(self,message):
        self.pushStatus(message.data)

    def pushStatus(self, text):
        '''
        Pushes the given text onto the stack for the current activity part of
        the ststus bar.

        Argument
        test: Text to push onto the stack.
        '''
        self.statusbar.PushStatusText(text, STATUS_MAIN)

    def popStatusMsg(self,message):
        self.popStatus()

    def popStatus(self):
        '''
        Removes the top item form the stack for the current activity part of
        the status bar.
        '''
        self.statusbar.PopStatusText(STATUS_MAIN)

    def updateStatusMsg(self, message):
        self.updateStatus(message.data)

    def updateStatus(self, rows=None):
        '''
        Updates the total number of caches and the number of caches after the
         filter the status bar.

         Keyword Arguments
         rows: the number of rows to use as the number of records after
               filtering.
        '''
        self.statusbar.SetStatusText(_('Total: %i') %
                                     geocacher.db().getNumberCaches(),
                                     STATUS_TOTAL)
        if rows==None:
            self.statusbar.SetStatusText(_('After Filter: %i') %
                                         self.cacheGrid.GetNumberRows(),
                                         STATUS_FILTERED)
        else:
            self.statusbar.SetStatusText(_('After Filter: %i') %
                                         rows,
                                         STATUS_FILTERED)

    def updateDetailMsg(self, message):
        self.updateDetail(message.data)

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
        newCacheObj = geocacher.db().getCacheByCode(newCache)
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

    def selectCaches(self, gps):
        '''
        Returns a list of cache objets for export based on the stored export
        preferences.
        '''
        if gps:
            geocacher.config().exportType = "gps"
        else:
            geocacher.config().exportType = "file"
        if geocacher.config().exportFilterSel:
            caches = self.cacheGrid.GetSelectedCaches()
        elif geocacher.config().exportFilterDisp:
            caches = self.cacheGrid.GetDisplayedCaches()
        else:
            caches = geocacher.db().getCacheList()
        if geocacher.config().exportFilterUser:
            filteredCaches = []
            for cache in caches:
                if cache.user_flag:
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
        for i in range(0,self.selLocation.GetCount()):
            self.selLocation.Delete(0)
        for location in geocacher.db().getLocationNameList():
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
        geocacher.config().currentLocation = name
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
        HelpAbout.SetName(geocacher.appname)
        HelpAbout.SetVersion(__version__)
        HelpAbout.SetCopyright(geocacher.appcopyright)
        for developer in geocacher.developers:
            HelpAbout.AddDeveloper(developer)
        HelpAbout.SetLicense(geocacher.getLicense())
        HelpAbout.SetWebSite(geocacher.website)
        HelpAbout.SetDescription(geocacher.appdescription)
        wx.AboutBox(HelpAbout)

    def OnInspector(self, event=None):
        '''
        Handles the event from the "Inspector" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        wx.lib.inspection.InspectionTool().Show()

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

        if os.path.isdir(geocacher.config().importFolder):
            dir = geocacher.config().importFolder
        else:
            dir = wx.StandardPaths.GetDocumentsDir(wx.StandardPaths.Get())

        dlg = wx.FileDialog(
            self, message=_("Choose a file to load"),
            defaultDir=dir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE
            )
        if os.path.isfile(geocacher.config().importFile):
            dlg.SetPath(geocacher.config().importFile)
            ext = os.path.splitext(geocacher.config().importFile)[1]
            if ext != '':
                if ext == '.gpx':
                    dlg.SetFilterIndex(0)
                elif ext == '.loc':
                    dlg.SetFilterIndex(1)
                elif ext == '.zip':
                    dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            geocacher.config().importFolder = dlg.GetDirectory()
            paths = dlg.GetPaths()
            geocacher.config().importFile = paths[0]
            options = [_('Update'),_('Replace')]
            dlg = wx.SingleChoiceDialog(self, _('Load option'),
                                        _('Type of file load'),
                                        choices=options,
                                        style=wx.CHOICEDLG_STYLE)
            if geocacher.config().importMode == 'replace':
                dlg.SetSelection(1)
            else:
                dlg.SetSelection(0)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    geocacher.config().importMode = 'update'
                else:
                    geocacher.config().importMode = 'replace'

                changes = {}
                for path in paths:
                    self.pushStatus(_('Loading caches from file: %s')% path)
                    changes[path] = self.LoadFile(path, geocacher.config().importMode)
                    self.popStatus()
                self.displayImportedChanges(changes)
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
        if os.path.isdir(geocacher.config().importFolder):
            dir = geocacher.config().importFolder

        else:
            dir = os.getcwd()#####

        dlg = wx.DirDialog(self, _('Select Folder to import waypoint files from'),
                                 defaultPath=dir,
                                 style=wx.DD_DEFAULT_STYLE
                                 | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            geocacher.config().importFolder = dir

            options = [_('Update'),_('Replace')]
            dlg = wx.SingleChoiceDialog(self, _('Load option'),
                                        _('Type of file load'),
                                        choices=options,
                                        style=wx.CHOICEDLG_STYLE)
            if geocacher.config().importMode == 'replace':
                dlg.SetSelection(1)
            else:
                dlg.SetSelection(0)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetSelection() == 0:
                    geocacher.config().importMode = 'update'
                else:
                    geocacher.config().importMode = 'replace'

                changes = {}
                addWptFiles = []
                for file in listFiles(dir):
                    if file.rfind('-wpts') >= 0:
                        addWptFiles.append(file)
                    else:
                        self.pushStatus(_('Loading caches from folder, processing file: %s') % file)
                        changes[file] = self.LoadFile(file, geocacher.config().importMode)
                        self.popStatus()
                for file in addWptFiles:
                    self.pushStatus(_('Loading caches from folder, processing file: %s') % file)
                    changes[file] = self.LoadFile(file, geocacher.config().importMode)
                    self.popStatus()
                self.displayImportedChanges(changes)
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
            sucess,changes= gpxLoad(path,mode=mode,
                                    userId=geocacher.config().GCUserID,
                                    userName=geocacher.config().GCUserName)
        elif ext == '.loc':
            sucess,changes = locLoad(path,mode=mode)
        elif ext == '.zip':
            sucess,changes = zipLoad(path,mode=mode,
                                    userId=geocacher.config().GCUserID,
                                    userName=geocacher.config().GCUserName)
        if sucess == False:
            wx.MessageDialog(self,
                             _('Could not import "%s" due to an error accessing the file') % path,
                             caption=_("File import error"),
                             style=wx.OK|wx.ICON_WARNING)
        return changes

    def displayImportedChanges(self,changes):
        '''
        Displays the changes in the DBfrom importing files to the user

        Argument
        changes: the changes that have been made to the DB
        '''
        dlg = CacheChanges(self, wx.ID_ANY, changes)
        dlg.ShowModal()
        dlg.Destroy()


    def OnExportWpt(self, event=None):
        '''
        Handles the event from the "Export Waypoints to file" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Exporting caches to file'))
        opts = ExportOptions(self, False)
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
                    question.Destroy()
                    self.popStatus()
                    return
            ext = os.path.splitext(path)[1]
            caches = self.selectCaches(False)
            if len(caches) == 0:
                wx.MessageBox(parent = self,
                                  message = _('With the current settings there is nothing to export!'),
                                  caption = _('Nothing to export'),
                                  style = wx.OK | wx.ICON_ERROR)
            else:
                if ext == '.loc':
                    ret = locExport(path, caches,
                                    correct    = opts.GetAdjWpts(),
                                    corMark    = opts.GetAdjWptSufix())
                elif ext == '.gpx':
                    ret = gpxExport(path, caches,
                                    full       = opts.GetType() == 'full',
                                    simple     = opts.GetType() == 'simple',
                                    gc         = opts.GetGc(),
                                    logs       = opts.GetLogs(),
                                    tbs        = opts.GetTbs(),
                                    addWpts    = opts.GetAddWpts(),
                                    correct    = opts.GetAdjWpts(),
                                    corMark    = opts.GetAdjWptSufix(),
                                    maxLogs    = opts.GetMaxLogs(),
                                    logOrderDesc = opts.GetLogsDecendingSort())
                elif ext == '.zip':
                    geocacher.config().exportSepAddWpts = opts.GetSepAddWpts()
                    ret = zipExport(path, caches,
                                    full       = opts.GetType() == 'full',
                                    simple     = opts.GetType() == 'simple',
                                    gc         = opts.GetGc(),
                                    logs       = opts.GetLogs(),
                                    tbs        = opts.GetTbs(),
                                    addWpts    = opts.GetAddWpts(),
                                    sepAddWpts = opts.GetSepAddWpts(),
                                    correct    = opts.GetAdjWpts(),
                                    corMark    = opts.GetAdjWptSufix(),
                                    maxLogs    = opts.GetMaxLogs(),
                                    logOrderDesc = opts.GetLogsDecendingSort())
                else:
                    ret = True
                    wx.MessageBox(parent = self,
                                  message = _('Error exporting to file: %s\n file type not supported') % path,
                                  caption = _('Way point export Error'),
                                  style = wx.OK | wx.ICON_ERROR)
                if not ret:
                    wx.MessageBox(parent = self,
                                  message = _('Error exporting to file: %s') % path,
                                  caption = _('Way point export Error'),
                                  style = wx.OK | wx.ICON_ERROR)
            self.popStatus()

    def OnBackupDb(self, event=None): ### SQL
        '''
        Handles the event from the "Backup Database" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Backing up the Database'))
        wildcard = "Zip (*.zip)|*.zip|"\
                   "XML (*.xml)|*.xml|"\
                   "Any Type (*.*)|*.*|"
        lastFile = geocacher.config().dbBackupFile
        lastDir = os.path.dirname(lastFile)
        if not os.path.isfile(lastFile):
            lastFile = ''
            if not os.path.isdir(lastDir):
                lastDir = wx.StandardPaths.GetDocumentsDir(wx.StandardPaths.Get())
        dlg = wx.FileDialog(
            self, message=_("Select file to backup the DB to"),
            defaultDir=lastDir,
            defaultFile=lastFile,
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

            geocacher.config().dbBackupFile = path
            zip = os.path.splitext(path)[1] == '.zip'
            if zip:
                realPath = path
                tempDir = tempfile.mkdtemp()
                path = os.path.join(tempDir,'backup.xml')
                archive = zipfile.ZipFile(realPath, mode='w', compression=zipfile.ZIP_DEFLATED)
            self.xmldb.backup(path)
            if zip:
                archive.write(path, os.path.basename(path).encode("utf_8"))
                archive.close()
                shutil.rmtree(tempDir)

        dlg.Destroy()
        self.popStatus()

    def OnRestoreDb(self, event=None): ### SQL
        '''
        Handles the event from the "Restore Database" menu item.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.pushStatus(_('Restoring database from file'))
        wildcard = "Zip (*.zip)|*.zip|"\
                   "XML (*.xml)|*.xml|"\
                   "Any Type (*.*)|*.*|"
        lastFile = geocacher.config().dbBackupFile
        lastDir = os.path.dirname(lastFile)
        if not os.path.isfile(lastFile):
            lastFile = ''
            if not os.path.isdir(lastDir):
                lastDir = wx.StandardPaths.GetDocumentsDir(wx.StandardPaths.Get())
        dlg = wx.FileDialog(
            self, message=_("Select file to restore the DB from"),
            defaultDir=lastDir,
            defaultFile=lastFile,
            wildcard=wildcard,
            style=wx.OPEN
            )
        error = False
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.popStatus()
            self.pushStatus(_('Restoring database from file: %s') % path)
            question = wx.MessageDialog(None,
                           message=_("Are you sure you want to replace the contents of the DB with ") + path + '?',
                           caption=_("Replace DB?"),
                           style=wx.YES_NO|wx.ICON_WARNING
                           )
            if question.ShowModal() == wx.ID_YES:
                geocacher.config().dbBackupFile = path
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
                    error = not self.xmldb.restore(path)
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
        dlg = Preferences(self, wx.ID_ANY)
        if dlg.ShowModal() == wx.ID_OK:
            self.cacheGrid.UpdateUserDataLabels()
            self.updateLocations()
            self.updateCurrentLocation(
                geocacher.config().currentLocation)
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
        geocacher.config().showFilter = show
        self.ShowHideFilterBar(show)

    def OnGpsUpload(self, event=None):
        '''
        Uploads caches to GPS
        '''
        self.pushStatus(_('Uploading caches to GPS'))
        opts = ExportOptions(self, True)
        if opts.ShowModal() == wx.ID_OK:
            opts.SaveConf()
            caches = self.selectCaches(True)
            if len(caches) == 0:
                wx.MessageBox(parent = self,
                                  message = _('With the current settings there is nothing to export!'),
                                  caption = _('Nothing to export'),
                                  style = wx.OK | wx.ICON_ERROR)
            else:
                fd,tmpFile = tempfile.mkstemp()
                if gpxExport(tmpFile, caches,
                            full       = opts.GetType() == 'full',
                            simple     = opts.GetType() == 'simple',
                            gc         = opts.GetGc(),
                            logs       = opts.GetLogs(),
                            tbs        = opts.GetTbs(),
                            addWpts    = opts.GetAddWpts(),
                            correct    = opts.GetAdjWpts(),
                            corMark    = opts.GetAdjWptSufix(),
                            maxLogs    = opts.GetMaxLogs(),
                            logOrderDesc = opts.GetLogsDecendingSort()):
                    gpsCom = GpsCom(gps=geocacher.config().gpsType,
                                    port=geocacher.config().gpsConnection)
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
        gpsCom = GpsCom(gps=geocacher.config().gpsType,
                        port=geocacher.config().gpsConnection)
        ok, lat, lon, message = gpsCom.getCurrentPos()
        if ok:
            self.NewLocation(lat, lon, _('the GPS'), _('GPS Point'))
        else:
            self.GpsError(message)
        self.popStatus()

    def NewLocationMsg(self,message):
        lat, lon, source, name = message.data
        self.NewLocation(lat, lon, source, name)

    def NewLocation(self, lat, lon, source, name=''): ### SQL
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
        if name in geocacher.db().getLocationNameList():
            dlg = wx.MessageDialog(self,
                message=_('Are you sure you want to replace the existing laocation named ')+name,
                caption=_('Replace Existing Location'),
                style=wx.YES_NO|wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                location = geocacher.db().getLocationByName(name)
                location.lat = lat
                location.lon = lon
            else:
                dlg.Destroy()
                return
        else:
            self.xmldb.addLocation(name, lat, lon)
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
        geocacher.config().filterArchived = state
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
        geocacher.config().filterDisabled = state
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
        geocacher.config().filterFound = state
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
        geocacher.config().filterMine = state
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
        geocacher.config().filterOverDist = state
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
            defaultValue=str(geocacher.config().filterMaxDist),
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
            geocacher.config().filterMaxDist = dist
            self.tbMaxDistance.SetValue(str(dist))
            self.updateFilter()
    def OnViewStats(self, event=None):
        '''
        Handles view statistics menu event.
        exiting.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        stats = cacheStats()
        dlg = ViewHtml(self, wx.ID_ANY,stats.html(), 'Geocaching Stats')
        dlg.ShowModal()

    def OnQuit(self, event=None):
        '''
        Handles the exit application event saving the necessary data before
        exiting.

        Keyword Argument
        event: The event causing this function to be called.
        '''
        geocacher.config().mainWinSize = self.GetSize()
        geocacher.config().detailSplit = self.splitter.GetSashPosition()
        geocacher.config().cacheColumnOrder = self.cacheGrid.GetCols()
        (geocacher.config().cacheSortColumn,
         geocacher.config().cacheSortDescend) = self.cacheGrid.GetSort()
        if self.displayedCache != None:
            geocacher.config().displayedCache = self.displayedCache
        else:
            geocacher.config().displayedCache = ''
        self.Destroy()
