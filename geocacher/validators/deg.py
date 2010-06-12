# -*- coding: UTF-8 -*-

import wx

from geocacher.libs.latlon import degToStr, strToDeg

import geocacher

class DegValidator(wx.PyValidator):
    def __init__(self, mode, data, key, new=False):
        wx.PyValidator.__init__(self)
        self.mode = mode
        self.data = data
        self.key = key
        self.new = new

    def Clone(self):
        return DegValidator(self.mode, self.data, self.key, self.new)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        if strToDeg(textCtrl.GetValue(), self.mode) == None:
            textCtrl.SetBackgroundColour('pink')
            message = _('The highlighted field must be in one of the following formats:')
            if self.mode == 'lat':
                message = message + '''
    N12 34.345
    S12 34 45.6
    S12.34567
    -12.34567'''
            elif self.mode == 'lon':
                message = message + '''
    E12 34.345
    W12 34 45.6
    W12.34567
    -12.34567'''
            else:
                message = message + '''
    12 34.345
    12 34 45.6
    12.34567'''
            wx.MessageBox(message, _('Input Error'))
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        value = self.data.get(self.key, 0)
        if self.new:
            textCtrl.SetValue('')
        else:
            format = geocacher.config().coordinateFormat
            textCtrl.SetValue(degToStr(value, format, self.mode))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = strToDeg(textCtrl.GetValue(), self.mode)
        return True

class LatValidator(DegValidator):
    def __init__(self, data, key, new=False):
        DegValidator.__init__(self, 'lat', data, key, new)

class LonValidator(DegValidator):
    def __init__(self, data, key, new=False):
        DegValidator.__init__(self, 'lon', data, key, new)
