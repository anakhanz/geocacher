# -*- coding: UTF-8 -*-

import wx

from validators.deg import LatValidator, LonValidator #@UnresolvedImport
from validators.notEmpty import NotEmptyValidator #@UnresolvedImport

class CorrectLatLon(wx.Dialog):
    '''Get the import options from the user'''
    def __init__(self,parent,id, conf, code, data, new):
        '''Creates the Lat/Lon correction Frame'''
        wx.Dialog.__init__(self,parent,id,
            _('Lat/Lon Correction for ')+code,size = (350,250),
           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create labels for controls
        latName = wx.StaticText(self, wx.ID_ANY, _('Latitude'))
        lonName = wx.StaticText(self, wx.ID_ANY, _('Longitude'))
        origName = wx.StaticText(self, wx.ID_ANY, _('Origional'))
        corName = wx.StaticText(self, wx.ID_ANY, _('Corrected'))
        commName = wx.StaticText(self, wx.ID_ANY, _('Comment'))

        # Create controls
        oLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LatValidator(conf, data, 'lat'))
        oLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(conf, data, 'lon'))
        cLat = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LatValidator(conf, data, 'clat', new))
        cLon = wx.TextCtrl(self, wx.ID_ANY, size=(100, -1),
            validator=LonValidator(conf, data, 'clon', new))

        comment = wx.TextCtrl(self, wx.ID_ANY, size=(200, 100),
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            validator=NotEmptyValidator(data, 'cnote'))

        # Create Grid for coordinate information and add the controls
        coordGrid = wx.GridBagSizer(3, 3)
        coordGrid.Add(latName, (0,1), (1,1), wx.ALL, 1)
        coordGrid.Add(lonName, (0,2), (1,1), wx.ALL, 1)
        coordGrid.Add(origName, (1,0), (1,1), wx.ALL, 1)
        coordGrid.Add(corName, (2,0), (1,1), wx.ALL, 1)

        coordGrid.Add(oLat, (1,1), (1,1), wx.ALL, 1)
        coordGrid.Add(oLon, (1,2), (1,1), wx.ALL, 1)
        coordGrid.Add(cLat, (2,1), (1,1), wx.ALL, 1)
        coordGrid.Add(cLon, (2,2), (1,1), wx.ALL, 1)

        # Put a box around the coordinates section
        coordSbox = wx.StaticBox(self, wx.ID_ANY, _('Coordinates'))
        coordSboxSizer = wx.StaticBoxSizer(coordSbox, wx.VERTICAL)
        coordSboxSizer.Add(coordGrid, 0, 0, 0)

        # place the coordinates section and the comment in the vertical box
        mainBox = wx.BoxSizer(orient=wx.VERTICAL)
        mainBox.Add(coordSboxSizer)
        mainBox.Add(commName, 0, wx.EXPAND)
        mainBox.Add(comment, 0, wx.EXPAND)

        # Ok and Cancel Buttons to the bottom of the form
        okButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonBox = wx.StdDialogButtonSizer()
        buttonBox.AddButton(okButton)
        buttonBox.AddButton(cancelButton)
        buttonBox.Realize()

        mainBox.Add(buttonBox, 0, wx.EXPAND)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

        # Stop the original Lat/Lon values being edited
        oLat.SetEditable(False)
        oLon.SetEditable(False)

        self.Show(True)