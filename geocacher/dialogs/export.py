# -*- coding: UTF-8 -*-
import os.path

import wx
import wx.xrc as Xrc

import geocacher

class ExportOptions(wx.Dialog):
    '''Get the export options from the user'''
    def __init__(self,parent,gps=False):
        '''
        Initialises the dialog from the supplied information

        Arguments:
        parent: The parent window
        Keyword Argument
        gps:    True if the dialog is for exporting to GPS rather than file
        '''
        if gps:
            geocacher.config().exportType = "gps"
        else:
            geocacher.config().exportType = "file"
        self.gps = gps
        self.gpx = False
        self.zip = False

        self.types = ['simple','full','custom']

        pre = wx.PreDialog()
        self.res = Xrc.XmlResource(os.path.join(geocacher.getBasePath(), 'xrc', 'export.xrc'))
        self.res.LoadOnDialog(pre, parent, 'ExportWaypointDialog')
        self.PostCreate(pre)

        if gps:
            self.SetTitle(_('Export to GPS options'))
        else:
            self.SetTitle(_('Export to file options'))

        self.displayed = Xrc.XRCCTRL(self, 'displayedCheckBox')
        self.selected = Xrc.XRCCTRL(self, 'selectedCheckBox')
        self.userFlag = Xrc.XRCCTRL(self, 'userFlagCheckBox')

        self.path = Xrc.XRCCTRL(self, 'pathPicker')
        self.gpsLabel = Xrc.XRCCTRL(self, 'gpsLabel')

        self.exType = Xrc.XRCCTRL(self, 'typeRadioBox')

        self.gc = Xrc.XRCCTRL(self, 'extensionsCheckBox')

        self.logs = Xrc.XRCCTRL(self, 'logsCheckBox')
        self.tbs = Xrc.XRCCTRL(self, 'travelBugsCheckBox')
        self.addWpts = Xrc.XRCCTRL(self, 'addWptsCheckBox')

        self.sepAddWpts = Xrc.XRCCTRL(self, 'sepAddWptsCheckBox')

        self.adjWpts = Xrc.XRCCTRL(self, 'adjustedCheckBox')
        self.adjWptSufix = Xrc.XRCCTRL(self, 'adjWptSufixText')

        self.limitLogs = Xrc.XRCCTRL(self, 'limitLogsCheckBox')
        self.maxLogs = Xrc.XRCCTRL(self, 'limitLogsSpin')
        self.logOrder = Xrc.XRCCTRL(self, 'logSortRadioBox')

        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPathChanged, self.path)
        self.Bind(wx.EVT_RADIOBOX, self.OnChangeType, self.exType)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleGc, self.gc)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleAddWpts, self.addWpts)

        self.Bind(wx.EVT_CHECKBOX, self.OnToggleAdjWpts, self.adjWpts)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleLimitLogs, self.limitLogs)

        self.displayed.SetValue(geocacher.config().exportFilterDisp)
        self.selected.SetValue(geocacher.config().exportFilterSel)
        self.userFlag.SetValue(geocacher.config().exportFilterUser)

        if gps:
            self.path.Disable()
            self.path.Hide()
            self.sepAddWpts.Hide()
            self.gpx = True
        else:
            self.gpsLabel.Hide()
            if os.path.isfile(geocacher.config().exportFile):
                self.path.SetPath(geocacher.config().exportFile)
                ext = os.path.splitext(geocacher.config().exportFile)[1]
                if ext == '.zip':
                    self.zip = True
                    self.gpx = True
                elif ext == '.gpx':
                    self.gpx = True

        self.exType.Disable()
        self.gc.Disable()
        self.logs.Disable()
        self.tbs.Disable()
        self.addWpts.Disable()
        self.sepAddWpts.Disable()
        if self.gpx:
            self.exType.Enable()
            if (geocacher.config().exportScope) == self.types[0]:
                self.exType.SetSelection(0)
            elif (geocacher.config().exportScope) == self.types[1]:
                self.exType.SetSelection(1)
                if self.zip:
                    self.sepAddWpts.Enable()
                    self.sepAddWpts.SetValue(geocacher.config().exportSepAddWpts)
            else:
                self.exType.SetSelection(2)
                self.gc.Enable()
                self.gc.SetValue(geocacher.config().exportGc)
                if self.gc.GetValue():
                    self.logs.Enable()
                    self.logs.SetValue(geocacher.config().exportLogs)
                    self.tbs.Enable()
                    self.tbs.SetValue(geocacher.config().exportTbs)
                self.addWpts.Enable()
                self.addWpts.SetValue(geocacher.config().exportAddWpts)
                if self.zip and self.addWpts.GetValue():
                    self.sepAddWpts.Enable()
                    self.sepAddWpts.SetValue(geocacher.config().exportSepAddWpts)

        self.adjWpts.SetValue(geocacher.config().exportAdjWpts)
        self.adjWptSufix.SetValue(geocacher.config().exportAdjWptSufix)
        if not self.adjWpts.GetValue():
            self.adjWptSufix.Disable()

        self.limitLogs.SetValue(geocacher.config().exportLimitLogs)
        self.maxLogs.SetValue(geocacher.config().exportMaxLogs)
        if not self.limitLogs.GetValue():
            self.maxLogs.Disable()
        self.logOrder.SetSelection(geocacher.config().exportLogOrder)

    def OnPathChanged(self, event=None):
        '''
        Handles the changing of the export path and enables/disables the
        various expot options as necessary
        '''
        ext = os.path.splitext(self.path.GetPath())[1]

        self.zip = ext =='.zip'
        self.gpx = self.zip or ext =='.gpx'

        if not self.zip:
            self.sepAddWpts.Disable()
            self.sepAddWpts.SetValue(False)

        if self.gpx:
            self.exType.Enable()
        else:
            self.exType.SetSelection(0)
            self.exType.Disable()
            self.gc.SetValue(False)
            self.gc.Disable()
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()

        if self.zip and (self.exType.GetSelection()==1 or
                         (self.exType.GetSelection()==2 and
                          self.addWpts.GetValue())):
            self.sepAddWpts.Enable()

    def OnChangeType(self, event=None):
        '''
        Handles changing of the export type enables/disables the geocahhing.com
        extensions and the separation of additional way points as necessary
        '''
        if self.exType.GetSelection() == 2:
            self.gc.Enable()
            self.addWpts.Enable()
            if self.zip and self.addWpts.GetValue():
                self.sepAddWpts.Enable()
            else:
                self.sepAddWpts.SetValue(False)
                self.sepAddWpts.Disable()
        else:
            self.gc.SetValue(False)
            self.gc.Disable()
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()
            self.addWpts.SetValue(False)
            self.addWpts.Disable()
            if self.zip and self.exType.GetSelection() == 1:
                self.sepAddWpts.Enable()
            else:
                self.sepAddWpts.SetValue(False)
                self.sepAddWpts.Disable()

    def OnToggleGc(self, event=None):
        '''
        Handles the toggling of the geocaching.com extensions and
        enables/disables the sub options as necessary
        '''
        if self.gc.GetValue():
            self.logs.Enable()
            self.tbs.Enable()
            self.addWpts.Enable()
        else:
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()

    def OnToggleAddWpts(self, event=None):
        '''
        Handles toggling of the additional way points option and
        enables/disables the additional way points in a separate file option
        if necessary
        '''
        if self.zip and self.addWpts.GetValue():
            self.sepAddWpts.Enable()
        else:
            self.sepAddWpts.Disable()

    def OnToggleAdjWpts(self, event=None):
        '''
        Handles toggling of the adjust way points option and enables/disables
        the adjusted waypoints sufixin option as necessary
        '''
        if self.adjWpts.GetValue():
            self.adjWptSufix.Enable()
        else:
            self.adjWptSufix.Disable()

    def OnToggleLimitLogs(self, event=None):
        '''
        Handles toggling of the limit logs option and enables/disables the max
        logs option as necessary
        '''
        if self.limitLogs.GetValue():
            self.maxLogs.Enable()
        else:
            self.maxLogs.Disable()

    def GetDisplayed(self):
        '''
        Returns True if the "Displayed" filter option is checked
        '''
        return self.displayed.GetValue()

    def GetSelected(self):
        '''
        Returns True if the "Selected" filter option is checked
        '''
        return self.selected.GetValue()

    def GetUserFlag(self):
        '''
        Returns True if the "User Flag" filter option is checked
        '''
        return self.userFlag.GetValue()

    def GetPath(self):
        '''
        Returns the user selected path if not in GPS mode otherwise None
        '''
        if self.gps:
            return None
        else:
            return self.path.GetPath()

    def GetType(self):
        '''
        Returns the selected export type
        '''
        return self.types[self.exType.GetSelection()]

    def GetGc(self):
        '''
        Returns True if the geocaching.com extensions are enabled
        '''
        return self.gc.GetValue()

    def GetLogs(self):
        '''
        Returns True if Exporting of logs is enabled
        '''
        return self.logs.GetValue()

    def GetTbs(self):
        '''
        Returns True if exporting of Travel Bugs is enabled
        '''
        return self.tbs.GetValue()

    def GetAddWpts(self):
        '''
        Returns True if exporting of additional way points is enabled
        '''
        return self.addWpts.GetValue()

    def GetSepAddWpts(self):
        '''
        Returns True if the additional way points are to be exported to a
        separate file
        '''
        return self.sepAddWpts.GetValue()

    def GetAdjWpts(self):
        '''
        Returns True if using adjusted way points is enabled
        '''
        return self.adjWpts.GetValue()

    def GetAdjWptSufix(self):
        '''
        Returns True if exporting of additional way points is enabled
        '''
        return self.adjWptSufix.GetValue()

    def GetMaxLogs(self):
        '''
        Returns True if exporting of additional way points is enabled
        '''
        if self.limitLogs.GetValue():
            return self.maxLogs.GetValue()
        else:
            return None

    def GetLogsDecendingSort(self):
        '''
        Returns True if the logs are sorteed in a desending order
        '''
        return self.logOrder.GetSelection() == 0

    def SaveConf(self):
        '''
        Saves the values form the dialog to the configuration structure
        '''
        geocacher.config().exportFilterDisp = self.displayed.GetValue()
        geocacher.config().exportFilterSel = self.selected.GetValue()
        geocacher.config().exportFilterUser = self.userFlag.GetValue()

        if not self.gps:
            geocacher.config().exportFile = self.path.GetPath()

        geocacher.config().exportScope = self.types[self.exType.GetSelection()]

        geocacher.config().exportGc = self.gc.GetValue()
        geocacher.config().exportLogs = self.logs.GetValue()
        geocacher.config().exportTbs = self.tbs.GetValue()

        geocacher.config().exportAddWpts = self.addWpts.GetValue()
        geocacher.config().exportSepAddWpts = self.sepAddWpts.GetValue()

        geocacher.config().exportAdjWpts = self.adjWpts.GetValue()
        geocacher.config().exportAdjWptSufix = self.adjWptSufix.GetValue()
        geocacher.config().exportLimitLogs = self.limitLogs.GetValue()
        geocacher.config().exportMaxLogs = self.maxLogs.GetValue()
        geocacher.config().exportLogOrder = self.logOrder.GetSelection()
