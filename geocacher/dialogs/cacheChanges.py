# -*- coding: UTF-8 -*-

import wx
import  wx.gizmos   as  gizmos

from geocacher.libs.dbobjects import ATTRIBUTES

import geocacher

class CacheChanges (wx.Dialog):
    '''Display cache changes to the user'''
    def __init__(self,parent,id,changes):
        '''
        Init function

        Arguments
        parent:  Parent frame
        id:      Frame ID to be used
        changes: Dictioinary containing the change s to be displayed
        '''

        exceptions = ['change type','Attributes','Logs','Travel Bugs',
                      'Add Wpts','gpx_date', 'source']

        wx.Dialog.__init__(self,parent,id,
            _('Changes from Import'),size = (700,400),
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
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,
                                                           wx.ART_OTHER,
                                                           isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,
                                                           wx.ART_OTHER,
                                                           isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,
                                                           wx.ART_OTHER,
                                                           isz))
        self.tree.SetImageList(il)
        self.il = il

        self.tree.AddColumn("Item")
        self.tree.AddColumn("New Value")
        self.tree.AddColumn("Old Value")
        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 350)
        self.tree.SetColumnWidth(1, 155)
        self.tree.SetColumnWidth(2, 155)

        self.root = self.tree.AddRoot("Changes")

        for filename in changes.keys():
            fileNode = self.addBranch(self.root, filename)
            for cacheCode in changes[filename].keys():
                self.cache = geocacher.db().getCacheByCode(cacheCode)
                text = cacheCode + ' ' + self.cache.name
                cacheNode = self.addBranch(fileNode,
                                           text,
                                           changes[filename]
                                                  [cacheCode]
                                                  ['change type'])
                self.processFields(cacheNode,
                                   changes[filename][cacheCode],
                                   exceptions)
                if 'Attributes' in changes[filename][cacheCode].keys():
                    self.processAttributes(cacheNode,
                                        changes[filename]
                                               [cacheCode]
                                               ['Attributes'])
                if 'Add Wpts' in changes[filename][cacheCode].keys():
                    self.processAddWpts(cacheNode,
                                        changes[filename]
                                               [cacheCode]
                                               ['Add Wpts'])
                if 'Travel Bugs' in changes[filename][cacheCode].keys():
                    self.processTbs(cacheNode,
                                    changes[filename]
                                           [cacheCode]
                                           ['Travel Bugs'])
                if 'Logs' in changes[filename][cacheCode].keys():
                    self.processLogs(cacheNode,
                                     changes[filename]
                                            [cacheCode]
                                            ['Logs'])
            self.tree.SortChildren(fileNode)
        self.tree.SortChildren(self.root)

    def processAttributes(self,parent,attribChanges):
        '''
        Process the given list of changes for the Attributes and adds them to the tree.

        Arguments
        parent:        Parent node to add the attributes branch to.
        attribChanges: Attribute changes to be added
        '''
        attribsNode = self.addBranch(parent, _('Attributes'))
        for attrib in attribChanges.keys():
            attribNode = self.addBranch(attribsNode,'#'+str(attrib)+' '+ ATTRIBUTES[attrib])
            self.processFields(attribNode, attribChanges[attrib])
        self.tree.SortChildren(attribsNode)

    def processLogs(self,parent,logChanges):
        '''
        Process the given list of changes for the Logs and adds them to the tree.

        Arguments
        parent:     Parent node to add the logs branch to.
        logChanges: Log changes to be added
        '''
        logsNode = self.addBranch(parent, _('Logs'))
        for log in logChanges.keys():
            logOwner = self.cache.getLogById(log).finder_name
            logNode = self.addBranch(logsNode,'#'+str(log)+' '+logOwner)
            self.processFields(logNode, logChanges[log])
        self.tree.SortChildren(logsNode)

    def processTbs(self,parent,tbChanges):
        '''
        Process the given list of changes for the Travel Bug and adds them to
        the tree.

        Arguments
        parent:    Parent node to add the travel bugs branch to.
        tbChanges: Travel Bug changes to be added
        '''
        tbsNode = self.addBranch(parent, _('Travel Bugs'))
        for tb in tbChanges.keys():
            self.addLeaf(tbsNode, tb, tbChanges[tb])
        self.tree.SortChildren(tbsNode)

    def processAddWpts(self,parent,wptChanges):
        '''
        Process the given list of changes for the Additional waypoints and adds
        them to the tree.

        Arguments
        parent:     Parent node to add the additional waypoints branch to.
        wptChanges: Additional waypoint changes to be added
        '''
        wptsNode = self.addBranch(parent, _('Additional Waypints'))
        for wpt in wptChanges.keys():
            wptNode = self.addBranch(wptsNode,wpt)
            self.processFields(wptNode, wptChanges[wpt])
        self.tree.SortChildren(wptsNode)

    def processFields(self,parent,fields,exceptions=[]):
        '''
        Adds the given dictionary of fields as leaf nodes to the given parent.

        Arguments
        parent:     Parent node to add the
        fields:     Dictionary of fields to process

        Keywork Arguments
        exceptions: Field names to skip
        '''
        for field in fields:
            if field not in exceptions:
                self.addLeaf(parent, field, fields[field])
        self.tree.SortChildren(parent)

    def addBranch(self, parent, branchName, changeType=None):
        '''
        Adds a branch node with the right icons using the given name and change
        type.

        Arguments
        parent:     Parent node to add the branch node under
        branchName: Name of the node

        Keyword Argument
        changeType: Change type to be displayed in the first column
        '''
        branchNode = self.tree.AppendItem(parent, branchName)
        if changeType != None:
            self.tree.SetItemText(branchNode,changeType,1)
        self.tree.SetItemImage(branchNode,
                               self.fldridx,
                               which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(branchNode,
                               self.fldropenidx,
                               which = wx.TreeItemIcon_Expanded)
        return branchNode

    def addLeaf(self, parent, changeName, changeDetail):
        '''
        Adds a leaf node with the right icon using the given name and change
        details.

        Arguments
        parent:       Parent node to add the leaf node under
        branchName:   Name of the node
        changeDetail: Detail of the canged to be displayed in the columns
        '''
        leafNode = self.tree.AppendItem(parent, str(changeName))
        if type(changeDetail) == list:
            self.tree.SetItemText(leafNode,
                                  unicode(changeDetail[0]),1)
            self.tree.SetItemText(leafNode,
                                  unicode(changeDetail[1]),2)
        else:
            self.tree.SetItemText(leafNode,
                                  unicode(changeDetail),1)
        self.tree.SetItemImage(leafNode,self.fileidx)
        return leafNode

