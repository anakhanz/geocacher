# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree
import os
import string

from libs.common import getTextFromPath,getAttribFromPath #@UnresolvedImport

def locLoad(filename,DB,mode="update"):
    # Load LOC file
    if os.path.isfile(filename):
        locDoc = ElementTree(file=filename).getroot()
    else:
        return
    locDate = datetime.utcfromtimestamp(os.path.getmtime(filename))

    # Find the way points and process them
    for wpt in locDoc.xpath("//loc//waypoint"):
        code = getAttribFromPath(wpt,"name","id")
        if code[:2] !="GC":
            continue
        updated = False
        lon = float(getAttribFromPath(wpt,"coord",'lon'))
        lat = float(getAttribFromPath(wpt,"coord",'lat'))
        info = string.split(getTextFromPath(wpt,"name"), " by ")
        name= info[0]
        placed_by = info[1]
        for part in info[2:]:
            placed_by +=" by "+part
        url = getTextFromPath(wpt,"link")
        symbol = getTextFromPath(wpt,"type")

        cache = DB.getCacheByCode(code)
        if cache==None:
            cache = DB.addCache(code,lat=lat,lon=lon,name=name,url=url,
            symbol=symbol,placed_by=placed_by,gpx_date=locDate)
            updated = True

        if ((cache.gpx_date<=locDate and mode=="update") or mode=="replace"):
            cache.lon = lon
            cache.lat = lat
            cache.name = name
            cache.url = url
            cache.symbol = symbol
            cache.placed_by = placed_by
        if updated:
            cache.gpx_date = locDate
            cache.source = os.path.abspath(filename)

def locExport(filename,caches,correct=True,corMark='-A'):
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
        ElementTree(root).write(fid,encoding="utf-8")
        fid.close()
        return True
    except:
        return False