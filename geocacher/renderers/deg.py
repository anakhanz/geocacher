# -*- coding: UTF-8 -*-

import wx
import wx.grid             as  Grid

from geocacher.libs.latlon import degToStr

class DegRenderer(Grid.PyGridCellRenderer):
    '''Renderer for cells containing measurements in degrees'''
    def __init__(self, table, conf, mode = 'pure'):
        Grid.PyGridCellRenderer.__init__(self)
        self.conf = conf
        self.table = table
        self.mode = mode

        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        try: text = degToStr(value, format, self.mode)
        except: text = ''
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = grid.GetDefaultCellBackgroundColour()
            fg = grid.GetDefaultCellTextColour()

        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

    def GetBestSize(self, grid, attr, dc, row, col):
        value = self.table.GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        text = degToStr(value, format, self.mode)
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def clone(self):
        return DegRenderer(self.table, self.conf, self.mode)

class LatRenderer(DegRenderer):
    '''Renderer for cells containing Latitudes (subclass of DegRenderer)'''
    def __init__(self, table, conf):
        DegRenderer.__init__(self, table, conf, 'lat')

class LonRenderer(DegRenderer):
    '''Renderer for cells containing Longitudes (subclass of DegRenderer)'''
    def __init__(self, table, conf):
        DegRenderer.__init__(self, table, conf, 'lon')
