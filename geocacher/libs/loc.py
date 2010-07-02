# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree
import os
import string

from geocacher.libs.common import getTextFromPath,getAttribFromPath

def locExport(filename,caches,correct=True,corMark='-A'):
    '''
    Exports the given caches to the given file in the .loc format.

    Arguments
    filename: Path to the file to export the cache information to
    caches:   List of cache objects to be exported

    Keyword Arguments
    correct: If true use the corrected cordinates for exporting
    corMark: String to append to the cache code if the cordinates are corrected
    '''
    if len(caches) == 0:
        return True
    root = Element("loc",version="1.0", src="Geocacher")
    for cache in caches:
        waypoint = Element("waypoint")
        root.append(waypoint)
        if correct and cache.corrected:
            name = Element("name", id=cache.code + corMark)
        else:
            name = Element("name", id=cache.code)
        name.text = cache.name + " by " + cache.placed_by
        waypoint.append(name)
        if correct:
            coord = Element("coord",
                            lat='%f' % cache.currentLat,
                            lon='%f' % cache.currentLon)
        else:
            coord = Element("coord",
                            lat='%f' % cache.lat,
                            lon='%f' % cache.lon)
        waypoint.append(coord)
        type = Element("type")
        type.text = cache.symbol.lower()
        waypoint.append(type)
        link = Element("link", text="Cache Details")
        link.text = cache.url
        waypoint.append(link)
    try:
        fid = open(filename,"w")
        fid.write("""<?xml version="1.0" encoding="UTF-8"?>""")
        ElementTree(root).write(fid,encoding="utf-8", pretty_print=True)
        fid.close()
        return True
    except:
        return False