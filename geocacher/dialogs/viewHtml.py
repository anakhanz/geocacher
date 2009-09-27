# -*- coding: UTF-8 -*-

import wx
import  wx.html as Html

class ViewHtml(wx.Dialog):
    '''
    A HTML Viewer dialog
    '''


    def __init__(self,parent,id,data,caption, size=(640,480)):
        '''
        Constructor
        
        Arguments
        parent:  Parent window.
        id:      ID for the window.
        data:    html data to be displayed.
        caption: Caption for the window.
        
        Keyword Argument
        size:    Size tuple for the window.
        '''
        
        self.data = data
        
        wx.Dialog.__init__(self,parent,id,caption,
                           size = size,
                           style = wx.DEFAULT_FRAME_STYLE |
                            wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.html = Html.HtmlWindow(self, wx.ID_ANY)
        
        self.printer = Html.HtmlEasyPrinting()
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.html, 1, wx.GROW)

        subbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # Save File
        btn = wx.Button(self, wx.ID_ANY, _('Save File'))
        self.Bind(wx.EVT_BUTTON, self.OnSaveFile, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)
        # Print
        btn = wx.Button(self, wx.ID_ANY, _('Print'))
        self.Bind(wx.EVT_BUTTON, self.OnPrint, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)
        # View Source
        btn = wx.Button(self, wx.ID_ANY, _('View Source'))
        self.Bind(wx.EVT_BUTTON, self.OnViewSource, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)
        # Quit
        btn = wx.Button(self, wx.ID_CLOSE, _('Close'))
        self.Bind(wx.EVT_BUTTON, self.OnClose, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)
        
        self.box.Add(subbox, 0, wx.GROW)
        self.SetSizer(self.box)
        self.SetAutoLayout(True)
        
        self.html.SetPage(data)
        
    def OnClose(self, event=None):
        '''
        Handles the event from the "Close" button, closing the html viewer.
        
        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.Destroy()
        
    def OnPrint(self, event=None):'''
        Handles the event from the "Print" button, calling the html print
        dialog.
        
        Keyword Argument
        event: The event causing this function to be called.
        '''
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintFile(self.html.GetOpenedPage())
    
    def OnSaveFile(self, event):'''
        Handles the event from the "Save" button, saving the html to a file.
        
        Keyword Argument
        event: The event causing this function to be called.
        '''
        dlg = wx.FileDialog(self, style=wx.SAVE,
                            wildcard='HTML Files|*.htm;*.html', )

        if dlg.ShowModal():
            path = dlg.GetPath()
            fid = open(file,"w")
            fid.write(self.data)
            fid.close()

        dlg.Destroy()
        
    def OnViewSource(self, event=None):'''
        Handles the event from the "View Source" button,
        displaying the html source in a window.
        
        Keyword Argument
        event: The event causing this function to be called.
        '''
        import  wx.lib.dialogs

        source = self.html.GetParser().GetSource()

        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, source, 'HTML Source')
        dlg.ShowModal()
        dlg.Destroy()