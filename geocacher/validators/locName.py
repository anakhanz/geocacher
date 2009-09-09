# -*- coding: UTF-8 -*-

import wx

class LocNameValidator(wx.PyValidator):
    def __init__(self, data, key, names):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key
        self.names = names

    def Clone(self):
        return LocNameValidator(self.data, self.key, self.names)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        ok = False
        if len(text) == 0:
            message = _('The Location Name field must not be empty')
        elif text != self.data[self.key] and text in self.names:
            message = _('The Location Name can not be the same as another Location Name')
        else:
            ok = True
        if ok:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True
        else:
            textCtrl.SetBackgroundColour('pink')
            wx.MessageBox(message, _('Input Error'))
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False

    def TransferToWindow(self):
        textCtrl = self.GetWindow()
        textCtrl.SetValue(self.data.get(self.key, ""))
        return True

    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = textCtrl.GetValue()
        return True
