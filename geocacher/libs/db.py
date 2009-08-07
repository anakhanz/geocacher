# -*- coding: UTF-8 -*-
'''Module to implement the persistant data stores'''
import datetime
from lxml.etree import Element,ElementTree
import os
import string

from libs import dict4ini
from libs.common import textToBool,boolToText,textToDateTime,dateTimeToText
from libs.common import getTextFromPath,getAttribFromPath

VERSION = 1
ROOT_ELEMENT = 'db'

class DB:
    '''Database for all non configuration data in the geocacher application'''

    def __init__(self,file):
        '''Load the DB or initalise if missing'''
        try:
            self.root = ElementTree(file=file).getroot()
            version = int(self.root.attrib["version"])
            self.update()
        except:
            self.root = Element(ROOT_ELEMENT,version=str(VERSION))
            version=VERSION
            self.addLocation('Default')
        self.file = file

    def save(self):
        '''Saves the DB'''
        self.backup(self.file)

    def backup(self, file):
        '''Save the DB to the given file'''
        fid = open(file,"w")
        fid.write("""<?xml version="1.0" encoding="utf-8"?>""")
        ElementTree(self.root).write(fid,encoding="utf-8")
        fid.close()

    def restore(self, file):
        '''Restores the DB from the given file'''
        try:
            newRoot = ElementTree(file=file).getroot()
            tag = newRoot.tag
            version = int(newRoot.attrib["version"])
        except:
            return False
        if tag == ROOT_ELEMENT and version == VERSION:
            self.root = newRoot
            self.update()

    def update(self):
        pass

    def getCacheList(self):
        '''Returns a list of caches'''
        cacheList = []
        for cacheNode in self.root.xpath(u"cache"):
            cacheList.append(Cache(cacheNode))
        return cacheList

    def getCacheCodeList(self):
        '''Returns a list of cache codes'''
        cacheCodeList = []
        for cacheNode in self.root.xpath(u"cache"):
            cacheCodeList.append(cacheNode.attrib["code"])
        return cacheCodeList

    def getCacheByCode(self,code):
        '''Returns the cache with the given code if found, otherwise "None"'''
        caches = self.root.xpath(u"""cache[@code="%s"]""" % code)
        if len(caches) > 0:
            return Cache(caches[0])
        else:
            return None

    def addCache(self,code,
                        id="aa",
                        lat=0.0,
                        lon=0.0,
                        name="",
                        url="",
                        locked=False,
                        user_date=None,
                        gpx_date=None,
                        symbol="Geocache",
                        placed=None,
                        placed_by="",
                        owner="",
                        owner_id="",
                        container="Not chosen",
                        difficulty=0.0,
                        terrain=0.0,
                        type="Traditional Cache",
                        available=True,
                        archived=False,
                        state="",
                        country="",
                        short_desc="",
                        short_desc_html=False,
                        long_desc="",
                        long_desc_html=False,
                        encoded_hints="",
                        ftf=False,
                        found=False,
                        found_date=None,
                        dnf=False,
                        dnf_date=None,
                        own_log="",
                        own_log_encoded=False,
                        source="",
                        corrected=False,
                        clat=0.0,
                        clon=0.0,
                        cnote="",
                        user_comments="",
                        user_flag=False,
                        user_data1="",
                        user_data2="",
                        user_data3="",
                        user_data4=""):
        '''Creates a new cache with the given data'''
        newCache=Element("cache",code=code,
                            id         = "%s" % id,
                            lat        = "%f" % lat,
                            lon        = "%f" % lon,
                            name       = "%s" % name,
                            url        = "%s" % url,
                            locked     = boolToText(locked),
                            user_date  = "%s" % dateTimeToText(user_date),
                            gpx_date   = "%s" % dateTimeToText(gpx_date),
                            symbol     = "%s" % symbol,
                            type       = "%s" % type,
                            placed     = "%s" % dateTimeToText(placed),
                            placed_by  = "%s" % placed_by,
                            owner      = "%s" % owner,
                            owner_id   = "%s" % owner_id,
                            container  = "%s" % container,
                            difficulty = "%1.1f" % difficulty,
                            terrain    = "%1.1f" % terrain,
                            available  = boolToText(available),
                            archived   = boolToText(archived),
                            state      = "%s" % state,
                            country    = "%s" % country,
                            found      = boolToText(found),
                            ftf        = boolToText(ftf),
                            found_date = "%s" % dateTimeToText(found_date),
                            dnf        = boolToText(dnf),
                            dnf_date   = "%s" % dateTimeToText(dnf_date),
                            source     = "%s" % source,
                            corrected  = boolToText(corrected),
                            clat       = "%f" % clat,
                            clon       = "%f" % clon,
                            user_flag  = boolToText(user_flag),
                            user_data1 = "%s" % user_data1,
                            user_data2 = "%s" % user_data2,
                            user_data3 = "%s" % user_data3,
                            user_data4 = "%s" % user_data4)
        sDesc = Element("short_description",html=boolToText(short_desc_html))
        sDesc.text = short_desc
        newCache.append(sDesc)
        lDesc = Element("long_description",html=boolToText(long_desc_html))
        lDesc.text = long_desc
        newCache.append(lDesc)
        hints = Element("encoded_hints")
        hints.text = encoded_hints
        newCache.append(hints)
        ownLog = Element("own_log",encoded=boolToText(own_log_encoded))
        ownLog.text=own_log
        newCache.append(ownLog)
        userComments = Element("user_comments")
        userComments.text = user_comments
        newCache.append(userComments)
        cNote  = Element("cnote")
        cNote.text = cnote
        newCache.append(cNote)
        self.root.append(newCache)
        return Cache(newCache)

    def getLocationList(self):
        '''Returns a list of home locations'''
        locationList = []
        for locationNode in self.root.xpath(u"location"):
            locationList.append(Location(locationNode))
        return cacheList

    def getLocationNameList(self):
        '''Returns a list of home location names'''
        locationNameList = []
        for locationNode in self.root.xpath(u"location"):
            locationNameList.append(locationNode.attrib["name"])
        locationNameList.sort()
        return locationNameList

    def getLocationByName(self,name):
        '''Returns the location with the given name if found, otherwise "None"'''
        locations = self.root.xpath(u"""location[@name="%s"]""" % name)
        if len(locations) > 0:
            return Location(locations[0])
        else:
            return None

    def addLocation(self,name,lat=0.0,lon=0.0,comment=""):
        '''Adds a new location with the given data'''
        newLocation = Element('location',name=name, lat="%f" % lat, lon="%f" % lon)
        newLocation.text = comment
        self.root.append(newLocation)
        return Location(newLocation)

class Cache(object):
    def __init__(self,n):
        assert n.tag == "cache"
        self.__node = n

    def __getCode(self):    return self.__node.attrib["code"]
    code = property(__getCode)

    def __getId(self):    return self.__node.attrib["id"]

    def __setId(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["id"] = t

    id = property(__getId, __setId)

    def __getLat(self):    return float(self.__node.attrib["lat"])

    def __setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    lat = property(__getLat, __setLat)

    def __getLon(self):    return float(self.__node.attrib["lon"])

    def __setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    lon = property(__getLon, __setLon)

    def __getCurrentLat(self):
        if self.corrected:
            return self.clat
        else:
            return self.lat
    currentLat = property(__getCurrentLat)

    def __getCurrentLon(self):
        if self.corrected:
            return self.clon
        else:
            return self.lon
    currentLon = property(__getCurrentLon)

    def __getName(self):    return self.__node.attrib["name"]

    def __setName(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["name"] = t

    name = property(__getName,__setName)

    def __getUrl(self):    return self.__node.attrib["url"]

    def __setUrl(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["url"] = t

    url = property(__getUrl,__setUrl)

    def __getLocked(self):    return textToBool(self.__node.attrib["locked"])
    locked = property(__getLocked)

    def __getUser_date(self):    return textToDateTime(self.__node.attrib["user_date"])

    def __setUser_date(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["user_date"] = dateTimeToText(dt)

    user_date = property(__getUser_date, __setUser_date)

    def __getGpx_date(self):    return textToDateTime(self.__node.attrib["gpx_date"])

    def __setGpx_date(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["gpx_date"] = dateTimeToText(dt)

    gpx_date = property(__getGpx_date, __setGpx_date)

    def __getSymbol(self):    return self.__node.attrib["symbol"]

    def __setSymbol(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["symbol"] = t

    symbol = property(__getSymbol, __setSymbol)

    def __getPlaced(self):
        return textToDateTime(self.__node.attrib["placed"])

    def __setPlaced(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["placed"] = dateTimeToText(dt)

    placed = property(__getPlaced, __setPlaced)

    def __getPlaced_by(self):    return self.__node.attrib["placed_by"]

    def __setPlaced_by(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["placed_by"] = t

    placed_by = property(__getPlaced_by, __setPlaced_by)

    def __getOwner(self):    return self.__node.attrib["owner"]

    def __setOwner(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["owner"] = t

    owner = property(__getOwner, __setOwner)

    def __getOwner_id(self):    return self.__node.attrib["owner_id"]

    def __setOwner_id(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["owner_id"] = t

    owner_id = property(__getOwner_id, __setOwner_id)

    def __getContainer(self):    return self.__node.attrib["container"]

    def __setContainer(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO: add assertion that the container type is a valid one
        self.__node.attrib["container"] = t

    container = property(__getContainer, __setContainer)

    def __getDifficulty(self):    return float(self.__node.attrib["difficulty"])

    def __setDifficulty(self,f):
        assert type(f)==float
        assert f >= 0 and f <=5
        self.__node.attrib["difficulty"] = "%1.1f" % f

    difficulty = property(__getDifficulty, __setDifficulty)

    def __getTerrain(self):    return float(self.__node.attrib["terrain"])

    def __setTerrain(self,f):
        assert type(f)==float
        assert f >= 0 and f <=5
        self.__node.attrib["terrain"] = "%1.1f" % f

    terrain = property(__getTerrain, __setTerrain)

    def __getType(self):    return self.__node.attrib["type"]

    def __setType(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO: add assertion that the type is a valid one
        self.__node.attrib["type"] = t

    type= property(__getType, __setType)

    def __getAvailable(self):    return textToBool(self.__node.attrib["available"])

    def __setAvailable(self,b):
        assert type(b) == bool
        self.__node.attrib["available"] = boolToText(b)

    available = property(__getAvailable, __setAvailable)

    def __getArchived(self):    return textToBool(self.__node.attrib["archived"])

    def __setArchived(self,b):
        assert type(b) == bool
        self.__node.attrib["archived"] = boolToText(b)

    archived = property(__getArchived, __setArchived)

    def __getState(self):    return self.__node.attrib["state"]

    def __setState(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["state"] = t

    state = property(__getState, __setState)

    def __getCountry(self):    return self.__node.attrib["country"]

    def __setCountry(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["country"] = t

    country = property(__getCountry, __setCountry)

    def __getShort_desc(self):
        return self.__node.xpath("short_description")[0].text

    def __setShort_desc(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("short_description")[0].text = t

    short_desc = property(__getShort_desc, __setShort_desc)

    def __getShort_desc_html(self):
        return textToBool(self.__node.xpath("short_description")[0].attrib["html"])

    def __setShort_desc_html(self,b):
        assert type(b)==bool
        self.__node.xpath("short_description")[0].attrib["html"] = boolToText(b)

    short_desc_html = property(__getShort_desc_html, __setShort_desc_html)

    def __getLong_desc(self):
        return self.__node.xpath("long_description")[0].text

    def __setLong_desc(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("long_description")[0].text = t

    long_desc = property(__getLong_desc, __setLong_desc)

    def __getLong_desc_html(self):
        return textToBool(self.__node.xpath("long_description")[0].attrib["html"])

    def __setLong_desc_html(self,b):
        assert type(b)==bool
        self.__node.xpath("long_description")[0].attrib["html"] = boolToText(b)

    long_desc_html = property(__getLong_desc_html, __setLong_desc_html)

    def __getEncoded_hints(self):
        return self.__node.xpath("encoded_hints")[0].text

    def __setEncoded_hints(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("encoded_hints")[0].text = t

    encoded_hints = property(__getEncoded_hints, __setEncoded_hints)

    def __getFtf(self):    return textToBool(self.__node.attrib["ftf"])

    def __setFtf(self,b):
        assert type(b) == bool
        self.__node.attrib["ftf"] = boolToText(b)

    ftf = property(__getFtf, __setFtf)

    def __getFound(self):    return textToBool(self.__node.attrib["found"])

    def __setFound(self,b):
        assert type(b) == bool
        self.__node.attrib["found"] = boolToText(b)

    found = property(__getFound, __setFound)

    def __getFound_date(self):
        return textToDateTime(self.__node.attrib["found_date"])

    def __setFound_date(self,dt):
        assert type(dt) == datetime.datetime or dt == None
        if dt == None:
            self.__node.attrib["found_date"] = ''
        else:
            self.__node.attrib["found_date"] = dateTimeToText(dt)

    found_date = property(__getFound_date, __setFound_date)

    def __getDnf(self):    return textToBool(self.__node.attrib["dnf"])

    def __setDnf(self,b):
        assert type(b) == bool
        self.__node.attrib["dnf"] = boolToText(b)

    dnf = property(__getDnf, __setDnf)

    def __getDnf_date(self):
        return textToDateTime(self.__node.attrib["dnf_date"])

    def __setDnf_date(self,dt):
        assert type(dt)==datetime.datetime or dt == None
        if dt == None:
            self.__node.attrib["dnf_date"] = ''
        else:
            self.__node.attrib["dnf_date"] = dateTimeToText(dt)

    dnf_date = property(__getDnf_date, __setDnf_date)

    def __getOwn_log(self):    return self.__node.xpath("own_log")[0].text

    def __setOwn_log(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("own_log")[0].text = t

    own_log = property(__getOwn_log, __setOwn_log)

    def __getOwn_log_encoded(self):
        return textToBool(self.__node.xpath("own_log")[0].attrib["encoded"])

    def __setOwn_log_encoded(self,b):
        assert type(b)==bool
        self.__node.xpath("own_log")[0].attrib["encoded"] = boolToText(b)

    own_log_encoded = property(__getOwn_log_encoded, __setOwn_log_encoded)

    def __getCorrected(self):
        return textToBool(self.__node.attrib["corrected"])

    def __setCorrected(self,b):
        assert type(b) == bool
        self.__node.attrib["corrected"] = boolToText(b)

    corrected = property(__getCorrected, __setCorrected)

    def __getCLat(self):    return float(self.__node.attrib["clat"])

    def __setCLat(self,f):
        assert type(f) == float
        self.__node.attrib["clat"] = "%f" % f

    clat = property(__getCLat, __setCLat)

    def __getCLon(self):    return float(self.__node.attrib["clon"])

    def __setCLon(self,f):
        assert type(f) == float
        self.__node.attrib["clon"] = "%f" % f

    clon = property(__getCLon, __setCLon)

    def __getCNote(self):
        ret = self.__node.xpath("cnote")[0].text
        if ret == None:
            ret = ""
        return ret

    def __setCNote(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("cnote")[0].text = t

    cnote = property(__getCNote, __setCNote)

    def __getSource(self):    return self.__node.attrib["source"]

    def __setSource(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["source"] = t

    source = property(__getSource, __setSource)

    def __getUser_comments(self):
        return self.__node.xpath("user_comments")[0].text

    def __setUser_comments(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("user_comments")[0].text = t

    user_comments = property(__getUser_comments, __setUser_comments)

    def __getUser_flag(self):
        return textToBool(self.__node.attrib["user_flag"])

    def __setUser_flag(self,b):
        assert type(b) == bool
        self.__node.attrib["user_flag"] = boolToText(b)

    user_flag = property(__getUser_flag, __setUser_flag)

    def __getUser_data1(self):    return self.__node.attrib["user_data1"]

    def __setUser_data1(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data1"] = t

    user_data1 = property(__getUser_data1, __setUser_data1)

    def __getUser_data2(self):    return self.__node.attrib["user_data2"]

    def __setUser_data2(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data2"] = t

    user_data2 = property(__getUser_data2, __setUser_data2)

    def __getUser_data3(self):    return self.__node.attrib["user_data3"]

    def __setUser_data3(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data3"] = t

    user_data3 = property(__getUser_data3, __setUser_data3)

    def __getUser_data4(self):    return self.__node.attrib["user_data4"]

    def __setUser_data4(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data4"] = t

    user_data4 = property(__getUser_data4, __setUser_data4)

    def getLogs(self):
        '''Returns the logs associated with the cache'''
        logNodes = self.__node.xpath("log")
        logs=[]
        for logNode in logNodes:
            logs.append(Log(logNode))
        return logs

    def getLogIdList(self):
        '''Returns a list of the ID's of the logs associated with the cache'''
        logNodes = self.__node.xpath("log")
        logIds=[]
        for logNode in logNodes:
            logIds.append(logNode.attrib["id"])
        return logIds

    def getNumLogs(self):
        '''Returns the number of logs in the DB for the cache'''
        return len(self.__node.xpath("log"))

    def getLogById(self,id):
        '''Returns the log with the given id if found, otherwise "None"'''
        assert type(id)==unicode or type(id)==str
        logs = self.__node.xpath(u"""log[@id="%s"]""" % id)
        if len(logs) > 0:
            return Log(logs[0])
        else:
            return None

    def getLogDates(self):
        '''
        Returns a sorted list of the dates on which the cache has been logged
        with the most recent first
        '''
        logs = self.__node.xpath("log")
        dates = []
        if logs != None:
            for log in logs:
                dates.append(Log(log).date)
        dates.sort(reverse=True)
        return dates

    def getLastLogDate(self):
        '''Returns the date of the last log or None if no logs'''
        dates = self.getLogDates()
        if len(dates) == 0:
            return None
        else:
            return dates[0]

    def getFoundDates(self):
        '''
        Returns a sorted list of the dates on which the cache has been found
        with the most recent first
        '''
        logs = self.__node.xpath(u"""log[@type="%s"]""" % 'Found it')
        dates = []
        if logs != None:
            for log in logs:
                dates.append(Log(log).date)
        dates.sort(reverse=True)
        return dates

    def getLastFound(self):
        '''Returns the date on which the cache was found or None if never Found'''
        dates = self.getFoundDates()
        if len(dates) == 0:
            return None
        else:
            return dates[0]

    def getFoundCount(self):
        return len(self.getFoundDates())

    def addLog(self,id,
                    date        = None,
                    type        = u"",
                    finder_id   = u"",
                    finder_name = u"",
                    encoded     = False,
                    text        = u""):
        '''Adds a log to the cache with the given information'''
        if date == None:
            dateText = u""
        else:
            dateText = dateTimeToText(date)
        log = Element("log",id          = id,
                            date        = dateText,
                            type        = type,
                            finder_id   =finder_id,
                            finder_name = finder_name,
                            encoded     = boolToText(encoded))
        log.text = text
        self.__node.append(log)
        return Log(log)

    def getTravelBugs(self):
        '''Returns a list of the travel bugs in the cache'''
        bugNodes = self.__node.xpath("travelbug")
        bugs=[]
        for bugNode in bugNodes:
            bugs.append(TravelBug(bugNode))
        return bugs

    def getTravelBugRefs(self):
        '''Returns a list of th ref's of the travel bugs in the cache'''
        bugNodes = self.__node.xpath("travelbug")
        bugRefs=[]
        for bugNode in bugNodes:
            bugRefs.append(TravelBug(bugNode).ref)
        return bugRefs

    def hasTravelBugs(self):
        '''Returns True if the cache has travel bugs in it at present'''
        return len(self.__node.xpath("travelbug")) > 0

    def getTravelBugByRef(self,ref):
        '''Returns the travel bug with the given ref if found, otherwise "None"'''
        assert type(ref)==unicode or type(ref)==str
        bugs = self.__node.xpath(u"""travelbug[@ref="%s"]""" % ref)
        if len(bugs) > 0:
            return TravelBug(bugs[0])
        else:
            return None

    def addTravelBug(self,ref,id=u"",name=u""):
        '''Adds a travel bug tto the cache with the given information'''
        travelbug = Element("travelbug",ref=ref,id=id)
        travelbug.text = name
        self.__node.append(travelbug)
        return TravelBug(travelbug)

    def getAddWaypoints(self):
        '''Returns a list of the additional waypoints associated with the cache'''
        addWptNodes = self.__node.xpath("add_wpt")
        addWpts=[]
        for addWptNode in addWptNodes:
            addWpts.append(AddWaypoint(addWptNode))
        return addWpts

    def getAddWaypointCodes(self):
        '''Returns a list of the codes of the waypoints associated with the cache'''
        addWptNodes = self.__node.xpath("add_wpt")
        addWptCodes=[]
        for addWptNode in addWptNodes:
            addWptCodes.append(AddWaypoint(addWptNode).code)
        return addWptCodes

    def getAddWaypointByCode(self,code):
        '''Returns the additional waypoint with the given code if found, otherwise "None"'''
        assert type(code)==unicode or type(code)==str
        addWpts = self.__node.xpath(u"""add_wpt[@code="%s"]""" % code)
        if len(addWpts) > 0:
            return AddWaypoint(addWpts[0])
        else:
            return None


    def addAddWaypoint(self,code,lat  = 0,
                                 lon  = 0,
                                 name = u"",
                                 url  = "",
                                 time = None,
                                 cmt  = u"",
                                 sym  = u""):
        '''Adds an additional waypoint to the cache with the given information'''
        if time == None:
            timeText = u""
        else:
            timeText = dateTimeToText(time)
        latText = "%f" % lat
        lonText = "%f" % lon
        addWpt = Element("add_wpt",code=code,lat=latText,lon=lonText,name=name,url=url,time=timeText,sym=sym)
        addWpt.text = cmt
        self.__node.append(addWpt)
        return AddWaypoint(addWpt)

    def delete(self):
        self.__node.getparent().remove(self.__node)

class Log(object):
    def __init__(self,n):
        assert n.tag == "log"
        self.__node = n

    def __getId(self):    return self.__node.attrib["id"]
    id = property(__getId)

    def __getDate(self):    return textToDateTime(self.__node.attrib["date"])

    def __setDate(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["date"] = dateTimeToText(dt)

    date = property(__getDate, __setDate)

    def __getType(self):    return self.__node.attrib["type"]

    def __setType(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO add assertion that the type is valid
        self.__node.attrib["type"] = t

    type = property(__getType, __setType)

    def __getFinder_id(self):    return self.__node.attrib["finder_id"]

    def __setFinder_id(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["finder_id"] = t

    finder_id = property(__getFinder_id, __setFinder_id)

    def __getFinder_name(self):    return self.__node.attrib["finder_name"]

    def __setFinder_name(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["finder_name"] = t

    finder_name = property(__getFinder_name, __setFinder_name)

    def __getEncoded(self):    return textToBool(self.__node.attrib["encoded"])

    def __setEncoded(self,b):
        assert type(b)==bool
        self.__node.attrib["encoded"] = boolToText(b)

    encoded = property(__getEncoded, __setEncoded)

    def __getText(self):    return self.__node.text

    def __setText(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.text = t

    text = property(__getText, __setText)

    def delete(self):
        self.__node.getparent().remove(self.__node)

class TravelBug(object):
    def __init__(self,n):
        assert n.tag == "travelbug"
        self.__node = n

    def __getRef(self):    return self.__node.attrib["ref"]
    ref = property(__getRef)

    def __getId(self):    return self.__node.attrib["id"]

    def __setId(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["id"] = t

    id = property(__getId, __setId)

    def __getName(self):    return self.__node.text

    def __setName(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["name"] = t

    name = property(__getName, __setName)

    def delete(self):
        self.__node.getparent().remove(self.__node)

class AddWaypoint(object):
    def __init__(self,n):
        assert n.tag =="add_wpt"
        self.__node = n

    def __getCode(self):    return self.__node.attrib["code"]

    def __setCode(self,t):
        assert type(t) == uniceode or type(t)==str
        self.__node.attrib["code"] = t

    code = property(__getCode, __setCode)

    def __getLat(self):    return float(self.__node.attrib["lat"])

    def __setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    lat = property(__getLat, __setLat)

    def __getLon(self):    return float(self.__node.attrib["lon"])

    def __setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    lon = property(__getLon, __setLon)

    def __getName(self):    return self.__node.attrib["name"]

    def __setName(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["name"] = t

    name = property(__getName, __setName)

    def __getUrl(self):    return self.__node.attrib["url"]

    def __setUrl(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["url"] = t

    url = property(__getUrl, __setUrl)

    def __getTime(self):    return textToDateTime(self.__node.attrib["time"])

    def __setTime(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["time"] = dateTimeToText(dt)

    time = property(__getTime, __setTime)

    def __getCmt(self):    return self.__node.text

    def __setCmt(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.text = t

    cmt = property(__getCmt, __setCmt)

    def __getSym(self):    return self.__node.attrib["sym"]

    def __setSym(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["sym"] = t

    sym = property(__getSym, __setSym)

    def delete(self):
        self.__node.getparent().remove(self.__node)

class Location(object):
    def __init__(self,n):
        assert n.tag =="location"
        self.__node = n

    def __getName(self):    return self.__node.attrib["name"]

    def __setName(self,t):
        assert type(t) == uniceode or type(t)==str
        self.__node.attrib["name"] = t

    name = property(__getName, __setName)

    def __getLat(self):    return float(self.__node.attrib["lat"])

    def __setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    lat = property(__getLat, __setLat)

    def __getLon(self):    return float(self.__node.attrib["lon"])

    def __setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    lon = property(__getLon, __setLon)

    def delete(self):
        self.__node.getparent().remove(self.__node)

class Geocacher:

    @staticmethod
    def getHomeDir(mkdir=None):
        '''
        Return the "Home dir" of the system (if it exists), or None
        (if mkdir is set : it will create a subFolder "mkdir" if the path exist,
        and will append to it (the newfolder can begins with a "." or not))
        '''
        maskDir=False
        try:
            #windows NT,2k,XP,etc. fallback
            home = os.environ['APPDATA']
            if not os.path.isdir(home): raise
            maskDir=False
        except:
            try:
                #all user-based OSes
                home = os.path.expanduser("~")
                if home == "~": raise
                if not os.path.isdir(home): raise
                maskDir=True
            except:
                try:
                    # freedesktop *nix ?
                    home = os.environ['XDG_CONFIG_HOME']
                    if not os.path.isdir(home): raise
                    maskDir=False
                except:
                    try:
                        #*nix fallback
                        home = os.environ['HOME']
                        if os.path.isdir(home):
                            conf = os.path.join(home,".config")
                            if os.path.isdir(conf):
                                home = conf
                                maskDir=False
                            else:
                                # keep home
                                maskDir=True
                        else:
                            raise
                    except:
                        #What os are people using?
                        home = None

        if home:
            if mkdir:
                if maskDir:
                    newDir = "."+mkdir
                else:
                    newDir = mkdir

                home = os.path.join(home,newDir)
                if not os.path.isdir(home):
                    os.mkdir(home)

            return home

    @staticmethod
    def getConfFile(name):
        '''Return the path to the configuration file named name'''
        if os.path.isfile(name):
            # the file exists in the local "./"
            # so we use it first
            return name
        else:
            # the file doesn't exist in the local "./"
            # it must exist in the "geocacher" config dir
            home = Geocacher.getHomeDir("geocacher")
            if home:
                # there is a "geocacher" config dir
                # the file must be present/created in this dir
                return os.path.join(home,name)
            else:
                # there is not a "geocacher" config dir
                # the file must be present/created in this local "./"
                return name

    @staticmethod
    def init(canModify=True):
        Geocacher.canModify = canModify
        # load/initalise the database
        Geocacher.db = DB( Geocacher.getConfFile("db.xml") )
        # load/initalise the program configuration
        # Set default values for configuration items
        d = {'common':{'mainWidth'  :700,
                       'mainHeight'  :500,
                       'mainSplit'  :400,
                       'cacheCols'  :['code','id','lat','lon','name','found',
                                      'type','size','distance','bearing'],
                       'sortCol'    :'code',
                       'userData1'  :'User Data 1',
                       'userData2'  :'User Data 2',
                       'userData3'  :'User Data 3',
                       'userData4'  :'User Data 4',
                       'miles'      :False,
                       'coordFmt'   :'hdd mm.mmm',
                       'CurrentLoc' :'Default',
                       'dispCache'  :''},
             'export':{'lastFolder' :Geocacher.getHomeDir(),
                       'lastFile'   :'',
                       'type'       :'simple',
                       'gc'         :False,
                       'logs'       :False,
                       'tbs'        :False,
                       'addWpts'    :False,
                       'sepAddWpts' :False,
                       'scope'      :'all'},
             'gps'   :{'type'       :'garmin',
                       'connection' :'usb:'},
             'filter':{'archived'   :False,
                       'disabled'   :False,
                       'found'      :False,
                       'mine'       :False},
             'load'  :{'lastFolder' :Geocacher.getHomeDir(),
                       'lastFile'   :'',
                       'mode'       :'update'},
             'gc'    :{'userName'  :'',
                       'userId'    :''}}
        Geocacher.conf = dict4ini.DictIni( Geocacher.getConfFile("geocacher.conf"), values=d)
