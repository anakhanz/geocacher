# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree
import os
import string

from geocacher.libs.common import getTextFromPath,getAttribFromPath

def locLoad(filename,DB,mode='update',userName=''):
    '''
    Imports the given .loc file into the database.

    Arguments
    filename: path to the file from which to import the cache information
    DB:       Database object to import the caches into

    Keyword Arguments
    mode:     mode to run the import in (update or replace)
    userName: geocaching.com user name for matching cache owner
    '''
    # Load LOC file
    if os.path.isfile(filename):
        locDoc = ElementTree(file=filename).getroot()
    else:
        return (False,{})
    locDate = datetime.utcfromtimestamp(os.path.getmtime(filename))
    sourceFile = os.path.abspath(filename)

    fileUpdates = {}

    # Find the way points and process them
    for wpt in locDoc.xpath('//loc//waypoint'):
        code = getAttribFromPath(wpt,'name',"id")
        if code[:2] !="GC":
            continue
        lon = float(getAttribFromPath(wpt,'coord','lon'))
        lat = float(getAttribFromPath(wpt,'coord','lat'))
        info = string.split(getTextFromPath(wpt,'name'), ' by ')
        name= info[0]
        placed_by = info[1]
        for part in info[2:]:
            placed_by +=" by "+part
        url = getTextFromPath(wpt,'link')
        symbol = getTextFromPath(wpt,'type')

        if code in fileUpdates.keys():
            ccacheUpdates = fileUpdates[code]
        else:
            cacheUpdates = {}

        cache = DB.getCacheByCode(code)
        if cache==None:
            cacheUpdates['change type'] = 'new'
            cacheUpdates['lat'] = [lat,'']
            cacheUpdates['lon'] = [lon,'']
            cacheUpdates['name'] = [name,'']
            cacheUpdates['url'] = [url,'']
            cacheUpdates['symbol'] = [symbol,'']
            cacheUpdates['placed_by'] = [placed_by,'']
            cacheUpdates['gpx_date'] = [locDate,'']
            cache = DB.addCache(code,lat=lat,lon=lon,name=name,url=url,
            symbol=symbol,placed_by=placed_by,gpx_date=locDate)
        elif 'change type' not in cacheUpdates.keys():
                cacheUpdates['change type'] = 'update'

        if ((cache.gpx_date<=locDate and mode=="update") or mode=="replace"):

            if cache.lon != lon:
                cacheUpdates['lon'] = [lon,cache.lon]
                cache.lon = lon
            if cache.lat != lat:
                cacheUpdates['lat'] = [lat,cache.lat]
                cache.lat = lat
            if cache.name != name:
                cacheUpdates['name'] = [name,cache.name]
                cache.name = name
            if cache.url != url:
                cacheUpdates['url'] = [url,cache.url]
                cache.url = url
            if cache.symbol != symbol:
                cacheUpdates['symbol'] = [symbol,cache.symbol]
                cache.symbol = symbol
            if cache.placed_by != placed_by:
                cacheUpdates['placed_by'] = [placed_by,cache.placed_by]
                cache.placed_by = placed_by
        if len(cacheUpdates) > 1:
            if cache.gpx_date != locDate:
                cache.gpx_date = locDate
                if cacheUpdates['change type'] == 'update':
                    cacheUpdates['gpx_date'] = [locDate,cache.gpx_date]
            if cache.source != sourceFile:
                cache.source = sourceFile
                cacheUpdates['source'] = [sourceFile,cache.source]
            fileUpdates[code] = cacheUpdates
    return (True,fileUpdates)


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