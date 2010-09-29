# -*- coding: UTF-8 -*-

from datetime import datetime
#from xml.etree import Element,ElementTree,XML
from xml.etree import ElementTree
import logging
import os
import shutil
import tempfile
import zipfile

import geocacher

from geocacher.libs.common import textToBool,textToDateTime,dateTimeToText
from geocacher.libs.common import getTextFromPath,getAttribFromPath

NS = {'gpx': "http://www.topografix.com/GPX/1/0",
      'gs': "http://www.groundspeak.com/cache/1/0"}

GPX = "{%s}" %NS['gpx']
GS = "{%s}" %NS['gs']

ElementTree.register_namespace('', "http://www.topografix.com/GPX/1/0")
ElementTree.register_namespace('groundspeak', "http://www.groundspeak.com/cache/1/0")


def gpxLoad(filename,mode="update",userName="",userId="",fileUpdates={},
            gpxFilename = None):
    '''
    Imports the given .gpx file into the database.

    Arguments
    filename: path to the file from which to import the cache information
    DB:       Database object to import the caches into

    Keyword Arguments
    mode:        mode to run the import in (update or replace)
    userName:    geocaching.com user name for matching cache owner
    userId:      geocaching.com user ID for matching cache owner ID
    fileUpdates: Dictionary for adding updates to for reporting back to the user
    gpxFilename: filename to use in gpx source column if different from filename
    '''
    # Load GPX file
    if os.path.isfile(filename):
        gpxDoc = ElementTree.parse(filename).getroot()
        if gpxFilename == None:
            sourceFile = os.path.abspath(filename)
        else:
            sourceFile = gpxFilename
    else:
        return (False, fileUpdates)
    # Get the date the GPX file was created
    try:
        gpxDate = textToDateTime('%s' % gpxDoc.find("gpx:time", NS).text)
        logging.debug('Date from File contents: %s' % dateTimeToText(gpxDate))
    except:
        gpxDate = datetime.utcfromtimestamp(os.path.getmtime(filename))
        logging.debug('Date from file timestamp: %s' % dateTimeToText(gpxDate))

    # Create list for extra points
    extraWpts = []

    # Find the waypoints and process them
    for wpt in gpxDoc.findall("gpx:wpt", NS):
        code = getTextFromPath(wpt,"gpx:name",NS)
        logging.debug(code)
        if code[:2] !="GC":
            extraWpts.append(wpt)
            continue
        lon = float(getAttribFromPath(wpt,".","lon",NS,'0.0'))
        lat = float(getAttribFromPath(wpt,".","lat",NS,'0.0'))
        id = int(getAttribFromPath(wpt,"gs:cache","id",NS))
        available = textToBool(getAttribFromPath(wpt,"gs:cache","available",NS,'True'))
        archived = textToBool(getAttribFromPath(wpt,"gs:cache","archived",NS,'False'))
        name = getTextFromPath(wpt,"gpx:urlname",NS)
        url = getTextFromPath(wpt,"gpx:url",NS)
        placed = textToDateTime(getTextFromPath(wpt,"gpx:time",NS))
        placed_by = getTextFromPath(wpt,"gs:cache//gs:placed_by",NS)
        owner = getTextFromPath(wpt,"gs:cache//gs:owner",NS)
        owner_id = int(getAttribFromPath(wpt,"gs:cache//gs:owner","id",NS))
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

        if code in fileUpdates.keys():
            cacheUpdates = fileUpdates[code]
        else:
            cacheUpdates = {}

        cache = geocacher.db().getCacheByCode(code)
        if cache==None:
            cacheUpdates['change type'] = 'new'
            cacheUpdates['lat'] = [lat,'']
            cacheUpdates['lon'] = [lon,'']
            cacheUpdates['id'] = [id,'']
            cacheUpdates['available'] = [available,'']
            cacheUpdates['archived'] = [archived,'']
            cacheUpdates['name'] = [name,'']
            cacheUpdates['url'] = [url,'']
            cacheUpdates['placed_by'] = [placed_by,'']
            cacheUpdates['owner'] = [owner,'']
            cacheUpdates['owner_id'] = [owner_id,'']
            cacheUpdates['type'] = [cachetype,'']
            cacheUpdates['container'] = [container,'']
            cacheUpdates['difficulty'] = [difficulty,'']
            cacheUpdates['terrain'] = [terrain,'']
            cacheUpdates['state'] = [state,'']
            cacheUpdates['country'] = [country,'']
            cacheUpdates['short_desc'] = [short_desc,'']
            cacheUpdates['short_desc_html'] = [short_desc_html,'']
            cacheUpdates['long_desc'] = [long_desc,'']
            cacheUpdates['long_desc_html'] = [long_desc_html,'']
            cacheUpdates['encoded_hints'] = [hints,'']
            cacheUpdates['gpx_date'] = [gpxDate,'']
            cache = geocacher.db().addCache(code,lat=lat,lon=lon,id=id,
                                available=available,archived=archived,
                                name=name,url=url,
                                placed=placed,placed_by=placed_by,
                                owner=owner,owner_id=owner_id,
                                type=cachetype,container=container,
                                difficulty=difficulty,terrain=terrain,
                                state=state,country=country,
                                short_desc=short_desc,
                                short_desc_html=short_desc_html,
                                long_desc=long_desc,
                                long_desc_html=long_desc_html,
                                encoded_hints=hints,gpx_date=gpxDate)



        elif 'change type' not in cacheUpdates.keys():
            cacheUpdates['change type'] = 'update'
        if ((cache.gpx_date<=gpxDate and mode=="update") or mode=="replace"):
            if cache.lon != lon:
                cacheUpdates['lon'] = [lon,cache.lon]
                cache.lon = lon
            if cache.lat != lat:
                cacheUpdates['lat'] = [lat,cache.lat]
                cache.lat = lat
            if cache.id != id:
                cacheUpdates['available'] = [cache.available,available]
                cache.id = id
            if cache.archived != archived:
                cacheUpdates['archived'] = [archived,cache.archived]
                cache.archived = archived
            if cache.name != name:
                cacheUpdates['name'] = [name,cache.name]
                cache.name = name
            if cache.url != url:
                cacheUpdates['url'] = [url,cache.url]
                cache.url = url
            if cache.placed_by != placed_by:
                cacheUpdates['placed_by'] = [placed_by,cache.placed_by]
                cache.placed_by = placed_by
            if cache.owner != owner:
                cacheUpdates['owner'] = [owner,cache.owner]
                cache.owner = owner
            if cache.owner_id != owner_id:
                cacheUpdates['owner_id'] = [owner_id,cache.owner_id]
                cache.owner_id = owner_id
            if cache.type != cachetype:
                cacheUpdates['type'] = [owner_id,cache.owner_id]
                cache.type = cachetype
            if cache.container != container:
                cacheUpdates['container'] = [container,cache.container]
                cache.container = container
            if cache.difficulty != difficulty:
                cacheUpdates['difficulty'] = [difficulty,cache.difficulty]
                cache.difficulty = difficulty
            if cache.terrain != terrain:
                cacheUpdates['terrain'] = [terrain,cache.terrain]
                cache.terrain = terrain
            if cache.state != state:
                cacheUpdates['state'] = [state,cache.state]
                cache.state = state
            if cache.country != country:
                cacheUpdates['country'] = [country,cache.country]
                cache.country = country
            if cache.short_desc != short_desc:
                cacheUpdates['short_desc'] = [short_desc,cache.short_desc]
                cache.short_desc = short_desc
            if cache.short_desc_html != short_desc_html:
                cacheUpdates['short_desc_html'] = [short_desc_html,
                                                   cache.short_desc_html]
                cache.short_desc_html = short_desc_html
            if cache.long_desc != long_desc:
                cacheUpdates['long_desc'] = [long_desc,cache.long_desc]
                cache.long_desc = long_desc
            if cache.long_desc_html != long_desc_html:
                cacheUpdates['long_desc_html'] = [long_desc_html,
                                                  cache.long_desc_html]
                cache.long_desc_html != long_desc_html
            if cache.encoded_hints != hints:
                cacheUpdates['encoded_hints'] = [hints,cache.encoded_hints]
                cache.encoded_hints = hints
        # Always update Logs and travel bugs
        foundUpdated=False
        logsUpdates = {}
        for wptLog in wpt.findall("gs:cache//gs:logs//gs:log", NS):
            logId = int(getAttribFromPath(wptLog, '.', "id",NS))
            #logId = int(wptLog.attrib["id"])
            logDate = textToDateTime(getTextFromPath(wptLog, "gs:date",NS))
            logType = getTextFromPath(wptLog, "gs:type",NS)
            logFinderId = int(getAttribFromPath(wptLog, "gs:finder", "id", NS))
            logFinderName = getTextFromPath(wptLog, "gs:finder",NS)
            logEncoded = textToBool(getAttribFromPath(wptLog, "gs:text", "encoded", NS, "False"))
            logText = getTextFromPath(wptLog, "gs:text",NS)

            logUpdates = {}

            log = cache.getLogById(logId)
            if  log==None:
                logging.debug('Log %i not forund in existing data, creating' % logId)
                logUpdates['id'] = [logId,'']
                logUpdates['date'] = [logDate,'']
                logUpdates['type'] = [logType,'']
                logUpdates['finder_id'] = [logFinderId,'']
                logUpdates['finder_name'] = [logFinderName,'']
                logUpdates['encoded'] = [logEncoded,'']
                logUpdates['text'] = [logText,'']

                log = cache.addLog(logId,date=logDate,logType=logType,
                finder_id=logFinderId,finder_name=logFinderName,
                encoded=logEncoded,text=logText)
            else:

                logging.debug('Log %i found in existing data, checking data' % logId)
                if logDate != log.date:
                    logUpdates['id'] = [logDate,log.date]
                    log.date = logDate
                if logType != log.logType:
                    logUpdates['type'] = [logType,log.logType]
                    log.logType = logType
                if logFinderId != log.finder_id:
                    logUpdates['finder_id'] = [logFinderId,log.finder_id]
                    log.finder_id = logFinderId
                if logFinderName != log.finder_name:
                    logUpdates['finder_name'] = [logFinderName,log.finder_name]
                    log.finder_name = logFinderName
                if logEncoded != log.encoded:
                    logUpdates['encoded'] = [logEncoded,log.encoded]
                    log.encoded = logEncoded
                if logText != log.text:
                    logUpdates['text'] = [logText,log.text]
                    log.text = logText
            if len(logUpdates) > 0:
                log.save()
                logsUpdates[logId] = logUpdates
                # Update Own find details if this is the first log with changes
                # in it that is of the "Found it" type and the finderId or
                # finderName matches the users values
                if ((not foundUpdated) and(logFinderId == userId or
                                           logFinderName == userName)):
                    logging.debug('User ID or Name match for log id %i' % logId)
                    if logType in ['Found it', 'Attended']:
                        logging.debug('Log type is found or atttended')
                        if not cache.found:
                            cacheUpdates['found'] = [True,False]
                            cache.found = True
                        if cache.found_date != logDate:
                            cacheUpdates['found_date'] = [logDate,cache.found_date]
                            cache.found_date = logDate
                        foundUpdated = True
                    elif logType == "Didn't find it":
                        logging.debug('Log type is DNF')
                        if not cache.dnf:
                            cacheUpdates['dnf'] = [True,False]
                            cache.dnf = True
                        if cache.dnf_date != logDate:
                            cacheUpdates['dnf_date'] = [logDate,cache.dnf_date]
                            cache.found_date = logDate
                        foundUpdated = True
                    if foundUpdated:
                        if cache.own_log_id != logId:
                            cacheUpdates['own_log_id'] = [logId,cache.own_log_id]
                            cache.own_log_id = logId
                            cache.refreshOwnLog()
        if len(logsUpdates) > 0:
            cacheUpdates['Logs'] = logsUpdates

        tbUpdates = {}
        wptTbRefs = []
        cacheTbRefs = cache.getTravelBugRefs()
        for wptTb in wpt.findall('gs:cache//gs:travelbugs//gs:travelbug', NS):
            wptTbRef = wptTb.attrib['ref']
            wptTbRefs.append(wptTbRef)
            wptTbId = wptTb.attrib['id']
            wptTbName = getTextFromPath(wptTb,'gs:name',NS)
            if not (wptTbRef in cacheTbRefs):
                tbUpdates[wptTbRef + ' ' +wptTbName] = [_('Added'),'']
                cacheTb = cache.addTravelBug(wptTbRef,id=wptTbId,name=wptTbName)
            else:
                cacheTb = cache.getTravelBugByRef(wptTbRef)
                if cacheTb.name != wptTbName:
                    tbUpdates[wptTbRef + ' ' +wptTbName] = [cacheTb.name, wptTbName]
                    cacheTb.name = wptTbName
                    cacheTb.save()
        # Go through the list of travel bugs in the cache and delete any
        # that are not listed in the wpt
        for cacheTbRef in cacheTbRefs:
            if not(cacheTbRef in wptTbRefs):
                toDelete = cache.getTravelBugByRef(cacheTbRef)
                tbUpdates[cacheTbRef + ' ' +toDelete.name] = [_('Removed'),'']
                toDelete.delete()
        if len(tbUpdates) > 0:
            cacheUpdates['Travel Bugs'] = tbUpdates

        if len(cacheUpdates) > 1:
            if cache.gpx_date != gpxDate:
                cache.gpx_date = gpxDate
                if cacheUpdates['change type'] == 'update':
                    cacheUpdates['gpx_date'] = [gpxDate,cache.gpx_date]
            if cache.source != sourceFile:
                cache.source = sourceFile
                cacheUpdates['source'] = [sourceFile,cache.source]
            cache.save()
            fileUpdates[code] = cacheUpdates

    for wpt in extraWpts:
        lon = float(getAttribFromPath(wpt,".","lon",NS,'0.0'))
        lat = float(getAttribFromPath(wpt,".","lat",NS,'0.0'))
        id = getTextFromPath(wpt,'gpx:name',NS)
        time = textToDateTime(getTextFromPath(wpt,'gpx:time',NS))
        cmt = getTextFromPath(wpt,'gpx:cmt',NS,'')
        name = getTextFromPath(wpt,'gpx:desc',NS)
        url = getTextFromPath(wpt,'gpx:url',NS)
        sym = getTextFromPath(wpt,'gpx:sym',NS)
        cacheCode = 'GC'+id[2:]
        cache = geocacher.db().getCacheByCode(cacheCode)
        if cache is not None:
            if cacheCode in fileUpdates.keys():
                cacheUpdates = fileUpdates[cacheCode]
            else:
                cacheUpdates = {}
                cacheUpdates['change type'] = _('update')
            addWaypoint = cache.getAddWaypointByCode(id)
            addWptUpdates = {}
            if 'Add Wpts' in cacheUpdates.keys():
                if id in cacheUpdates['Add Wpts'].keys():
                    addWptUpdates =cacheUpdates['Add Wpts'][id]
            if addWaypoint is None:
                addWaypoint = cache.addAddWaypoint(id,
                                                   lat=lat,
                                                   lon=lon,
                                                   name=name,
                                                   url=url,
                                                   time=time,
                                                   cmt=cmt,
                                                   sym=sym)
                addWptUpdates['id'] = [id,'']
                addWptUpdates['lat'] = [lat,'']
                addWptUpdates['lon'] = [lon,'']
                addWptUpdates['name'] = [name,'']
                addWptUpdates['url'] = [url,'']
                addWptUpdates['time'] = [time,'']
                addWptUpdates['cmt'] = [cmt,'']
                addWptUpdates['sym'] = [sym,'']
            else:
                if addWaypoint.lat != lat:
                    addWptUpdates['lat'] = [lat,addWaypoint.lat]
                    addWaypoint.lat = lat
                if addWaypoint.lon != lon:
                    addWptUpdates['lon'] = [lon,addWaypoint.lon]
                    addWaypoint.lon = lon
                if addWaypoint.name != name:
                    addWptUpdates['name'] = [name,addWaypoint.name]
                    addWaypoint.name = name
                if addWaypoint.url != url:
                    addWptUpdates['url'] = [url,addWaypoint.url]
                    addWaypoint.url = url
                if addWaypoint.time != time:
                    addWptUpdates['time'] = [time,addWaypoint.time]
                    addWaypoint.time = time
                if addWaypoint.cmt != cmt:
                    addWptUpdates['cmt'] = [cmt,addWaypoint.cmt]
                    addWaypoint.cmt = cmt
                if addWaypoint.sym != sym:
                    addWptUpdates['sym'] = [sym,addWaypoint.sym]
                    addWaypoint.sym = sym
            if len(addWptUpdates) > 0:
                cache.gpx_date = gpxDate
                cache.source = os.path.abspath(filename)
                if 'Add Wpts' in cacheUpdates.keys():
                    cacheUpdates['Add Wpts'][id] = addWptUpdates
                else:
                    cacheUpdates['Add Wpts'] = {id: addWptUpdates}
                addWaypoint.save()
                cache.save()
                fileUpdates[cacheCode] = cacheUpdates
    if len(fileUpdates) > 0:
        geocacher.db().commit()

    return (True,fileUpdates)

def gpxExport(filename,caches,gc=False,logs=False,tbs=False,addWpts=False,
              simple=False,full=False,
              correct=True,corMark='',
              maxLogs=None,logOrderDesc=True):
    '''
    Exports the given caches to the given file in the .gpx format.

    Arguments
    filename: Path to the file to export the cache information to
    caches:   List of cache objects to be exported

    Keyword Arguments
    gc:           If True include basic geocaching.com extensions
    logs:         If True include logs (requires gc to be True)
    tbs:          If True include travel bugs (requires gc to be True)
    addWpts:      If True include additional waypoints  (requires gc to be True)
    simple:       If True ignore gc, logs, tbs & addWpts arguments and only
                  include the standard gpx fields
    full:         If True ignore gc, logs, tbs & addWpts arguments and include
                  all possible fields
    correct:      If true use the corrected cordinates for exporting
    corMark:      String to append to the cache code if the cordinates are
                  corrected
    maxLogs:      The maximum number of logs to be exported per cache (None
                  removes any limit)
    logOrderDesc: If True the logs are sorted with the oldeest first otherwise
                  the newest is first
    '''
    assert os.path.isdir(os.path.split(filename)[0])
    gc = (gc and (not simple)) or full
    logs = (logs and (not simple)) or full
    tbs = (tbs and (not simple)) or full
    addWpts = addWpts and (not simple) or full

    if len(caches) == 0:
        return True

    root = gpxInit(caches)

    for cache in caches:
        if correct:
            wpt = ElementTree.SubElement(root,
                                         'wpt',
                                         {'lat':'%f' % cache.currentLat,
                                          'lon':'%f' % cache.currentLon})
        else:
            wpt = ElementTree.SubElement(root, 'wpt', {'lat':'%f' % cache.lat,
                                                       'lon':'%f' % cache.lon})
        if cache.gpx_date == None and cache.user_date == None:
            cacheTime = datetime.now()
        elif cache.gpx_date == None:
            cacheTime=cache.user_date
        elif cache.user_date == None:
            cacheTime=cache.gpx_date
        elif cache.gpx_date < cache.user_date:
            cacheTime=cache.user_date
        else:
            cacheTime=cache.gpx_date
        time = ElementTree.SubElement(wpt, 'time')
        time.text = dateTimeToText(cacheTime)
        name = ElementTree.SubElement(wpt, 'name')
        if correct and cache.corrected:
            name.text = cache.code+corMark
        else:
            name.text = cache.code
        desc = ElementTree.SubElement(wpt, 'desc')
        desc.text = '%s by %s, %s (%0.1f/%0.1f)' % (cache.name, cache.placed_by,
                                              cache.type, cache.difficulty,
                                              cache.terrain)
        if cache.url != '':
            url = ElementTree.SubElement(wpt, 'url')
            url.text = cache.url
            urlname = ElementTree.SubElement(wpt, 'urlname')
            urlname.text = cache.name
        sym = ElementTree.SubElement(wpt, 'sym')
        if cache.found:
            sym.text = 'Geocache Found'
        else:
            sym.text = 'Geocache'
        wpttype = ElementTree.SubElement(wpt, 'type')
        wpttype.text = 'Geocache|%s' % cache.type
        if gc:
            gsCache = ElementTree.SubElement(wpt, GS + 'cache',
                                             {'id':str(cache.id),
                                              'available':str(cache.available),
                                              'archived':str(cache.archived)})
            gsName = ElementTree.SubElement(gsCache, GS + 'name')
            gsName.text = cache.name
            gsPlaced_by = ElementTree.SubElement(gsCache, GS + 'placed_by')
            gsPlaced_by.text = cache.placed_by
            gsOwner = ElementTree.SubElement(gsCache, GS + 'owner',
                                             {'id':str(cache.owner_id)})
            gsOwner.text = cache.owner
            gsType = ElementTree.SubElement(gsCache, GS + 'type')
            gsType.text = cache.type
            gsContainer = ElementTree.SubElement(gsCache, GS + 'container')
            gsContainer.text = cache.container
            gsDifficulty = ElementTree.SubElement(gsCache, GS + 'difficulty')
            gsDifficulty.text = '%0.1f' % cache.difficulty
            gsTerrain = ElementTree.SubElement(gsCache, GS + 'terrain')
            gsTerrain.text = '%0.1f' % cache.terrain
            gsCountry = ElementTree.SubElement(gsCache, GS + 'country')
            gsCountry.text = cache.country
            gsState = ElementTree.SubElement(gsCache, GS + 'state')
            gsState.text = cache.state
            gsShort_desc = ElementTree.SubElement(gsCache,
                                                  GS + 'short_description',
                                                  {'html':str(cache.short_desc_html)})
            gsShort_desc.text = cache.short_desc
            gsLong_desc = ElementTree.SubElement(gsCache,
                                                 GS + 'long_description',
                                                 {'html':str(cache.long_desc_html)})
            gsLong_desc.text = cache.long_desc
            gsHints = ElementTree.SubElement(gsCache, GS + 'encoded_hints')
            gsHints.text = cache.encoded_hints
            if logs:
                gsLogs = ElementTree.SubElement(gsCache, GS + 'logs')
                for log in cache.getLogs(sort=True,
                                         descending=logOrderDesc,
                                         maxLen=maxLogs):
                    gsLog = ElementTree.SubElement(gsLogs, GS + 'log',
                                                   {'id':str(log.logId)})
                    gsLogDate = ElementTree.SubElement(gsLog, GS + 'date')
                    gsLogDate.text = dateTimeToText(log.date)
                    gsLogType = ElementTree.SubElement(gsLog, GS + 'type')
                    gsLogType.text = log.logType
                    gsLogFinder = ElementTree.SubElement(gsLog,
                                                         GS + 'finder',
                                                         {'id':str(log.finder_id)})
                    gsLogFinder.text = log.finder_name
                    gsLogText = ElementTree.SubElement(gsLog,
                                                       GS + 'text',
                                                       {'encoded':str(log.encoded)})
                    gsLogText.text = log.text
            if tbs:
                gsTbs = ElementTree.SubElement(gsCache, GS + 'travelbugs')
                for tb in cache.getTravelBugs():
                    gsTb = ElementTree(gsTbs,
                                       GS +'travelbug',
                                       {'id':str(tb.id),
                                        'ref':tb.ref})
                    gsTbName = ElementTree.SubElement(gsTb, GS + 'name')
                    gsTbName.text = tb.name
        if addWpts:
            gpxExportAddWptProcess(root, cache)

    #try:
    gpxSave(filename,root)
    return True
    #except:
    #    return False

def gpxExportAddWptProcess(root, cache):
    for addWpt in cache.getAddWaypoints():
        wpt = ElementTree.SubElement(root, 'wpt', {'lat':str(addWpt.lat),
                                                   'lon':str(addWpt.lon)})
        time = ElementTree.SubElement(wpt, 'time')
        time.text = dateTimeToText(addWpt.time)
        name = ElementTree.SubElement(wpt, 'name')
        name.text = addWpt.code
        cmt = ElementTree.SubElement(wpt, 'cmt')
        cmt.text = addWpt.cmt
        desc = ElementTree.SubElement(wpt, 'desc')
        desc.text = addWpt.name
        url = ElementTree.SubElement(wpt, 'url')
        url.text = addWpt.url
        urlname = ElementTree.SubElement(wpt, 'urlname')
        urlname.text = addWpt.name
        sym = ElementTree.SubElement(wpt, 'sym')
        sym.text = addWpt.sym
        wpttype = ElementTree.SubElement(wpt, 'type')
        wpttype.text = 'Waypoint|%s' % addWpt.sym

def gpxExportAddWpt(filename,caches):
    if len(caches) == 0:
        return True, 0
    root = gpxInit(caches)
    for cache in caches:
        gpxExportAddWptProcess(root, cache)
    count = len(root.xpath("wpt"))
    if count != 0:
        try:
            gpxSave(filename,root)
        except:
            return False,0
    return True, count

def gpxInit(caches):
    time = dateTimeToText(datetime.now())
    minLat = caches[0].lat
    minLon = caches[0].lon
    maxLat = caches[0].lat
    maxLon = caches[0].lon
    for cache in caches:
        if cache.lat < minLat: minLat=cache.lat
        if cache.lon < minLon: minLon=cache.lon
        if cache.lat > maxLat: maxLat=cache.lat
        if cache.lon > maxLon: maxLon=cache.lon
    gpx_base = '<?xml version="1.0" encoding="utf-8"?>'\
    '<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '\
    'xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1.0" '\
    'creator="Geocacher" '\
    'xsi:schemaLocation="http://www.topografix.com/GPX/1/0 '\
    'http://www.topografix.com/GPX/1/0/gpx.xsd '\
    'http://www.groundspeak.com/cache/1/0 '\
    'http://www.groundspeak.com/cache/1/0/cache.xsd" '\
    'xmlns="http://www.topografix.com/GPX/1/0" '\
    'xmlns:groundspeak="http://www.groundspeak.com/cache/1/0">'\
    '<name>Custom geocache query</name>'\
    '<desc>Custom geocache query generated by Geocacher</desc>'\
    '<author>Geocacher</author>'\
    '<email>rob@wallace.gen.nz</email>'\
    '<time>%s</time>'\
    '<keywords>cache, geocache, groundspeak</keywords>'\
    '<bounds minlat="%f" minlon="%f" maxlat="%f" maxlon="%f" /></gpx>'\
     % (time,minLat,minLon,maxLat,maxLon)

    return ElementTree.fromstring(gpx_base)

def gpxSave(filename,root):
    fid = open(filename,"w")
    fid.write("""<?xml version="1.0" encoding="utf-8"?>""")
    fid.write(ElementTree.tostring(root, encoding="utf-8"))
    fid.close()

def zipLoad(filename,mode="update",userName="",userId=""):
    '''
    Imports the given zip file containing .gpx files into the database.

    Arguments
    filename: path to the file from which to import the cache information

    Keyword Arguments
    mode:     mode to run the import in (update or replace)
    userName: geocaching.com user name for matching cache owner
    userId:   geocaching.com user ID for matching cache owner ID
    '''
    zipChanges = {}
    # Load zipped GPX file(s)
    if os.path.isfile(filename):
        tempDir = tempfile.mkdtemp()
        try:
            archive = zipfile.ZipFile(filename, mode='r')
            archive.extractall(tempDir)
            archive.close()
        except:
            return (False,zipChanges)
        addWptFiles=[]
        for file in os.listdir(tempDir):
            if file.rfind('-wpts') >= 0:
                addWptFiles.append(file)
            else:
                gpxLoad(os.path.join(tempDir,file),
                        mode=mode,
                        userName=userName,userId=userId,
                        fileUpdates=zipChanges,
                        gpxFilename=os.path.abspath(filename))
        for file in addWptFiles:
            gpxLoad(os.path.join(tempDir,file),
                    mode=mode,
                    userName=userName,userId=userId,
                    fileUpdates=zipChanges,
                    gpxFilename=os.path.abspath(filename))
        shutil.rmtree(tempDir)
        return (True,zipChanges)
    else:
        return (False,zipChanges)

def zipExport(filename,caches,gc=False,logs=False,tbs=False,addWpts=False,
              simple=False,full=False,
              sepAddWpts=False,
              correct=True,corMark='',
              maxLogs=None,logOrderDesc=True):
    '''
    Exports the given caches to the given file in the .gpx format.

    Arguments
    filename: Path to the file to export the cache information to
    caches:   List of cache objects to be exported

    Keyword Arguments
    gc:           If True include basic geocaching.com extensions
    logs:         If True include logs (requires gc to be True)
    tbs:          If True include travel bugs (requires gc to be True)
    addWpts:      If True include additional waypoints  (requires gc to be True)
    simple:       If True ignore gc, logs, tbs & addWpts arguments and only
                  include the standard gpx fields
    full:         If True ignore gc, logs, tbs & addWpts arguments and include
                  all possible fields
    sepAddWpts:   If True any additional waypooints are put in a seperate file
                  within the zip archive
    correct:      If true use the corrected cordinates for exporting
    corMark:      String to append to the cache code if the cordinates are
                  corrected
    maxLogs:      The maximum number of logs to be exported per cache (None
                  removes any limit)
    logOrderDesc: If True the logs are sorted with the oldeest first otherwise
                  the newest is first
    '''
    assert os.path.isdir(os.path.split(filename)[0])

    if len(caches) == 0:
        return True

    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except:
            return False

    gc = (gc and (not simple)) or full
    logs = (logs and (not simple)) or full
    tbs = (tbs and (not simple)) or full
    addWpts = addWpts and (not simple) or full

    baseName = os.path.splitext(os.path.basename(filename))[0]
    try:
        tempDir = tempfile.mkdtemp()
        archive = zipfile.ZipFile(filename,
                                  mode='w',
                                  compression=zipfile.ZIP_DEFLATED)
    except:
        return False

    gpxFileName = os.path.join(tempDir, baseName+'.gpx')
    ret1 = gpxExport(gpxFileName,caches,gc=gc,logs=logs,tbs=tbs,
                     addWpts=addWpts and not sepAddWpts,
                     correct=correct,corMark=corMark,
                     maxLogs=maxLogs,logOrderDesc=logOrderDesc)
    archive.write(gpxFileName, os.path.basename(gpxFileName).encode("utf_8"))

    if addWpts and sepAddWpts:

        gpxAddFileName = os.path.join(tempDir, baseName+'-wpts.gpx')
        ret2, count = gpxExportAddWpt(gpxAddFileName,caches)
        if count != 0:
            archive.write(gpxAddFileName,
                          os.path.basename(gpxAddFileName).encode("utf_8"))
    else:
        ret2 = True

    archive.close()

    shutil.rmtree(tempDir)
    return ret1 and ret2
