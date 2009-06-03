# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree
import os
import string

from __main__ import Geocacher

from libs.common import textToBool,boolToText,textToDateTime,dateTimeToText
from libs.common import getTextFromPath,getAttribFromPath

def locLoad(filename,DB,mode="update"):
    # Load LOC file
    # TODO: implement returning of changes from LOC file for reporting to user
    if os.path.isfile(filename):
        locDoc = ElementTree(file=filename).getroot()
    else:
        return
    locDate = datetime.utcfromtimestamp(os.path.getmtime(filename))

    # Find the waypoints and process them
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
            cache.setLon(lon)
            cache.setLat(lat)
            cache.setName(name)
            cache.setUrl(url)
            cache.setSymbol(symbol)
            cache.setPlaced_by(placed_by)
        if updated:
            cache.setGpx_date(locDate)
            cache.setSource(os.path.abspath(filename))

def exportLoc(self,filename,caches):
    print "GPX file export not yet implemented"