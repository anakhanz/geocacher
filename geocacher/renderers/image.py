# -*- coding: UTF-8 -*-

import logging
import os

import wx
import wx.grid             as  Grid

import geocacher

class ImageRenderer(Grid.PyGridCellRenderer):
    def __init__(self, table):
        Grid.PyGridCellRenderer.__init__(self)
        self._dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'gfx')
        self._themeDir = geocacher.config().iconTheme
        self.table = table
        self._images = {}
        self._default = None

        self.colSize = None
        self.rowSize = None

    def addImage(self, name, filename, imageType):
        imagePath=os.path.join(self._dir,self._themeDir,self._subDir,filename)
        if not os.path.isfile(imagePath):
            imagePath=os.path.join(self._dir,'default',self._subDir,filename)
        if os.path.isfile(imagePath):
            self._images[name]=wx.Bitmap(imagePath, imageType)
        else:
            self._images[name]=wx.ArtProvider.GetBitmap(wx.ART_ERROR)


    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.table.GetValue(row, col)
        if value not in self._images:
            logging.warn("Image not defined for '%s'" % value)
            value = self._default
        bmp = self._images[value]
        image = wx.MemoryDC()
        image.SelectObject(bmp)

        # clear the background
        dc.SetBackgroundMode(wx.SOLID)

        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)

        # copy the image but only to the size of the grid cell
        width, height = bmp.GetWidth(), bmp.GetHeight()

        if width > rect.width-2:
            width = rect.width-2

        if height > rect.height-2:
            height = rect.height-2

        dc.Blit(rect.x+1, rect.y+1, width, height,
                image,
                0, 0, wx.COPY, True)

class CacheBearingRenderer(ImageRenderer):
    def __init__(self, table):
        ImageRenderer.__init__(self, table)
        self._subDir='compass'
        self.addImage('N','N.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('NE','NE.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('E','E.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('SE','SE.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('S','S.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('SW','SW.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('W','W.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('NW','NW.gif', wx.BITMAP_TYPE_GIF)
        self._default='N'

class CacheSizeRenderer(ImageRenderer):
    def __init__(self, table):
        ImageRenderer.__init__(self, table)
        self._subDir='size'
        self.addImage('Micro','micro.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Small','small.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Regular','regular.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Large','large.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Not chosen','not_chosen.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Virtual','virtual.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Other','other.gif', wx.BITMAP_TYPE_GIF)
        self._default='Not chosen'

class CacheTypeRenderer(ImageRenderer):
    def __init__(self, table):
        ImageRenderer.__init__(self, table)
        self._subDir='type'
        self.addImage('Traditional Cache','traditional.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Ape','ape.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('CITO','cito.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Earthcache','earthcache.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Event Cache','event.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Maze','gps_maze.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Letterbox Hybrid','letterbox.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Mega','mega.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Multi-cache','multi-cache.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Unknown Cache','mystery.gif',wx.BITMAP_TYPE_GIF)
        self.addImage('Reverse','reverse.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Virtual Cache','virtual.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Webcam Cache','webcam.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Wherigo Cache','whereigo.gif', wx.BITMAP_TYPE_GIF)
        self.addImage('Lost and Found Event Cache','10Years_32.gif', wx.BITMAP_TYPE_GIF)
        self._default='Traditional Cache'
