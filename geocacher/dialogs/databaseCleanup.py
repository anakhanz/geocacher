# -*- coding: UTF-8 -*-
import os.path

import wx
import wx.xrc as Xrc

import geocacher

class DatabaseCleanupOptions(wx.Dialog):
    '''Get the database clean-up options from the user'''
    def __init__(self,parent):
        '''
        Initialises the dialog from the supplied information

        Arguments:
        parent: The parent window
        '''

        self.actions = ['none', 'archive', 'delete']

        config = geocacher.config()

        pre = wx.PreDialog()
        self.res = Xrc.XmlResource(os.path.join(geocacher.getBasePath(), 'xrc', 'databaseCleanup.xrc'))
        self.res.LoadOnDialog(pre, parent, 'DatabaseCleanupDialog')
        self.PostCreate(pre)

        self.backup = Xrc.XRCCTRL(self, 'backupCheckBox')
        self.cacheAction = Xrc.XRCCTRL(self, 'cacheActionRadioBox')
        self.cacheAge = Xrc.XRCCTRL(self, 'cacheAgeSpinCtrl')
        self.logAge = Xrc.XRCCTRL(self, 'logAgeSpinCtrl')
        self.indexes = Xrc.XRCCTRL(self, 'indexesCheckBox')
        self.compact = Xrc.XRCCTRL(self, 'compactCheckBox')

        self.Bind(wx.EVT_RADIOBOX, self.OnChangeAction, self.cacheAction)

        self.backup.SetValue(config.cleanupBackup)
        if (config.cleanupCacheAct) == self.actions[0]:
            self.cacheAction.SetSelection(0)
        elif (config.cleanupCacheAct) == self.actions[1]:
            self.cacheAction.SetSelection(1)
        else:
            self.cacheAction.SetSelection(2)
        self.cacheAge.SetValue(config.cleanupCacheAge)
        self.logAge.SetValue(config.cleanupLog)
        self.indexes.SetValue(config.cleanupIndexes)
        self.compact.SetValue(config.cleanupCompact)

        if config.cleanupCacheAct == self.actions[0]:
            self.cacheAge.Disable()

    def OnChangeAction(self, event=None):
        '''
        Handles changing of the cache action enables/disables the cache age
        control
        '''
        if self.cacheAction.GetSelection() == 0:
            self.cacheAge.Disable()
        else:
            self.cacheAge.Enable()

    def SaveConf(self):
        '''
        Saves the values form the dialog to the configuration structure
        '''
        config = geocacher.config()
        config.cleanupBackup = self.backup.GetValue()
        config.cleanupCacheAct = self.actions[self.cacheAction.GetSelection()]
        config.cleanupCacheAge = self.cacheAge.GetValue()
        config.cleanupLog = self.logAge.GetValue()
        config.cleanupIndexes = self.indexes.GetValue()
        config.cleanupCompact = self.compact.GetValue()