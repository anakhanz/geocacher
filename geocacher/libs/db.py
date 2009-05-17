# -*- coding: UTF-8 -*-

from lxml.etree import Element,ElementTree
import os
import string

from libs import dict4ini
from xml.utils import iso8601

class DB:

    def __init__(self,file):
        """Load the DB or initalise if missing"""
        try:
            self.root = ElementTree(file=file).getroot()
        except:
            self.root = Element("db")
        self.file = file

    def save(self):
        """Save the DB"""
        fid = open(self.file,"w")
        fid.write("""<?xml version="1.0" encoding="UTF-8"?>""")
        ElementTree(self.root).write(fid,encoding="utf-8")
        fid.close()

    def addCache(self, code,lat,lon,desc):
        node = self.root
        Geocacher.dbgPrint("Adding %s" % code,3)
        try:
            cache = self.root.xpath(u"""cache[@code="%s"]""" % name)[0]
            Geocacher.dbgPrint("%s Found, updating" % code,3)
            cache.attrib["lat"] = lat
            cache.attrib["lon"] = lon
        except:
            Geocacher.dbgPrint("%s Not Found, adding" % code,3)
            cache = Element("cache", code=code, lat=lat, lon=lon)
            self.root.append(cache)
        if len(desc) != 0:
            cache.attrib["desc"] = desc

    def getCacheList(self):
        cacheList = []
        for cacheNode in self.root.xpath(u"cache"):
            cacheList.append([cacheNode.attrib["code"],
                              cacheNode.attrib["lat"],
                              cacheNode.attrib["lon"]])
        return cacheList

    def loadGpx(self,filename,mode="update"):
        NS = {'gpx': "http://www.topografix.com/GPX/1/0",
              'gs': "http://www.groundspeak.com/cache/1/0"}

        # Load GPX file
        if os.path.isfile(filename):
            gpxDoc = ElementTree(file=filename).getroot()
        else:
            return
        # Get the date the GPX file was created
        try:
            gpxDate = iso8601.parse(gpxDoc.xpath("//gpx:gpx//gpx:time", namespaces=NS)[0].text)
            Geocacher.dbgPrint("GPX time is: " + iso8601.tostring(gpxDate), 3)
        except:
            gpxDate = os.path.getmtime(filename)
            Geocacher.dbgPrint("No time in GPX file, using current time",1)

        # Find the waypoints and process them
        for wpt in gpxDoc.xpath("//gpx:gpx//gpx:wpt", namespaces=NS):
            code = self.getTextFromPath(wpt,"gpx:name",NS)
            Geocacher.dbgPrint("Adding %s" % code,3)
            try:
                cache = self.root.xpath(u"""cache[@code="%s"]""" % code)[0]
                Geocacher.dbgPrint("%s Found, updating" % code,3)
                updated = False
                new = False
            except:
                Geocacher.dbgPrint("%s Not Found, adding" % code,3)
                cache = Element("cache", code=code, gpx_date=iso8601.tostring(gpxDate), locked='False')
                self.root.append(cache)
                updated = True
                new = True

            if (updated or
               (iso8601.parse(cache.attrib["gpx_date"]) <= gpxDate and
                    mode == "update") or
                    mode=="replace"):
                Geocacher.dbgPrint("Update of allowed",3)
                updated |= self.copyAttrib(cache,"lat",wpt,"lat")
                updated |= self.copyAttrib(cache,"lon",wpt,"lon")
                updated |= self.updateAttrib(cache, "id", self.getAttribFromPath(wpt,"gs:cache","id",NS))
                updated |= self.updateAttrib(cache, "available", self.getAttribFromPath(wpt,"gs:cache","available",NS,'True'))
                updated |= self.updateAttrib(cache, "archived", self.getAttribFromPath(wpt,"gs:cache","archived",NS,'False'))
                updated |= self.updateAttrib(cache, "name", self.getTextFromPath(wpt,"gpx:urlname",NS))
                updated |= self.updateAttrib(cache, "url", self.getTextFromPath(wpt,"gpx:url",NS))
                updated |= self.updateAttrib(cache, "symbol", self.getTextFromPath(wpt,"gpx:sym",NS))
                updated |= self.updateAttrib(cache, "placed", self.getTextFromPath(wpt,"gpx:time",NS))
                updated |= self.updateAttrib(cache, "placed_by", self.getTextFromPath(wpt,"gs:cache//gs:placed_by",NS))
                updated |= self.updateAttrib(cache, "owner", self.getTextFromPath(wpt,"gs:cache//gs:owner",NS))
                updated |= self.updateAttrib(cache, "owner_id", self.getAttribFromPath(wpt,"gs:cache//gs:owner","id",NS))
                updated |= self.updateAttrib(cache, "type", self.getTextFromPath(wpt,"gs:cache//gs:type",NS))
                updated |= self.updateAttrib(cache, "container", self.getTextFromPath(wpt,"gs:cache//gs:container",NS,"Not Specified"))
                updated |= self.updateAttrib(cache, "difficulty", self.getTextFromPath(wpt,"gs:cache//gs:difficulty",NS,"1"))
                updated |= self.updateAttrib(cache, "terrain", self.getTextFromPath(wpt,"gs:cache//gs:terrain",NS,"1"))
                updated |= self.updateAttrib(cache, "state", self.getTextFromPath(wpt,"gs:cache//gs:state",NS))
                updated |= self.updateAttrib(cache, "country", self.getTextFromPath(wpt,"gs:cache//gs:country",NS))
                (changed,tag) = self.updateNodeText(cache, "short_description",self.getTextFromPath(wpt,"gs:cache//gs:short_description",NS))
                updated |= changed
                updated |= self.updateAttrib(tag, "html", self.getAttribFromPath(wpt,"gs:cache//gs:short_description","html",NS,'False'))
                (changed,tag) = self.updateNodeText(cache, "long_description",self.getTextFromPath(wpt,"gs:cache//gs:long_description",NS))
                updated |= changed
                updated |= self.updateAttrib(tag, "html", self.getAttribFromPath(wpt,"gs:cache//gs:long_description","html",NS,'False'))
                (changed,tag) = self.updateNodeText(cache, "encoded_hints",self.getTextFromPath(wpt,"gs:cache//gs:encoded_hints",NS))
                updated |= changed
                # TODO: Travel Bugs see "Headlights"
                # TODO: Extra waypoints
                # TODO: Logs
                # TODO: mark if found
            if updated:
                self.updateAttrib(cache, "gpx_date", iso8601.tostring(gpxDate))
                self.updateAttrib(cache, "source", os.path.abspath(filename))

    ##            # Deal with the log
    ##            for log in cachedetail.xpath('gs:logs//gs:log', namespaces=NS):
    ##                logFinder = log.xpath('gs:finder', namespaces=NS)[0]
    ##                if logFinder.attrib["id"]==userid or logFinder.text == username:
    ##                    print "matches"


    def loadLoc(self,filename,mode="update"):
        # Load LOC file
        if os.path.isfile(filename):
            locDoc = ElementTree(file=filename).getroot()
        else:
            return

        # Get the file modification time
        locDate = os.path.getmtime(filename)
        # Find the waypoints and process them
        for wpt in locDoc.xpath("//loc//waypoint"):
            code = self.getAttribFromPath(wpt,"name","id")
            Geocacher.dbgPrint("Adding %s" % code,3)
            try:
                cache = self.root.xpath(u"""cache[@code="%s"]""" % code)[0]
                Geocacher.dbgPrint("%s Found, updating" % code,3)
                updated = False
                new = False
            except:
                Geocacher.dbgPrint("%s Not Found, adding" % code,3)
                cache = Element("cache", code=code, gpx_date=iso8601.tostring(locDate))
                self.root.append(cache)
                updated = True
                new = True
            if (updated or
               (iso8601.parse(cache.attrib["gpx_date"]) <= locDate and
                    mode == "update") or
                    mode=="replace"):
                Geocacher.dbgPrint("Update of allowed",3)
                updated |= self.updateAttrib(cache, "lat", self.getAttribFromPath(wpt,"coord","lat"))
                updated |= self.updateAttrib(cache, "lon", self.getAttribFromPath(wpt,"coord","lon"))
                info = string.split(self.getTextFromPath(wpt,"name"), " by ")
                updated |= self.updateAttrib(cache, "name", info[0])
                if len(info)==2:
                    updated |= self.updateAttrib(cache, "placed_by", info[1])
                elif len(info)==3:
                    updated |= self.updateAttrib(cache, "placed_by", info[1]+" by "+info[2])
                url = self.getTextFromPath(wpt,"link")
                # Take care of extra "</link>" tag in the url if it is there
                if url[-7:] == "</link>":
                    url = url[:-7]
                updated |= self.updateAttrib(cache, "url", url)
            if updated:
                self.updateAttrib(cache, "gpx_date", iso8601.tostring(locDate))
                self.updateAttrib(cache, "source", os.path.abspath(filename))

    def getTextFromPath(self, root, relativePath, nameSpaces=None, default=None):
        if nameSpaces==None:
            print "None"
            try:
                ret = root.xpath(relativePath)[0].text
                Geocacher.dbgPrint("'%s' found at path '%s'" % (ret,relativePath),3)
            except:
                ret = default
                Geocacher.dbgPrint("'%s' path not found" % relativePath,3)
        else:
            try:
                ret = root.xpath(relativePath, namespaces=nameSpaces)[0].text
                Geocacher.dbgPrint("'%s' found at path '%s'" % (ret,relativePath),3)
            except:
                ret = default
                Geocacher.dbgPrint("'%s' path not found" % relativePath,3)
        return ret

    def getAttrib(felf, root, attrib, default=None):
        try:
            ret = root.attrib[attrib]
            Geocacher.dbgPrint("'%s' found at attribute '%s'" % (ret,attrib),3)
        except:
            ret = default
            Geocacher.dbgPrint("attribute '%s' not found" % attrib,3)
        return ret

    def getAttribFromPath(self, root, relativePath, attrib, nameSpaces=None, default=None):
        if nameSpaces==None:
            try:
                ret = root.xpath(relativePath)[0].attrib[attrib]
                Geocacher.dbgPrint("'%s' found at attribute '%s' path '%s'" % (ret,attrib,relativePath),3)
            except:
                ret = default
                Geocacher.dbgPrint("attribute '%s' not found at path '%s'" % (attrib,relativePath),3)
        else:
            try:
                ret = root.xpath(relativePath, namespaces=nameSpaces)[0].attrib[attrib]
                Geocacher.dbgPrint("'%s' found at attribute %s path '%s'" % (ret,attrib,relativePath),3)
            except:
                ret = default
                Geocacher.dbgPrint("attribute '%s' not found at path '%s'" % (attrib,relativePath),3)
        return ret

    def copyAttrib(self, destPath, destAttrib, srcPath, srcAttrib, default=None):
        try:
            srcValue = srcPath.attrib[srcAttrib]
        except:
            srcValue=None
        return self.updateAttrib(destPath, destAttrib, srcValue)

    def updateAttrib(self, destPath, destAttrib, newValue):
        try:
            destValue = destPath.attrib[destAttrib]
        except:
            destValue=None
        if destValue == newValue or newValue==None:
            return False
        else:
            destPath.attrib[destAttrib] = newValue
            return True

    def updateNodeText(self,root, destPath, newValue, nameSpaces=None):
        if newValue == None:
            Geocacher.dbgPrint("'None' value suppplied to update node text using blank",3)
            newValue=""
        if nameSpaces == None:
            destNodes = root.xpath(destPath)
        else:
            destNodes = root.xpath(destPath,namespaces=nameSpaces)
        if len(destNodes) > 0:
            Geocacher.dbgPrint("node '%s' found updating" % destPath,3)
            destNode = destNode[0]
        else:
            Geocacher.dbgPrint("node '%s' found creating" % destPath,3)
            if nameSpaces == None:
                destNode = Element("destTag")
            else:
                destNode = Element("destTag",namespaces=nameSpaces)
            root.append(destNode)
        if destNode.text == newValue:
            return (False,destNode)
        else:
            destNode.text = newValue
            return (True,destNode)

class Geocacher:
    __lockFile = "geocacher.lock"

    @staticmethod
    def lockOn():
        """ create the lock file, return True if it can"""
        file = os.path.join(Geocacher.getHomeDir("geocacher"),Geocacher.__lockFile)
        if os.path.isfile(file):
            print file
            return False
        else:
            open(file,"w").write("")
            return True

    @staticmethod
    def lockOff():
        """ delete the lockfile """
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
        d = {'common':{'mainWidth' :700,
                       'mainHeigt' :500,
                       'lastFolder':Geocacher.getHomeDir()},
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