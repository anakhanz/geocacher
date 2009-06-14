# -*- coding: UTF-8 -*-

import datetime
from lxml.etree import Element,ElementTree
import os
import string

from libs import dict4ini
from libs.common import textToBool,boolToText,textToDateTime,dateTimeToText
from libs.common import getTextFromPath,getAttribFromPath

class DB:

    def __init__(self,file):
        """Load the DB or initalise if missing"""
        try:
            self.root = ElementTree(file=file).getroot()
            version = int(self.root.attrib["version"])
        except:
            self.root = Element("db",version="1")
            version=1
            self.addLocation('Default')
        self.file = file

    def save(self):
        """Save the DB"""
        fid = open(self.file,"w")
        fid.write("""<?xml version="1.0" encoding="utf-8"?>""")
        ElementTree(self.root).write(fid,encoding="utf-8")
        fid.close()

    def getCacheList(self):
        """Returns a list of caches"""
        cacheList = []
        for cacheNode in self.root.xpath(u"cache"):
            cacheList.append(Cache(cacheNode))
        return cacheList

    def getCacheCodeList(self):
        """Returns a list of cache codes"""
        cacheCodeList = []
        for cacheNode in self.root.xpath(u"cache"):
            cacheCodeList.append(cacheNode.attrib["code"])
        return cacheCodeList

    def getCacheByCode(self,code):
        """Returns the cache with the given code if found, otherwise 'None'"""
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
                        user_comments="",
                        user_flag=False,
                        user_data1="",
                        user_data2="",
                        user_data3="",
                        user_data4=""):
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
                            found_date = "%s" % dateTimeToText(found_date),
                            dnf        = boolToText(dnf),
                            dnf_date   = "%s" % dateTimeToText(dnf_date),
                            own_log    = own_log,
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
        self.root.append(newCache)
        return Cache(newCache)

    def getLocationList(self):
        """Returns a list of locations"""
        locationList = []
        for locationNode in self.root.xpath(u"location"):
            locationList.append(Location(locationNode))
        return cacheList

    def getLocationNameList(self):
        """Returns a list of cache locations"""
        locationCodeList = []
        for locationNode in self.root.xpath(u"location"):
            locationCodeList.append(locationNode.attrib["name"])
        return cacheCodeList

    def getLocationByName(self,name):
        """Returns the cache with the given code if found, otherwise 'None'"""
        locations = self.root.xpath(u"""location[@name="%s"]""" % name)
        if len(locations) > 0:
            return Location(locations[0])
        else:
            return None

    def addLocation(self,name,lat=0.0,lon=0.0,comment=""):
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
    id = property(__getId)

    def setId(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["id"] = t

    def __getLat(self):    return float(self.__node.attrib["lat"])
    lat = property(__getLat)

    def setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    def __getLon(self):    return float(self.__node.attrib["lon"])
    lon = property(__getLon)

    def setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    def __getName(self):    return self.__node.attrib["name"]
    name = property(__getName)

    def setName(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["name"] = t

    def __getUrl(self):    return self.__node.attrib["url"]
    url = property(__getUrl)

    def setUrl(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["url"] = t

    def __getLocked(self):    textToBool(self.__node.attrib["locked"])
    locked = property(__getLocked)

    def __getUser_date(self):    return textToDateTime(self.__node.attrib["user_date"])
    user_date = property(__getUser_date)

    def setUserDate(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["user_date"] = dateTimeToText(dt)

    def __getGpx_date(self):    return textToDateTime(self.__node.attrib["gpx_date"])
    gpx_date = property(__getGpx_date)

    def setGpx_date(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["gpx_date"] = dateTimeToText(dt)

    def __getSymbol(self):    return self.__node.attrib["symbol"]
    symbol = property(__getSymbol)

    def setSymbol(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["symbol"] = t

    def __getPlaced(self):
        return textToDateTime(self.__node.attrib["placed"])
    placed = property(__getPlaced)

    def setPlaced(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["placed"] = dateTimeToText(dt)

    def __getPlaced_by(self):    return self.__node.attrib["placed_by"]
    placed_by = property(__getPlaced_by)

    def setPlaced_by(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["placed_by"] = t

    def __getOwner(self):    return self.__node.attrib["owner"]
    owner = property(__getOwner)

    def setOwner(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["owner"] = t

    def __getOwner_id(self):    return self.__node.attrib["owner_id"]
    owner_id = property(__getOwner_id)

    def setOwner_id(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["owner_id"] = t

    def __getContainer(self):    return self.__node.attrib["container"]
    container = property(__getContainer)

    def setContainer(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO: add assertion that the container type is a valid one
        self.__node.attrib["container"] = t

    def __getDifficulty(self):    return float(self.__node.attrib["difficulty"])
    difficulty = property(__getDifficulty)

    def setDifficulty(self,f):
        assert type(f)==float
        assert f >= 0 and f <=5
        self.__node.attrib["difficulty"] = "%1.1f" % f

    def __getTerrain(self):    return float(self.__node.attrib["terrain"])
    terrain = property(__getTerrain)

    def setTerrain(self,f):
        assert type(f)==float
        assert f >= 0 and f <=5
        self.__node.attrib["terrain"] = "%1.1f" % f

    def __getType(self):    return self.__node.attrib["type"]
    type= property(__getType)

    def setType(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO: add assertion that the type is a valid one
        self.__node.attrib["type"] = t

    def __getAvailable(self):    textToBool(self.__node.attrib["available"])
    available = property(__getAvailable)

    def setAvailable(self,b):
        assert type(b) == bool
        self.__node.attrib["available"] = boolToText(b)

    def __getArchived(self):    textToBool(self.__node.attrib["archived"])
    archived = property(__getArchived)

    def setArchived(self,b):
        assert type(b) == bool
        self.__node.attrib["archived"] = boolToText(b)

    def __getState(self):    return self.__node.attrib["state"]
    state = property(__getState)

    def setState(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["state"] = t

    def __getCountry(self):    return self.__node.attrib["country"]
    country = property(__getCountry)

    def setCountry(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["country"] = t

    def __getShort_desc(self):
        return self.__node.xpath("short_description")[0].text
    short_desc = property(__getShort_desc)

    def setShort_desc(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("short_description")[0].text = t

    def __getShort_desc_html(self):
        return textToBool(self.__node.xpath("short_description")[0].attrib["html"])
    short_desc_html = property(__getShort_desc_html)

    def setShort_desc_html(self,b):
        assert type(b)==bool
        self.__node.xpath("short_description")[0].attrib["html"] = boolToText(b)

    def __getLong_desc(self):
        return self.__node.xpath("long_description")[0].text
    long_desc = property(__getLong_desc)

    def setLong_desc(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("long_description")[0].text = t

    def __getLong_desc_html(self):
        return textToBool(self.__node.xpath("long_description")[0].attrib["html"])
    long_desc_html = property(__getLong_desc_html)

    def setLong_desc_html(self,b):
        assert type(b)==bool
        self.__node.xpath("long_description")[0].attrib["html"] = boolToText(b)

    def __getEncoded_hints(self):
        return self.__node.xpath("encoded_hints")[0].text
    encoded_hints = property(__getEncoded_hints)

    def setEncoded_hints(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("encoded_hints")[0].text = t

    def __getFound(self):    textToBool(self.__node.attrib["found"])
    found = property(__getFound)

    def setFound(self,b):
        assert type(b) == bool
        self.__node.attrib["found"] = boolToText(b)

    def __getFound_date(self):
        return textToDateTime(self.__node.attrib["found_date"])
    found_date = property(__getFound_date)

    def setFound_date(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["found_date"] = dateTimeToText(dt)

    def __getDnf(self):    textToBool(self.__node.attrib["dnf"])
    dnf = property(__getDnf)

    def setDnf(self,b):
        assert type(b) == bool
        self.__node.attrib["dnf"] = boolToText(b)

    def __getDnf_date(self):
        return textToDateTime(self.__node.attrib["dnf_date"])
    dnf_date = property(__getDnf_date)

    def setDnf_date(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["dnf_date"] = dateTimeToText(dt)

    def __getOwn_log(self):
        return self.__node.xpath("own_log")[0].text
    own_log = property(__getOwn_log)

    def setOwn_log(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("own_log")[0].text = t

    def __getOwn_log_encoded(self):
        return textToBool(self.__node.xpath("own_log")[0].attrib["encoded"])
    own_log_encoded = property(__getOwn_log_encoded)

    def setOwn_log_encoded(self,b):
        assert type(b)==bool
        self.__node.xpath("own_log")[0].attrib["encoded"] = boolToText(b)

    def __getCorrected(self):    textToBool(self.__node.attrib["corrected"])
    corrected = property(__getCorrected)

    def setCorrected(self,b):
        assert type(b) == bool
        self.__node.attrib["corrected"] = boolToText(b)

    def __getCLat(self):    return float(self.__node.attrib["clat"])
    clat = property(__getCLat)

    def setCLat(self,f):
        assert type(f) == float
        self.__node.attrib["clat"] = "%f" % f

    def __getCLon(self):    return float(self.__node.attrib["clon"])
    clon = property(__getCLon)

    def setCLon(self,f):
        assert type(f) == float
        self.__node.attrib["clon"] = "%f" % f

    def __getCNote(self):    return self.__node.attrib["cnote"]
    cnote = property(__getCNote)

    def setCNote(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["cnote"] = t

    def __getSource(self):    return self.__node.attrib["source"]
    source = property(__getSource)

    def setSource(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["source"] = t

    def __getUser_comments(self):
        return self.__node.xpath("user_comments")[0].text
    user_comments = property(__getUser_comments)

    def setUser_comments(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.xpath("user_comments")[0].text = t

    def __getUser_flag(self):    textToBool(self.__node.attrib["user_flag"])
    user_flag = property(__getUser_flag)

    def setUser_flag(self,b):
        assert type(b) == bool
        self.__node.attrib["user_flag"] = boolToText(b)

    def __getUser_data1(self):    return self.__node.attrib["user_data1"]
    user_data1 = property(__getUser_data1)

    def setUser_data1(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data1"] = t

    def __getUser_data2(self):    return self.__node.attrib["user_data2"]
    user_data2 = property(__getUser_data2)

    def setUser_data2(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data2"] = t

    def __getUser_data3(self):    return self.__node.attrib["user_data3"]
    user_data3 = property(__getUser_data3)

    def setUser_data3(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data3"] = t

    def __getUser_data4(self):    return self.__node.attrib["user_data4"]
    user_data4 = property(__getUser_data4)

    def setUser_data4(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["user_data4"] = t

    def getLogs(self):
        logNodes = self.__node.xpath("log")
        logs=[]
        for logNode in logNodes:
            logs.append(Log(logNode))
        return logs

    def getLogIdList(self):
        logNodes = self.__node.xpath("log")
        logIds=[]
        for logNode in logNodes:
            logIds.append(logNode.attrib["id"])
        return logIds

    def getLogById(self,id):
        """Returns the log with the given id if found, otherwise 'None'"""
        assert type(id)==unicode or type(id)==str
        logs = self.__node.xpath(u"""log[@id="%s"]""" % id)
        if len(logs) > 0:
            return Log(logs[0])
        else:
            return None

    def addLog(self,id,date=None,type=u"",finder_id=u"",finder_name=u"",encoded=False,text=u""):
        if date == None:
            dateText = u""
        else:
            dateText = dateTimeToText(date)
        log = Element("log",id=id,date=dateText,type=type,finder_id=finder_id,
        finder_name=finder_name,encoded=boolToText(encoded))
        log.text = text
        self.__node.append(log)
        return Log(log)

    def getTravelBugs(self):
        bugNodes = self.__node.xpath("travelbug")
        bugs=[]
        for bugNode in bugNodes:
            bugs.append(TravelBug(bugNode))
        return bugs

    def getTravelBugRefs(self):
        bugNodes = self.__node.xpath("travelbug")
        bugRefs=[]
        for bugNode in bugNodes:
            bugRefs.append(TravelBug(bugNode).ref)
        return bugRefs

    def getTravelBugByRef(self,ref):
        """Returns the travel bug with the given ref if found, otherwise 'None'"""
        assert type(ref)==unicode or type(ref)==str
        bugs = self.__node.xpath(u"""travelbug[@ref="%s"]""" % ref)
        if len(bugs) > 0:
            return TravelBug(bugs[0])
        else:
            return None

    def addTravelBug(self,ref,id=u"",name=u""):
        travelbug = Element("travelbug",ref=ref,id=id)
        travelbug.text = name
        self.__node.append(travelbug)
        return TravelBug(travelbug)

    def getAddWaypoints(self):
        addWptNodes = self.__node.xpath("add_wpt")
        addWpts=[]
        for addWptNode in addWptNodes:
            addWpts.append(AddWaypoint(addWptNode))
        return addWpts

    def getAddWaypointCodes(self):
        addWptNodes = self.__node.xpath("add_wpt")
        addWptCodes=[]
        for addWptNode in addWptNodes:
            addWptCodes.append(AddWaypoint(addWptNode).code)
        return addWptCodes

    def getAddWaypointByCode(self,code):
        """Returns the additional waypoint with the given code if found, otherwise 'None'"""
        assert type(code)==unicode or type(code)==str
        addWpts = self.__node.xpath(u"""add_wpt[@code="%s"]""" % code)
        if len(addWpts) > 0:
            return AddWaypoint(addWpts[0])
        else:
            return None


    def addAddWaypoint(self,code,lat=0,lon=0,name=u"",url="",time=None,cmt=u"",sym=u""):
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
    date = property(__getDate)

    def setDate(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["date"] = dateTimeToText(dt)

    def __getType(self):    return self.__node.attrib["type"]
    type = property(__getType)

    def setType(self,t):
        assert type(t)==unicode or type(t)==str
        # TODO add assertion that the type is valid
        self.__node.attrib["type"] = t

    def __getFinder_id(self):    return self.__node.attrib["finder_id"]
    finder_id = property(__getFinder_id)

    def setFinder_id(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["finder_id"] = t

    def __getFinder_name(self):    return self.__node.attrib["finder_name"]
    finder_name = property(__getFinder_name)

    def setFinder_name(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["finder_name"] = t

    def setEncoded(self,b):
        assert type(b)==bool
        self.__node.attrib["encoded"] = boolToText(b)

    def __getEncoded(self):    return textToBool(self.__node.attrib["encoded"])
    encoded = property(__getEncoded)

    def __getText(self):    return self.__node.text
    text = property(__getText)

    def setText(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.text = t

    def delete(self):
        self.__node.getparent().remove(self.__node)

class TravelBug(object):
    def __init__(self,n):
        assert n.tag == "travelbug"
        self.__node = n

    def __getRef(self):    return self.__node.attrib["ref"]
    ref = property(__getRef)

    def __getId(self):    return self.__node.attrib["id"]
    id = property(__getId)

    def setId(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["id"] = t

    def __getName(self):    return self.__node.text
    name = property(__getName)

    def setName(self,t):
        assert type(t)==unicode or type(t)==str
        self.__node.attrib["name"] = t

    def delete(self):
        self.__node.getparent().remove(self.__node)

class AddWaypoint(object):
    def __init__(self,n):
        assert n.tag =="add_wpt"
        self.__node = n

    def __getCode(self):    return self.__node.attrib["code"]
    code = property(__getCode)

    def setCode(self,t):
        assert type(t) == uniceode or type(t)==str
        self.__node.attrib["code"] = t

    def __getLat(self):    return float(self.__node.attrib["lat"])
    lat = property(__getLat)

    def setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    def __getLon(self):    return float(self.__node.attrib["lon"])
    lon = property(__getLon)

    def setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    def __getName(self):    return self.__node.attrib["name"]
    name = property(__getName)

    def setName(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["name"] = t

    def __getUrl(self):    return self.__node.attrib["url"]
    url = property(__getUrl)

    def setUrl(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["url"] = t

    def __getTime(self):    return textToDateTime(self.__node.attrib["time"])
    time = property(__getTime)

    def setTime(self,dt):
        assert type(dt)==datetime.datetime
        self.__node.attrib["time"] = dateTimeToText(dt)

    def __getCmt(self):    return self.__node.text
    cmt = property(__getCmt)

    def setCmt(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.text = t

    def __getSym(self):    return self.__node.attrib["sym"]
    sym = property(__getSym)

    def setSym(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.attrib["sym"] = t

    def delete(self):
        self.__node.getparent().remove(self.__node)

class Location(object):
    def __init__(self,n):
        assert n.tag =="location"
        self.__node = n

    def __getName(self):    return self.__node.attrib["name"]
    name = property(__getName)

    def setName(self,t):
        assert type(t) == uniceode or type(t)==str
        self.__node.attrib["name"] = t

    def __getLat(self):    return float(self.__node.attrib["lat"])
    lat = property(__getLat)

    def setLat(self,f):
        assert type(f) == float
        self.__node.attrib["lat"] = "%f" % f

    def __getLon(self):    return float(self.__node.attrib["lon"])
    lon = property(__getLon)

    def setLon(self,f):
        assert type(f) == float
        self.__node.attrib["lon"] = "%f" % f

    def __getCmt(self):    return self.__node.txt
    cmt = property(__getCmt)

    def setCmt(self,t):
        assert type(t) == unicode or type(t)==str
        self.__node.text = t

    def delete(self):
        self.__node.getparent().remove(self.__node)

class Geocacher:
    __lockFile = "geocacher.lock"

    @staticmethod
    def lockOn():
        """ create the lock file and return True if it can"""
        file = os.path.join(Geocacher.getHomeDir("geocacher"),Geocacher.__lockFile)
        if os.path.isfile(file):
            print file
            return False
        else:
            open(file,"w").write("")
            return True

    @staticmethod
    def lockOff():
        """ Delete the lockfile """
        file = os.path.join(Geocacher.getHomeDir("geocacher"),Geocacher.__lockFile)
        if os.path.isfile(file):
            os.unlink(file)

    @staticmethod
    def getHomeDir(mkdir=None):
        """
        Return the "Home dir" of the system (if it exists), or None
        (if mkdir is set : it will create a subFolder "mkdir" if the path exist,
        and will append to it (the newfolder can begins with a "." or not))
        """
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
        if os.path.isfile(name):
            # the file exists in the local "./"
            # so we use it first
            return name
        else:
            # the file doesn't exist in the local "./"
            # it must exist in the "jbrout" config dir
            home = Geocacher.getHomeDir("geocacher")
            if home:
                # there is a "jbrout" config dir
                # the file must be present/created in this dir
                return os.path.join(home,name)
            else:
                # there is not a "jbrout" config dir
                # the file must be present/created in this local "./"
                return name

    @staticmethod
    def init(debug=0, canModify=True):
        Geocacher.debugLevel = debug
        Geocacher.canModify = canModify
        # load/initalise the database
        Geocacher.db = DB( Geocacher.getConfFile("db.xml") )
        # load/initalise the program configuration
        d = {'common':{'mainWidth'  :700,
                       'mainHeigt'  :500,
                       'cacheCols'  :['code','id','lat','lon','name','found',
                                      'type','size','distance','bearing'],
                       'sortCol'    :'code',
                       'userData1'  :'User Data 1',
                       'userData2'  :'User Data 2',
                       'userData3'  :'User Data 3',
                       'userData4'  :'User Data 4',
                       'miles'      :False,
                       'CurrentLoc' :'Default'},
             'export':{'lastFolder' :Geocacher.getHomeDir(),
                       'lastFile'   :''},
             'load'  :{'lastFolder' :Geocacher.getHomeDir(),
                       'lastFile'   :''},
             'gc'    :{'userName'  :'',
                       'userId'    :''}}
        Geocacher.conf = dict4ini.DictIni( Geocacher.getConfFile("geocacher.conf"), values=d)

    @staticmethod
    def dbgPrint(message, level=1):
        if level == 0:
           print "Warning!   %s" % message
        else:
            if level <= Geocacher.debugLevel:
                print "Debug L%i: %s" % (level, message)
