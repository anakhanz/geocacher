# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree
import os
import string

from __main__ import Geocacher

from libs.common import textToBool,boolToText,textToDateTime,dateTimeToText
from libs.common import getTextFromPath,getAttribFromPath

NS = {'gpx': "http://www.topografix.com/GPX/1/0",
      'gs': "http://www.groundspeak.com/cache/1/0"}


def gpxLoad(filename,DB,mode="update",userName="",userId=""):
    # Load GPX file
    # TODO: implement returning of changes from GPX file for reporting to user
    if os.path.isfile(filename):
        gpxDoc = ElementTree(file=filename).getroot()
    else:
        return
    # Get the date the GPX file was created
    try:
        gpxDate = textToDateTime(gpxDoc.xpath("//gpx:gpx//gpx:time", namespaces=NS)[0].text)
    except:
        gpxDate = datetime.utcfromtimestamp(os.path.getmtime(filename))

    # Create list for extra points
    extraWpts = []

    # Find the waypoints and process them
    for wpt in gpxDoc.xpath("//gpx:gpx//gpx:wpt", namespaces=NS):
        code = getTextFromPath(wpt,"gpx:name",NS)
        if code[:2] !="GC":
            extraWpts.append(wpt)
            continue
        updated = False
        lon = float(wpt.attrib['lon'])
        lat = float(wpt.attrib['lat'])
        id = getAttribFromPath(wpt,"gs:cache","id",NS)
        available = textToBool(getAttribFromPath(wpt,"gs:cache","available",NS,'True'))
        archived = textToBool(getAttribFromPath(wpt,"gs:cache","archived",NS,'False'))
        name = getTextFromPath(wpt,"gpx:urlname",NS)
        url = getTextFromPath(wpt,"gpx:url",NS)
        symbol = getTextFromPath(wpt,"gpx:sym",NS)
        placed = textToDateTime(getTextFromPath(wpt,"gpx:time",NS))
        placed_by = getTextFromPath(wpt,"gs:cache//gs:placed_by",NS)
        owner = getTextFromPath(wpt,"gs:cache//gs:owner",NS)
        owner_id = getAttribFromPath(wpt,"gs:cache//gs:owner","id",NS)
        cachetype = getTextFromPath(wpt,"gs:cache//gs:type",NS)
        container = getTextFromPath(wpt,"gs:cache//gs:container",NS,"Not Specified")
        difficulty = float(getTextFromPath(wpt,"gs:cache//gs:difficulty",NS,"1"))
        terrain = float(getTextFromPath(wpt,"gs:cache//gs:terrain",NS,"1"))
        state = getTextFromPath(wpt,"gs:cache//gs:state",NS)
        country = getTextFromPath(wpt,"gs:cache//gs:country",NS)
        short_desc = getTextFromPath(wpt,"gs:cache//gs:short_description",NS,"")
        short_desc_html = textToBool(getAttribFromPath(wpt,"gs:cache//gs:short_description","html",NS,"False"))
        long_desc = getTextFromPath(wpt,"gs:cache//gs:long_description",NS,"")
        long_desc_html = textToBool(getAttribFromPath(wpt,"gs:cache//gs:long_description","html",NS,"False"))
        hints = getTextFromPath(wpt,"gs:cache//gs:encoded_hints",NS,"")

        cache = DB.getCacheByCode(code)
        if cache==None:
            cache = DB.addCache(code,lat=lat,lon=lon,id=id,available=available,
            archived=archived,name=name,url=url,symbol=symbol,placed=placed,
            placed_by=placed_by,owner=owner,owner_id=owner_id,type=cachetype,
            container=container,difficulty=difficulty,terrain=terrain,state=state,
            country=country,short_desc=short_desc,short_desc_html=short_desc_html,
            long_desc=long_desc,long_desc_html=long_desc_html,
            encoded_hints=hints,gpx_date=gpxDate)
            updated = True

        if ((cache.gpx_date<=gpxDate and mode=="update") or mode=="replace"):
            cache.setLon(lon)
            cache.setLat(lat)
            cache.setId(id)
            cache.setAvailable(available)
            cache.setArchived(archived)
            cache.setName(name)
            cache.setUrl(url)
            cache.setSymbol(symbol)
            cache.setPlaced(placed)
            cache.setPlaced_by(placed_by)
            cache.setOwner(owner)
            cache.setOwner_id(owner_id)
            cache.setType(cachetype)
            cache.setContainer(container)
            cache.setDifficulty(difficulty)
            cache.setTerrain(terrain)
            cache.setState(state)
            cache.setCountry(country)
            cache.setShort_desc(short_desc)
            cache.setShort_desc_html(short_desc_html)
            cache.setLong_desc(long_desc)
            cache.setLong_desc_html(long_desc_html)
            cache.setEncoded_hints(hints)
        # Always update Logs and travel bugs
        foundUpdated=False
        for wptLog in wpt.xpath("gs:cache//gs:logs//gs:log", namespaces=NS):
            logId = wptLog.attrib["id"]
            logDate = textToDateTime(getTextFromPath(wptLog, "gs:date",NS))
            logType = getTextFromPath(wptLog, "gs:type",NS)
            logFinderId = getAttribFromPath(wptLog, "gs:finder", "id", NS)
            logFinderName = getTextFromPath(wptLog, "gs:finder",NS)
            logEncoded = textToBool(getAttribFromPath(wptLog, "gs:text", "encoded", NS, "False"))
            logText = getTextFromPath(wptLog, "gs:text",NS)

            changed = False

            log = cache.getLogById(logId)
            if  log==None:
                log = cache.addLog(logId,date=logDate,type=logType,
                finder_id=logFinderId,finder_name=logFinderName,
                encoded=logEncoded,text=logText)
                changed = True
            else:
                if logDate != log.date:
                    log.setDate(logDate)
                    changed = True
                if logType != log.type:
                    log.setType(logType)
                    changed = True
                if logFinderId != log.finder_id:
                    log.setFinder_id(logFinderId)
                    changed = True
                if logFinderName != log.finder_name:
                    log.setFinder_name(logFinderName)
                    changed = True
                if logEncoded != log.encoded:
                    log.setEncoded(logEncoded)
                    changed = True
                if logText != log.text:
                    log.setText(logText)
                    changed = True
                updated |= changed
            # Update Own find details if this is the first log with changes
            # in it that is of the "Found it" type and the finderId or
            # finderName matches the users values
            if ((not foundUpdated) and changed and(logFinderId == userId or logFinderName == userName)):
                if logType =="Found it":
                    cache.setFound(True)
                    cache.setFound_date(logDate)
                elif logType == "Didn't find it":
                    cache.SetDnf(True)
                    cache.setDnf_date(logDate)
                if logType =="Found it" or logType == "Didn't find it":
                    cache.setOwn_log(logText)
                    cache.setOwn_log_encoded(logEncoded)
                    foundUpdated=True
        wptTbRefs = []
        cacheTbRefs = cache.getTravelBugRefs()
        for wptTb in wpt.xpath("gs:cache//gs:travelbugs//gs:travelbug", namespaces=NS):
            wptTbRef = wptTb.attrib["ref"]
            wptTbRefs.append(wptTbRef)
            wptTbId = wptTb.attrib["id"]
            wptTbName = getTextFromPath(wptTb,"gs:name",NS)
            if not (wptTbRef in cacheTbRefs):
                cacheTb = cache.addTravelBug(wptTbRef,id=wptTbId,name=wptTbName)
            else:
                cacheTb = cache.getTravelBugByRef(wptTbRef)
                cacheTb.setId(wptTbId)
                cacheTb.setName(wptTbName)
        # Go through the list of trave bugs in the cache and delete any
        # that are not listed in the wpt
        for cacheTbRef in cacheTbRefs:
            if not(cacheTbRef in wptTbRefs):
                cache.getTravelBugByName(cacheTbRef).delete()
                updated = True

        if updated:
            cache.setGpx_date(gpxDate)
            cache.setSource(os.path.abspath(filename))

    cacheCodes = DB.getCacheCodeList()
    for wpt in extraWpts:
        updated = False
        lon = float(wpt.attrib['lon'])
        lat = float(wpt.attrib['lat'])
        id = getTextFromPath(wpt,"gpx:name",NS)
        time = textToDateTime(getTextFromPath(wpt,"gpx:time",NS))
        cmt = getTextFromPath(wpt,"gpx:cmt",NS)
        name = getTextFromPath(wpt,"gpx:desc",NS)
        url = getTextFromPath(wpt,"gpx:url",NS)
        sym = getTextFromPath(wpt,"gpx:sym",NS)
        cache = DB.getCacheByCode("GC"+id[2:])
        if cache != None:
            addWaypoint = cache.getAddWaypointByCode(id)
            if addWaypoint == None:
                cache.addAddWaypoint(id,lat=lat,lon=lon,name=name,url=url,time=time,cmt=cmt,sym=sym)
                updated = True
            else:
                addWaypoint.setLat(lat)
                addWaypoint.setLon(lon)
                addWaypoint.setTime(time)
                addWaypoint.setCmt(cmt)
                addWaypoint.setName(name)
                addWaypoint.setUrl(url)
                addWaypoint.setSym(sym)
            if updated:
                cache.setGpx_date(gpxDate)
                cache.setSource(os.path.abspath(filename))

def exportGpx(self,filename,caches,gs=False,logs=False,tbs=False,addWpt=False,simple=False,full=False):
    assert simple != full
    assert os.path.isdir(os.path.split(filename)[0])
    gs = (gs and (not simple)) or full
    logs = (logs and (not simple)) or full
    tbs = (tbs and (not simple)) or full
    print "GPX file export not yet implemented"
    # TODO: implement GPX export
    addWpt = addWpt and (not simple) or full