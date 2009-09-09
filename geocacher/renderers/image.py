# -*- coding: UTF-8 -*-

import logging
import os

import wx
import wx.grid             as  Grid

class ImageRenderer(Grid.PyGridCellRenderer):
    def __init__(self, table, conf):
        Grid.PyGridCellRenderer.__init__(self)
        self.table = table
        self._images = {}
        self._default = None

        self.colSize = None
        self.rowSize = None

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
        
class CacheSizeRenderer(ImageRenderer):
    def __init__(self, table, conf):
        ImageRenderer.__init__(self, table, conf)
        self._images = {'Micro':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-micro.gif'), wx.BITMAP_TYPE_GIF),
                        'Small':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-small.gif'), wx.BITMAP_TYPE_GIF),
                        'Regular':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-regular.gif'), wx.BITMAP_TYPE_GIF),
                        'Large':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-large.gif'), wx.BITMAP_TYPE_GIF),
                        'Not chosen':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-not_chosen.gif'), wx.BITMAP_TYPE_GIF),
                        'Virtual':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-virtual.gif'), wx.BITMAP_TYPE_GIF),
                        'Other':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','sz-other.gif'), wx.BITMAP_TYPE_GIF)}
        self._default='Not chosen'

class CacheTypeRenderer(ImageRenderer):
    def __init__(self, table, conf):
        ImageRenderer.__init__(self, table, conf)
        self._images = {'Traditional Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-traditional.gif'), wx.BITMAP_TYPE_GIF),
                        'Ape':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-ape.gif'), wx.BITMAP_TYPE_GIF),
                        'CITO':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-cito.gif'), wx.BITMAP_TYPE_GIF),
                        'Earthcache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-earthcache.gif'), wx.BITMAP_TYPE_GIF),
                        'Event Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-event.gif'), wx.BITMAP_TYPE_GIF),
                        'Maze':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-gps_maze.gif'), wx.BITMAP_TYPE_GIF),
                        'Letterbox Hybrid':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-letterbox.gif'), wx.BITMAP_TYPE_GIF),
                        'Mega':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-mega.gif'), wx.BITMAP_TYPE_GIF),
                        'Multi-cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-multi-cache.gif'), wx.BITMAP_TYPE_GIF),
                        'Unknown Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-mystery.gif'), wx.BITMAP_TYPE_GIF),
                        'Reverse':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-reverse.gif'), wx.BITMAP_TYPE_GIF),
                        'Virtual Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-virtual.gif'), wx.BITMAP_TYPE_GIF),
                        'Webcam Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-webcam.gif'), wx.BITMAP_TYPE_GIF),
                        'Wherigo Cache':wx.Bitmap(os.path.join(os.path.dirname(__file__),'gfx','type-whereigo.gif'), wx.BITMAP_TYPE_GIF)
                        }
        self._default='Traditional Cache'
