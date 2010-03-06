# -*- coding: UTF-8 -*-

import wx
import wx.grid             as  Grid

from geocacher.libs.latlon import degToStr, strToDeg

class DegEditor(Grid.PyGridCellEditor):
    def __init__(self, conf, mode = 'pure'):
        Grid.PyGridCellEditor.__init__(self)
        self.conf = conf
        self.mode = mode

    def Create(self, parent, id, evtHandler):
        self.newValue = [0]

        self._tc = wx.TextCtrl(parent, id,'')
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)

        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        format = self.conf.common.coordFmt or 'hdd mm.mmm'
        self._tc.SetValue(degToStr(self.startValue, format, self.mode))
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()
        self._tc.SetSelection(0, self._tc.GetLastPosition())

    def EndEdit(self, row, col, grid):
        changed = False

        value = strToDeg(self._tc.GetValue(), self.mode)

        if value != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, value)

        return changed

    def Reset(self):
        self._tc.SetValue(degToStr(self.startValue, format, self.mode))
        self._tc.SetInsertionPointEnd()

    def Clone(self):
        return DegEditor(self.conf, self.mode)

    def StartingKey(self, evt):
        self.OnChar(evt)
        if evt.GetSkipped():
            self._tc.EmulateKeyPress(evt)

class LatEditor(DegEditor):
    '''Editor for cells containing Latitudes (subclass of DegEditor)'''
    def __init__(self, conf):
        DegEditor.__init__(self, conf, 'lat')

class LonEditor(DegEditor):
    '''Editor for cells containing Longitudes (subclass of DegEditor)'''
    def __init__(self, conf):
        DegEditor.__init__(self, conf, 'lon')
