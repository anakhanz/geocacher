# -*- coding: UTF-8 -*-

import wx
import wx.grid             as  Grid


class DistRenderer(Grid.PyGridCellRenderer):
    '''
    Renderer for cells containing distances
    '''
    def __init__(self, table, conf):
        Grid.PyGridCellRenderer.__init__(self)
        self.conf = conf
        self.table = table

        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        if self.conf.common.miles or False:
            text = '%0.2f Mi' % (value * 0.621371192)
        else:
            text = '%0.2f km' % value
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
        if self.conf.common.miles or False:
            text = '%0.2f Mi' % (value * 0.621371192)
        else:
            text = '%0.2f km' % value
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def clone(self):
        return DistRenderer(self.table, self.conf)