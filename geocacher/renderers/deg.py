# -*- coding: UTF-8 -*-

import wx
import wx.grid             as  Grid

import geocacher
from geocacher.libs.latlon import degToStr

class DegRenderer(Grid.PyGridCellRenderer):
    '''Renderer for cells containing measurements in degrees'''
    def __init__(self, table, mode = 'pure'):
        Grid.PyGridCellRenderer.__init__(self)
        self.table = table
        self.mode = mode

        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        try:
            text = degToStr(value,
                            geocacher.config().coordinateFormat,
                            self.mode)
        except:
            text = ''
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
        text = degToStr(value, geocacher.config().coordinateFormat, self.mode)
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def clone(self):
        return DegRenderer(self.table, self.mode)

class LatRenderer(DegRenderer):
    '''Renderer for cells containing Latitudes (subclass of DegRenderer)'''
    def __init__(self, table):
        DegRenderer.__init__(self, table, 'lat')

class LonRenderer(DegRenderer):
    '''Renderer for cells containing Longitudes (subclass of DegRenderer)'''
    def __init__(self, table):
        DegRenderer.__init__(self, table, 'lon')
