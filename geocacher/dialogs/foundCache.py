# -*- coding: UTF-8 -*-

import wx
import wx.xrc as Xrc

class FoundCache(wx.Dialog):
    '''
    Dialog to get date and Log Text for marking a cache as Found/DNF
    '''
    def __init__(self,parent,cache,markType,date=None, logText='',encoded=False):
        '''
        Initialises the View Travel Bugs Frame
        
        Arguments
        parent: The parent window for the dialog.
        cache:  The cache object to display the travel bugs from.
        '''
        pre = wx.PreDialog()
        self.res = Xrc.XmlResource('xrc\geocacher.xrc')
        self.res.LoadOnDialog(pre, parent, 'FoundCacheDialog')
        self.PostCreate(pre)

        self.SetTitle(_('Mark cache ') + cache + _(' as ') + markType)

        self.date = Xrc.XRCCTRL(self, 'datePick')
        self.logText = Xrc.XRCCTRL(self, 'logText')
        self.encodeLog = Xrc.XRCCTRL(self, 'encodeLogCb')

        if date != None:
            self.date.SetValue(wx.DateTimeFromDMY(date.day,date.month-1,date.year))
        if logText == None:
            logText = ''
        self.logText.SetValue(logText)
        self.encodeLog.SetValue(encoded)