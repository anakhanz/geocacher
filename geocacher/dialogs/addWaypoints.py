# -*- coding: UTF-8 -*-

import os.path

import wx
import wx.lib.scrolledpanel as Scrolled
import wx.xrc as Xrc

import geocacher
from geocacher.libs.latlon import latToStr, lonToStr

class AddWpts(wx.Dialog):
    '''
    Additional Waypoints Dialog
    '''
    def __init__(self,parent,cache):
        '''
        Initialises the additional waypoints dialog.

        Arguments
        parent: The parent window for the dialog.
        cache:  The cache object to display the additional waypoints from.
        '''

        wx.Dialog.__init__(self,parent,wx.ID_ANY,_("Additional Waypoints for ")+cache.code,size = (490,500),
                           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create a scrolled panel and a vertical sizer within it to take the logs
        sw = Scrolled.ScrolledPanel(self, -1, size=(480, 450),
                                 style = wx.TAB_TRAVERSAL)
        wptSizer = wx.BoxSizer(orient=wx.VERTICAL)

        res = Xrc.XmlResource(os.path.join(geocacher.getBasePath(), 'xrc', 'addWaypointsPanel.xrc'))

        # Create a block for each log and add it to the logs sizer
        for wpt in cache.getAddWaypoints():
            wptPanel = res.LoadPanel(sw, 'addWaypointPanel')
            code = Xrc.XRCCTRL(wptPanel, 'codeText')
            wptType = Xrc.XRCCTRL(wptPanel, 'typeText')
            lat = Xrc.XRCCTRL(wptPanel, 'latText')
            lon = Xrc.XRCCTRL(wptPanel, 'lonText')
            name = Xrc.XRCCTRL(wptPanel, 'nameText')
            comment = Xrc.XRCCTRL(wptPanel, 'commentText')

            code.SetValue(wpt.code)
            wptType.SetValue(wpt.sym)
            lat.SetValue(latToStr(wpt.lat, geocacher.config().coordinateFormat))
            lon.SetValue(lonToStr(wpt.lon, geocacher.config().coordinateFormat))
            name.SetValue(wpt.name)
            comment.SetValue(wpt.cmt)
            wptSizer.Add(wptPanel)

        # Final Setup of the scrolled panel
        sw.SetSizer(wptSizer)
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
