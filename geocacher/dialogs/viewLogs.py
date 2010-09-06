# -*- coding: UTF-8 -*-

import os.path

import wx
import wx.lib.scrolledpanel as Scrolled
import wx.xrc as Xrc

import geocacher

class ViewLogs(wx.Dialog):
    '''
    View Logs Dialog
    '''
    def __init__(self,parent,cache):
        '''
        Initialises the View Logs dialog.

        Arguments
        parent: The parent window for the dialog.
        cache:  The cache object to display the logs from.
        '''

        wx.Dialog.__init__(self,parent,wx.ID_ANY,_("Logs for ")+cache.code,size = (650,500),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create a scrolled panel and a vertical sizer within it to take the logs
        sw = Scrolled.ScrolledPanel(self, -1, size=(640, 450),
                                 style = wx.TAB_TRAVERSAL)
        logSizer = wx.BoxSizer(orient=wx.VERTICAL)

        res = Xrc.XmlResource(os.path.join(geocacher.getBasePath(), 'xrc', 'logPanel.xrc'))

        # Create a block for each log and add it to the logs sizer
        for log in cache.getLogs():
            logPanel = res.LoadPanel(sw, 'logPanel')
            date     = Xrc.XRCCTRL(logPanel, 'dateText')
            logType     = Xrc.XRCCTRL(logPanel, 'typeText')
            finder   = Xrc.XRCCTRL(logPanel, 'finderText')
            message  = Xrc.XRCCTRL(logPanel, 'messageText')

            date.SetValue(log.date.strftime("%x"))
            logType.SetValue(log.logType)
            finder.SetValue(log.finder_name)
            message.SetValue(log.text)

            logSizer.Add(logPanel)

        # Final Setup of the scrolled panel
        sw.SetSizer(logSizer)
        sw.SetAutoLayout(1)
        sw.SetupScrolling()

        # Buttons
        closeButton = wx.Button(self,wx.ID_CLOSE)

        self.Bind(wx.EVT_BUTTON, self.OnClose,closeButton)

        buttonBox = wx.BoxSizer(orient=wx.HORIZONTAL)
        buttonBox.Add(closeButton, 0, wx.EXPAND)

        # finally, put the scrolledPannel and buttons in a sizer to manage the layout
        mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        mainSizer.Add(sw)
        mainSizer.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainSizer)

    def OnClose(self, event=None):
        self.Destroy()
