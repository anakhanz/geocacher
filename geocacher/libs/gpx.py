# -*- coding: UTF-8 -*-

from datetime import datetime
from lxml.etree import Element,ElementTree,XML
import os
import shutil
import tempfile
import zipfile

from libs.common import textToBool,textToDateTime,dateTimeToText #@UnresolvedImport
from libs.common import getTextFromPath,getAttribFromPath #@UnresolvedImport

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
            cache.lon = lon
            cache.lat = lat
            cache.id = id
            cache.available = available
            cache.archived = archived
            cache.name = name
            cache.url = url
            cache.symbol = symbol
            cache.placed = placed
            cache.placed_by = placed_by
            cache.owner = owner
            cache.owner_id = owner_id
            cache.type = cachetype
            cache.container = container
            cache.difficulty = difficulty
            cache.terrain = terrain
            cache.state = state
            cache.country = country
            cache.short_desc = short_desc
            cache.short_desc_html = short_desc_html
            cache.long_desc = long_desc
            cache.long_desc_html = long_desc_html
            cache.encoded_hints = hints
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
                    log.date = logDate
                    changed = True
                if logType != log.type:
                    log.type = logType
                    changed = True
                if logFinderId != log.finder_id:
                    log.finder_id = logFinderId
                    changed = True
                if logFinderName != log.finder_name:
                    log.finder_name = logFinderName
                    changed = True
                if logEncoded != log.encoded:
                    log.encoded = logEncoded
                    changed = True
                if logText != log.text:
                    log.text = logText
                    changed = True
                updated |= changed
            # Update Own find details if this is the first log with changes
            # in it that is of the "Found it" type and the finderId or
            # finderName matches the users values
            if ((not foundUpdated) and changed and(logFinderId == userId or logFinderName == userName)):
                if logType =='Found it':
                    cache.found = True
                    cache.found_date = logDate
                elif logType == "Didn't find it":
                    cache.dnf = True
                    cache.dnf_date = logDate
                if logType =='Found it' or logType == "Didn't find it":
                    cache.own_log = logText
                    cache.own_log_encoded = logEncoded
                    foundUpdated=True
        wptTbRefs = []
        cacheTbRefs = cache.getTravelBugRefs()
        for wptTb in wpt.xpath('gs:cache//gs:travelbugs//gs:travelbug', namespaces=NS):
            wptTbRef = wptTb.attrib['ref']
            wptTbRefs.append(wptTbRef)
            wptTbId = wptTb.attrib['id']
            wptTbName = getTextFromPath(wptTb,'gs:name',NS)
            if not (wptTbRef in cacheTbRefs):
                cacheTb = cache.addTravelBug(wptTbRef,id=wptTbId,name=wptTbName)
            else:
                cacheTb = cache.getTravelBugByRef(wptTbRef)
                cacheTb.od = wptTbId
                cacheTb.name = wptTbName
        # Go through the list of travel bugs in the cache and delete any
        # that are not listed in the wpt
        for cacheTbRef in cacheTbRefs:
            if not(cacheTbRef in wptTbRefs):
                cache.getTravelBugByRef(cacheTbRef).delete()
                updated = True

        if updated:
            cache.gpx_date = gpxDate
            cache.source = os.path.abspath(filename)

    for wpt in extraWpts:
        updated = False
        lon = float(wpt.attrib['lon'])
        lat = float(wpt.attrib['lat'])
        id = getTextFromPath(wpt,'gpx:name',NS)
        time = textToDateTime(getTextFromPath(wpt,'gpx:time',NS))
        cmt = getTextFromPath(wpt,'gpx:cmt',NS,'')
        name = getTextFromPath(wpt,'gpx:desc',NS)
        url = getTextFromPath(wpt,'gpx:url',NS)
        sym = getTextFromPath(wpt,'gpx:sym',NS)
        cache = DB.getCacheByCode('GC'+id[2:])
        if cache != None:
            addWaypoint = cache.getAddWaypointByCode(id)
            if addWaypoint == None:
                cache.addAddWaypoint(id,lat=lat,lon=lon,name=name,url=url,time=time,cmt=cmt,sym=sym)
                updated = True
            else:
                addWaypoint.lat = lat
                addWaypoint.lon = lon
                addWaypoint.time = time
                addWaypoint.cmt = cmt
                addWaypoint.name = name
                addWaypoint.url = url
                addWaypoint.sym = sym
            if updated:
                cache.gpx_date = gpxDate
                cache.source = os.path.abspath(filename)

def gpxExport(filename,caches,gc=False,logs=False,tbs=False,addWpts=False,
              simple=False,full=False,maxLogs=4,correct=True,corMark='-A'):
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
            wpt = Element('wpt', lat='%f' % cache.currentLat, lon='%f' % cache.currentLon)
        else:
            wpt = Element('wpt', lat='%f' % cache.lat, lon='%f' % cache.lon)
        root.append(wpt)
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
        time = Element('time')
        time.text = dateTimeToText(cacheTime)
        wpt.append(time)
        name = Element('name')
        if correct and cache.corrected:
            name.text = cache.code+corMark
        else:
            name.text = cache.code
        wpt.append(name)
        desc = Element('desc')
        desc.text = '%s by %s, %s (%0.1f/%0.1f)' % (cache.name, cache.placed_by,
                                              cache.type, cache.difficulty,
                                              cache.terrain)
        wpt.append(desc)
        if cache.url != '':
            url = Element('url')
            url.text = cache.url
            wpt.append(url)
            urlname = Element('urlname')
            urlname.text = cache.name
            wpt.append(urlname)
        sym = Element('sym')
        if cache.found:
            sym.text = 'Geocache Found'
        else:
            sym.text = 'Geocache'
        wpt.append(sym)
        type = Element('type')
        type.text = 'Geocache|%s' % cache.type
        wpt.append(type)
        if gc:
            GS_NAMESPACE = "http://www.groundspeak.com/cache/1/0"
            GS = "{%s}" %GS_NAMESPACE
            gsCache = Element(GS + 'cache',id=cache.id,
                                available=str(cache.available),
                                archived=str(cache.archived))
            wpt.append(gsCache)
            gsName = Element(GS + 'name')
            gsName.text = cache.name
            gsCache.append(gsName)
            gsPlaced_by = Element(GS + 'placed_by')
            gsPlaced_by.text = cache.placed_by
            gsCache.append(gsPlaced_by)
            gsOwner = Element(GS + 'owner', id=cache.owner_id)
            gsOwner.text = cache.owner
            gsCache.append(gsOwner)
            gsType = Element(GS + 'type')
            gsType.text = cache.type
            gsCache.append(gsType)
            gsContainer = Element(GS + 'container')
            gsContainer.text = cache.container
            gsCache.append(gsContainer)
            gsDifficulty = Element(GS + 'difficulty')
            gsDifficulty.text = '%0.1f' % cache.difficulty
            gsCache.append(gsDifficulty)
            gsTerrain = Element(GS + 'terrain')
            gsTerrain.text = '%0.1f' % cache.terrain
            gsCache.append(gsTerrain)
            gsCountry = Element(GS + 'country')
            gsCountry.text = cache.country
            gsCache.append(gsCountry)
            gsState = Element(GS + 'state')
            gsState.text = cache.state
            gsCache.append(gsState)
            gsShort_desc = Element(GS + 'short_description', html=str(cache.short_desc_html))
            gsShort_desc.text = cache.short_desc
            gsCache.append(gsShort_desc)
            gsLong_desc = Element(GS + 'long_description', html=str(cache.long_desc_html))
            gsLong_desc.text = cache.long_desc
            gsCache.append(gsLong_desc)
            gsHints = Element(GS + 'encoded_hints')
            gsHints.text = cache.encoded_hints
            gsCache.append(gsHints)
            if logs:
                gsLogs = Element(GS + 'logs')
                gsCache.append(gsLogs)
                for log in cache.getLogs():
                    gsLog = Element(GS + 'log', id=log.id)
                    gsLogs.append(gsLog)
                    gsLogDate = Element(GS + 'date')
                    gsLogDate.text = dateTimeToText(log.date)
                    gsLog.append(gsLogDate)
                    gsLogType = Element(GS + 'type')
                    gsLogType.text = log.type
                    gsLog.append(gsLogType)
                    gsLogFinder = Element(GS + 'finder', id=log.finder_id)
                    gsLogFinder.text = log.finder_name
                    gsLog.append(gsLogFinder)
                    gsLogText = Element(GS + 'text', encoded=str(log.encoded))
                    gsLogText.text = log.text
                    gsLog.append(gsLogText)
            if tbs:
                gsTbs = Element(GS + 'travelbugs')
                gsCache.append(gsTbs)
                for tb in cache.getTravelBugs():
                    gsTb = Element(GS + 'travelbug', id=tb.id, ref=tb.ref)
                    gsTbs.append(gsTb)
                    gsTbName = Element(GS + 'name')
                    gsTbName.text = tb.name
                    gsTb.append(gsTbName)
        if addWpts:
            gpxExportAddWptProcess(root, cache)

    try:
        gpxSave(filename,root)
        return True
    except:
        return False

def gpxExportAddWptProcess(root, cache):
    for addWpt in cache.getAddWaypoints():
        wpt = Element('wpt', lat=str(addWpt.lat), lon=str(addWpt.lon))
        root.append(wpt)
        time = Element('time')
        time.text = dateTimeToText(addWpt.time)
        wpt.append(time)
        name = Element('name')
        name.text = addWpt.code
        wpt.append(name)
        cmt = Element('cmt')
        cmt.text = addWpt.cmt
        wpt.append(cmt)
        desc = Element('desc')
        desc.text = addWpt.name
        wpt.append(desc)
        url = Element('url')
        url.text = addWpt.url
        wpt.append(url)
        urlname = Element('urlname')
        urlname.text = addWpt.name
        wpt.append(urlname)
        sym = Element('sym')
        sym.text = addWpt.sym
        wpt.append(sym)
        type = Element('type')
        type.text = 'Waypoint|%s' % addWpt.sym
        wpt.append(type)

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
    '<time>%s</time>'\
    '<bounds minlat="%f" minlon="%f" maxlat="%f" maxlon="%f" /></gpx>'\
     % (time,minLat,minLon,maxLat,maxLon)

    return XML(gpx_base)

def gpxSave(filename,root):
    fid = open(filename,"w")
    fid.write("""<?xml version="1.0" encoding="utf-8"?>""")
    ElementTree(root).write(fid,encoding="utf-8")
    fid.close()

def zipLoad(filename,DB,mode="update",userName="",userId=""):
    # Load zipped GPX file(s)
    # TODO: implement returning of changes from zipped GPX file for reporting to user
    if os.path.isfile(filename):
        tempDir = tempfile.mkdtemp()
        try:
            archive = zipfile.ZipFile(filename, mode='r')
            archive.extractall(tempDir)
            archive.close()
        except:
            return False
        addWptFiles=[]
        for file in os.listdir(tempDir):
            if file.rfind('-wpts') >= 0:
                addWptFiles.append(file)
            else:
                gpxLoad(os.path.join(tempDir,file),DB,mode=mode,userName=userName,userId=userId)
        for file in addWptFiles:
            gpxLoad(os.path.join(tempDir,file),DB,mode=mode,userName=userName,userId=userId)
        shutil.rmtree(tempDir)
        return True
    else:
        return False

def zipExport(filename,caches,gc=False,logs=False,tbs=False,addWpts=False,simple=False,full=False, sepAddWpts=False):
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
        archive = zipfile.ZipFile(filename, mode='w', compression=zipfile.ZIP_DEFLATED)
    except:
        return False

    gpxFileName = os.path.join(tempDir, baseName+'.gpx')
    ret1 = gpxExport(gpxFileName,caches,gc=gc,logs=logs,tbs=tbs,addWpts=addWpts and not sepAddWpts)
    archive.write(gpxFileName, os.path.basename(gpxFileName).encode("utf_8"))

    if addWpts and sepAddWpts:

        gpxAddFileName = os.path.join(tempDir, baseName+'-wpts.gpx')
        ret2, count = gpxExportAddWpt(gpxAddFileName,caches)
        if count != 0:
            archive.write(gpxAddFileName, os.path.basename(gpxAddFileName).encode("utf_8"))

    archive.close()

    shutil.rmtree(tempDir)
    return ret1 and ret2

