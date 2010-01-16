# -*- coding: UTF-8 -*-
import os.path

import wx
import wx.xrc as Xrc

class ExportOptions(wx.Dialog):
    '''Get the export options from the user'''
    def __init__(self,parent,conf,gps=False):
        '''
        Initialises the dialog from the supplied information

        Arguments:
        parent: The parent window
        conf:   The configuration object
        Keyword Argument
        gps:    True if the dialog is for exporting to GPS rather than file
        '''
        self.conf = conf
        self.gps = gps
        self.gpx = False
        self.zip = False

        self.types = ['simple','full','custom']

        pre = wx.PreDialog()
        self.res = Xrc.XmlResource('xrc\geocacher.xrc')
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

        self.type = Xrc.XRCCTRL(self, 'typeRadioBox')

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
        self.Bind(wx.EVT_RADIOBOX, self.OnChangeType, self.type)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleGc, self.gc)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleAddWpts, self.addWpts)

        self.Bind(wx.EVT_CHECKBOX, self.OnToggleAdjWpts, self.adjWpts)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleLimitLogs, self.limitLogs)

        self.displayed.SetValue(self.conf.export.filterDisp or False)
        self.selected.SetValue(self.conf.export.filterSel or False)
        self.userFlag.SetValue(self.conf.export.filterUser or False)

        if gps:
            self.path.Disable()
            self.path.Hide()
            self.sepAddWpts.Hide()
            self.gpx = True
        else:
            self.gpsLabel.Hide()
            if os.path.isfile(self.conf.export.lastFile):
                self.path.SetPath(self.conf.export.lastFile)
                ext = os.path.splitext(self.conf.export.lastFile)[1]
                if ext == '.zip':
                    self.zip = True
                    self.gpx = True
                elif ext == '.gpx':
                    self.gpx = True

        self.type.Disable()
        self.gc.Disable()
        self.logs.Disable()
        self.tbs.Disable()
        self.addWpts.Disable()
        self.sepAddWpts.Disable()
        if self.gpx:
            self.type.Enable()
            if type == self.types[0]:
                self.type.SetSelection(0)
            elif type == self.types[1]:
                self.type.SetSelection(1)
                if self.zip:
                    self.sepAddWpts.Enable()
                    self.sepAddWpts.SetValue(self.conf.sepAddWpts or False)
            else:
                self.type.SetSelection(2)
                self.gc.Enable()
                self.gc.SetValue(conf.export.gc or False)
                if self.gc.GetValue():
                    self.logs.Enable()
                    self.logs.SetValue(conf.export.logs or False)
                    self.tbs.Enable()
                    self.tbs.SetValue(conf.export.tbs or False)
                self.addWpts.Enable()
                self.addWpts.SetValue(conf.export.addWpts or False)
                if self.zip and self.addWpts.GetValue():
                    self.sepAddWpts.Enable()
                    self.sepAddWpts.SetValue(conf.export.sepAddWpts or False)

        self.adjWpts.SetValue(conf.export.adjWpts or False)
        self.adjWptSufix.SetValue(conf.export.adjWptSufix or '')
        if not self.adjWpts.GetValue():
            self.adjWptSufix.Disable()

        self.limitLogs.SetValue(conf.export.limitLogs or False)
        self.maxLogs.SetValue(conf.export.maxLogs or 4)
        if not self.limitLogs.GetValue():
            self.maxLogs.Disable()
        self.logOrder.SetSelection(conf.export.logOrder or 0)

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
            self.type.Enable()
        else:
            self.type.SetSelection(0)
            self.type.Disable()
            self.gc.SetValue(False)
            self.gc.Disable()
            self.logs.SetValue(False)
            self.logs.Disable()
            self.tbs.SetValue(False)
            self.tbs.Disable()

        if self.zip and (self.type.GetSelection()==1 or
                         (self.type.GetSelection()==2 and
                          self.addWpts.GetValue())):
            self.sepAddWpts.Enable()

    def OnChangeType(self, event=None):
        '''
        Handles changing of the export type enables/disables the geocahhing.com
        extensions and the separation of additional way points as necessary
        '''
        if self.type.GetSelection() == 2:
            print 'ccc'
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
            if self.zip and self.type.GetSelection() == 1:
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
        return self.types[self.type.GetSelection()]

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

    def GetAdjWpts(self):
        '''
        Returns True if exporting of additional way points is enabled
        '''
        return self.addWpts.GetValue()

    def GetMaxLogs(self):
        '''
        Returns True if exporting of additional way points is enabled
        '''
        if self.maxLogs.GetValue():
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
        self.conf.export.filterDisp = self.displayed.GetValue()
        self.conf.export.filterSel = self.selected.GetValue()
        self.conf.export.filterUser = self.userFlag.GetValue()

        self.conf.export.lastFile = self.path.GetPath()

        self.conf.export.type = self.types[self.type.GetSelection()]

        self.conf.export.gc = self.gc.GetValue()
        self.conf.export.logs = self.logs.GetValue()
        self.conf.export.tbs = self.tbs.GetValue()

        self.conf.export.addWpts = self.addWpts.GetValue()
        self.conf.export.sepAddWpts = self.sepAddWpts.GetValue()

        self.conf.export.adjWpts = self.adjWpts.GetValue()
        self.conf.export.adjWptSufix = self.adjWptSufix.GetValue()
        self.conf.export.limitLogs = self.limitLogs.GetValue()
        self.conf.export.maxLogs = self.maxLogs.GetValue()
        self.conf.export.logOrder = self.logOrder.GetSelection()
