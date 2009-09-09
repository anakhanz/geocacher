# -*- coding: UTF-8 -*-

import wx
import wx.lib.scrolledpanel as Scrolled
import wx.xrc as Xrc


class ViewTravelBugs(wx.Dialog):
    '''
    View Travel Bugs dialog.
    '''
    def __init__(self,parent,cache):
        '''
        Initialises the View Travel Bugs Frame
        
        Arguments
        parent: The parent window for the dialog.
        cache:  The cache object to display the travel bugs from.
        '''

        wx.Dialog.__init__(self,parent,wx.ID_ANY,_("Travel Bugs for ")+cache.code,size = (420,500),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        res = Xrc.XmlResource('xrc\geocacher.xrc')

        # Create a scrolled panel and a vertical sizer within it to take the bugs
        sw = Scrolled.ScrolledPanel(self, -1, size=(400, 450),
                                 style = wx.TAB_TRAVERSAL)
        bugSizer = wx.BoxSizer(orient=wx.VERTICAL)
        for travelBug in cache.getTravelBugs():
            bugPanel = res.LoadPanel(sw, 'bugPanel')
            ref = Xrc.XRCCTRL(bugPanel, 'refText')
            name = Xrc.XRCCTRL(bugPanel, 'nameText')

            ref.SetValue(travelBug.ref)
            name.SetValue(travelBug.name)

            bugSizer.Add(bugPanel)

        # Final Setup of the scrolled panel
        sw.SetSizer(bugSizer)
        sw.SetAutoLayout(1)
        sw.SetupScrolling()

        # Buttons
        closeButton = wx.Button(self,wx.ID_CLOSE)

        self.Bind(wx.EVT_BUTTON, self.OnClose,closeButton)

        buttonBox = wx.BoxSizer(orient=wx.HORIZONTAL)
        buttonBox.Add(closeButton, 0, wx.EXPAND)

        # finally, put the scrolledPannel and buttons in a sizerto manage the layout

        mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        mainSizer.Add(sw)
        mainSizer.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainSizer)

    def OnClose(self, event=None):
        self.Destroy()