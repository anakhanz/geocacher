# -*- coding: UTF-8 -*-

import wx
import  wx.gizmos   as  gizmos

class CacheChanges (wx.Dialog):
    '''Display cache changes to the user'''
    def __init__(self,parent,id, changes):
        '''Creates the Lat/Lon correction Frame'''
        wx.Dialog.__init__(self,parent,id,
            _('Changes from Import'),size = (350,250),
           style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.tree = gizmos.TreeListCtrl(self, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        #| wx.TR_HAS_BUTTONS
                                        #| wx.TR_TWIST_BUTTONS
                                        #| wx.TR_ROW_LINES
                                        #| wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                        | wx.TR_HIDE_ROOT
                                   )

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,
                                                      wx.ART_OTHER,
                                                      isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,
                                                      wx.ART_OTHER,
                                                      isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,
                                                      wx.ART_OTHER,
                                                      isz))
        self.tree.SetImageList(il)
        self.il = il

        self.tree.AddColumn("Item")
        self.tree.AddColumn("New Value")
        self.tree.AddColumn("Old Value")
        self.tree.SetMainColumn(0)
        #self.tree.SetColumnWidth(width, column)

        self.root = self.tree.AddRoot("Changes")

        for filename in changes.keys():
            fileNode = self.tree.AppendItem(self.root, filename)
            self.tree.SetItemImage(fileNode,
                                   fldridx,
                                   which = wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(fileNode,
                                   fldropenidx,
                                   which = wx.TreeItemIcon_Expanded)
            for cacheName in changes[filename].keys():
                text = cacheName + ' ' + changes[filename]\
                                                [cacheName]\
                                                ['change type']
                cacheNode = self.tree.AppendItem(fileNode, text)
                self.tree.SetItemText(cacheNode,
                                      changes[filename]\
                                             [cacheName]\
                                             ['change type'],1)
                self.tree.SetItemImage(cacheNode,
                                       fldridx,
                                       which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(cacheNode,
                                       fldropenidx,
                                       which = wx.TreeItemIcon_Expanded)
                for change in changes[filename][cacheName].keys():
                    if change not in ['change type']:
                        changeNode = self.tree.AppendItem(cacheNode, change)
                        self.tree.SetItemText(changeNode,
                                              str(changes[filename]\
                                                         [cacheName]\
                                                         [change][0]),1)
                        self.tree.SetItemText(changeNode,
                                              str(changes[filename]\
                                                         [cacheName]\
                                                         [change][1]),2)
                self.tree.SortChildren(cacheNode)
            self.tree.SortChildren(fileNode)
        self.tree.SortChildren(self.root)