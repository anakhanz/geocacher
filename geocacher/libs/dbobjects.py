# -*- coding: UTF-8 -*-

import os.path
import sys
import sqlite3

import geocacher
from geocacher.libs.common import rows2list

minint = 0-sys.maxint

CACHE_CONTAINERS = ['Micro',
                    'Small',
                    'Regular',
                    'Large',
                    'Not chosen',
                    'Virtual',
                    'Other']

CACHE_TYPES = ['Traditional Cache',
               'Ape',
               'CITO',
               'Earthcache',
               'Event Cache',
               'Maze',
               'Letterbox Hybrid',
               'Mega',
               'Multi-cache',
               'Unknown Cache',
               'Reverse',
               'Virtual Cache',
               'Webcam Cache',
               'Wherigo Cache',
               'Lost and Found Event Cache']

LOG_TYPES = ["Found it",
             "Didn't find it",
             "Other",
             "Needs Archived",
             "Unknown",
             "Archive (show)",
             "Archive (no show)",
             "Attended"]

ATTRIBUTES = ["Unknown",#0
              "Dogs",#1
              "Access or parking fee",#2
              "Climbing gear",#3
              "Boat",#4
              "Scuba Gear",#5
              "Recommended for kids",#6
              "Takes less than an hour",#7
              "Scenic View",#8
              "Significant Hike",#9
              "Difficult Climbing",#10
              "May require wading",#11
              "May require Swimming",#12
              "Available at all times",#13
              "Recommended at night",#14
              "Available during winter",#15
              "",#16
              "Poison plants",#17
              "Dangerous Animals",#18
              "Ticks",#19
              "Abandoned mines",#20
              "Cliff / falling rocks",#21
              "Hunting",#22
              "Dangerous area",#23
              "Wheelchair accessible",#24
              "Parking available",#25
              "Public transportation",#26
              "Drinking water nearby",#27
              "Public restrooms nearby",#28
              "Telephone nearby",#29
              "Picnic tables nearby",#30
              "Camping available",#31
              "Bicycles",#32
              "Motorcycles",#33
              "Quads",#34
              "Off-road vehicles",#35
              "Snowmobiles",#36
              "Horses",#37
              "Campfires",#38
              "Thorns",#39
              "Stealth required",#40
              "Stroller accessible",#41
              "Needs maintenance",#42
              "Watch for livestock",#43
              "Flashlight required",#44
              "",#45
              "Truck Driver/RV",#46
              "Field Puzzle",#47
              "UV Light Required",#48
              "May Require Snowshoes",#49
              "May Require Skiis",#50
              "Special Tool Required",#51
              "Night Cache",#52
              "Park and Grab",#53
              "Abandoned Structure",#54
              "Short hike (less than 1km)",#55
              "Medium hike (1km-10km)",#56
              "Long Hike (+10km)",#57
              "Fuel Nearby",#58
              "Food Nearby",#59
              "Wireless Beacon Required",#60
              ]

ATTRIB_ICO = ["Unknown",#0
              "dogs",#1
              "fee",#2
              "rappelling",#3
              "boat",#4
              "scuba",#5
              "kids",#6
              "onehour",#7
              "scenic",#8
              "hiking",#9
              "climbing",#10
              "wading",#11
              "swimming",#12
              "available",#13
              "night",#14
              "winter",#15
              "",#16
              "poisonoak",#17
              "snakes",#18
              "ticks",#19
              "mine",#20
              "cliff",#21
              "hunting",#22
              "danger",#23
              "wheelchair",#24
              "parking",#25
              "public",#26
              "water",#27
              "restrooms",#28
              "phone",#29
              "picnic",#30
              "camping",#31
              "bicycles",#32
              "motorcycles",#33
              "quads",#34
              "jeeps",#35
              "snowmobiles",#36
              "horses",#37
              "campfires",#38
              "thorn",#39
              "stealth",#40
              "stroller",#41
              "firstaid",#42
              "cow",#43
              "flashlight",#44
              "",#45
              "rv",#46
              "field_puzzle",#47
              "UV",#48
              "snowshoes",#49
              "skiis",#50
              "s-tool",#51
              "night",#52
              "parkngrab",#53
              "AbandonedBuilding",#54
              "hike_short",#55
              "hike_med",#56
              "hike_long",#57
              "fuel",#58
              "food",#59
              "wirelessbeacon",#60
              ]

class Cache(object):
    def __init__(self, cid=minint):
        cur=geocacher.db().cursor()
        if cid < 0:
            cur.execute('select id from caches where id=?', (cid, ))
            if cur.fetchone() is None:
                cur.execute('select min(id) from caches')
                row = cur.fetchone()
                if row[0] is None:
                    cid = -1
                else:
                    cid = min(row[0]-1, -1)
        cur.execute('select id from caches where id=?', (cid, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Caches(id, code) VALUES(?, '')", (cid,))
        cur.execute("SELECT id, code, lat, lon, name, url, locked, user_date, gpx_date, placed,placed_by, owner, owner_id, container, difficulty, terrain, type, available, archived, state, country, short_desc, short_desc_html, long_desc, long_desc_html, encoded_hints, ftf, found, found_date, dnf, dnf_date, own_log_id, source, corrected, clat, clon, cnote, user_comments, user_flag, user_data1, user_data2, user_data3, user_data4 FROM Caches WHERE id=?", (cid,))
        row = cur.fetchone()
        if type(row) is not sqlite3.dbapi2.Row:
            raise geocacher.InvalidID("Invalid Cache ID: %s" % str(cid))
        self.id              = row[ 0]
        self.code            = row[ 1]
        self.lat             = row[ 2]
        self.lon             = row[ 3]
        self.name            = row[ 4]
        self.url             = row[ 5]
        self.locked          = row[ 6]
        self.user_date       = row[ 7]
        self.gpx_date        = row[ 8]
        self.placed          = row[ 9]
        self.placed_by       = row[10]
        self.owner           = row[11]
        self.owner_id        = row[12]
        self.container       = row[13]
        self.difficulty      = row[14]
        self.terrain         = row[15]
        self.type            = row[16]
        self.available       = row[17]
        self.archived        = row[18]
        self.state           = row[19]
        self.country         = row[20]
        self.short_desc      = row[21]
        self.short_desc_html = row[22]
        self.long_desc       = row[23]
        self.long_desc_html  = row[24]
        self.encoded_hints   = row[25]
        self.ftf             = row[26]
        self.found           = row[27]
        self.found_date      = row[28]
        self.dnf             = row[29]
        self.dnf_date        = row[30]
        self.own_log_id      = row[31]
        self.source          = row[32]
        self.corrected       = row[33]
        self.clat            = row[34]
        self.clon            = row[35]
        self.cnote           = row[36]
        self.user_comments   = row[37]
        self.user_flag       = row[38]
        self.user_data1      = row[39]
        self.user_data2      = row[40]
        self.user_data3      = row[41]
        self.user_data4      = row[42]

        self.refreshOwnLog()

    def __getCurrentLat(self):
        if self.corrected:
            return self.clat
        else:
            return self.lat

    def __getCurrentLon(self):
        if self.corrected:
            return self.clon
        else:
            return self.lon

    def __getSymbol(self):
        if self.found:
            return 'Geocache Found'
        else:
            return 'Geocache'

    currentLat = property(__getCurrentLat)
    currentLon = property(__getCurrentLon)
    symbol = property(__getSymbol)

    def refreshOwnLog(self):
        self.own_log = ""
        self.own_log_encoded = False
        if self.own_log_id not in [0, None]:
            cur = geocacher.db().cursor()
            cur.execute("SELECT encoded, text FROM Logs WHERE id=?",(self.own_log_id,))
            row = cur.fetchone()
            if type(row) is not sqlite3.dbapi2.Row:
                raise geocacher.InvalidID("Invalid Log ID: %s" % str(self.own_log_id))
            self.own_log_encoded = (row[0] == 1)
            self.own_log         = row[1]

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Caches WHERE id=?", (self.id,))
        cur.execute("INSERT INTO Caches(id, code, lat, lon, name, url, locked, user_date, gpx_date, placed, placed_by, owner, owner_id, container, difficulty, terrain, type, available, archived, state, country, short_desc, short_desc_html, long_desc, long_desc_html, encoded_hints, ftf, found, found_date, dnf, dnf_date, own_log_id, source, corrected, clat, clon, cnote, user_comments, user_flag, user_data1, user_data2, user_data3, user_data4) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.id, self.code, self.lat, self.lon, self.name, self.url, self.locked, self.user_date,self.gpx_date, self.placed, self.placed_by, self.owner, self.owner_id, self.container, self.difficulty, self.terrain, self.type, self.available, self.archived, self.state, self.country, self.short_desc, self.short_desc_html, self.long_desc, self.long_desc_html, self.encoded_hints, self.ftf, self.found, self.found_date, self.dnf, self.dnf_date, self.own_log_id, self.source, self.corrected, self.clat, self.clon, self.cnote, self.user_comments, self.user_flag, self.user_data1, self.user_data2, self.user_data3 , self.user_data4,))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Caches WHERE id=?", (self.id,))
        cur.execute("DELETE FROM Attributes WHERE cache_id=?", (self.id,))
        cur.execute("DELETE FROM Logs WHERE cache_id=?", (self.id,))
        cur.execute("DELETE FROM Travelbugs WHERE cache_id=?", (self.id,))
        cur.execute("DELETE FROM Waypoints WHERE cache_id=?", (self.id,))

    def getLogs(self, sort=True, descending=True, maxLen=None):
        '''
        Returns the logs associated with the cache

        Keyword arguments
        sort       Enable sorting of the log list by date
        descending Sort with the most recent log first
        maxLen     Truncate the list at this position
        '''

        logs=[]
        for row in self.getLogIdList(sort, descending, maxLen):
            logs.append(Log(row))
        return logs

    def getLogIdList(self, sort=True, descending=True, maxLen=None):
        '''
        Returns a list of the ID's of the logs associated with the cache

        Keyword arguments
        sort       Enable sorting of the log list by date
        descending Sort with the most recent log first
        maxLen     Truncate the list at this position
        '''
        cur = geocacher.db().cursor()
        sql = "SELECT id FROM Logs WHERE cache_id = ?"
        if sort:
            sql = sql + " ORDER BY log_date"
        if descending:
            sql = sql + " DESC"
        cur.execute(sql , (self.id,))
        rows = cur.fetchall()
        if maxLen is not None:
            if descending:
                rows = rows[:maxLen]
            else:
                rows = rows[-maxLen:]
        return rows2list(rows)

    def getNumLogs(self):
        '''Returns the number of logs in the DB for the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Logs WHERE cache_id = ?", (self.id,))
        return len(cur.fetchall())

    def getLogById(self,id):
        '''Returns the log with the given id if found, otherwise "None"'''
        assert type(id)==int
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Logs WHERE cache_id = ? AND id = ?", (self.id, id,))
        if cur.fetchone() is None:
            return None
        else:
            return Log(id)

    def getLogDates(self):
        '''
        Returns a sorted list of the dates on which the cache has been logged
        with the most recent first
        '''
        cur = geocacher.db().cursor()
        cur.execute("SELECT date FROM Logs WHERE cache_id = ? ORDER BY date DESC", (self.id,))
        return rows2list(cur.fetchall())

    def getLastLogDate(self):
        '''Returns the date of the last log or None if no logs'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT MAX(date) FROM Logs WHERE cache_id = ?", (self.id,))
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def getFoundDates(self):
        '''
        Returns a sorted list of the dates on which the cache has been found
        with the most recent first
        '''
        cur = geocacher.db().cursor()
        cur.execute("SELECT date FROM Logs WHERE cache_id = ? AND type=? ORDER BY date DESC", (self.id,'Found it',))
        dates = []
        for row in cur.fetchall():
            dates.append(datetime.fromtimestamp(row[0]))
        return dates

    def getLastFound(self):
        '''Returns the date on which the cache was found or None if never Found'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT date FROM Logs WHERE cache_id = ? AND type=? ORDER BY date DESC", (self.id,'Found it',))
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def getFoundCount(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT date FROM Logs WHERE cache_id = ? AND type=? ORDER BY date DESC", (self.id,'Found it',))
        return len(cur.fetchall())

    def addLog(self,logId,
                    date        = None,
                    logType     = u"",
                    finder_id   = u"",
                    finder_name = u"",
                    encoded     = False,
                    text        = u""):
        '''Adds a log to the cache with the given information'''
        if logId is None:
            log = Log()
        else:
            log = Log(logId)
        log.cache_id = self.id
        log.date = date
        log.logType = logType
        log.finder_id = finder_id
        log.finder_name = finder_name
        log.encoded = encoded
        log.text = text
        log.save()
        return log

    def getAttributes(self):
        '''Returns a list of the attributes for the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id, cache_id FROM Attributes WHERE cache_id = ? ORDER BY id" , (self.id,))
        attributes = []
        for row in cur.fetchall():
            attributes.append(Attribute(row[0], row[1]))
        return attributes

    def getAttributeIds(self):
        '''Returns a list of the id's of the caches attributes'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Attributes WHERE cache_id = ? ORDER BY id" , (self.id,))
        return rows2list(cur.fetchall())

    def getAttributeById(self,attribid):
        '''Returns the attribute with the given id if found, otherwise "None"'''
        assert type(attribid) is int
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Attributes WHERE cache_id = ? AND id = ?", (self.id, attribid,))
        if cur.fetchone() is None:
            return None
        else:
            return Attribute(attribid, self.id)

    def hasAttributes(self):
        '''Returns treu if the cache has attributes associated with it'''
        return len(self.getAttributes()) > 0

    def addAttribute(self, attribid, inc, description):
        '''Adds a attribute to the cache with the given information'''
        attribute = Attribute(attribid, self.id)
        attribute.inc = inc
        attribute.description = description
        attribute.save()
        return attribute

    def getTravelBugs(self):
        '''Returns a list of the travel bugs in the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Travelbugs WHERE cache_id = ? ORDER BY ref" , (self.id,))
        bugs = []
        for row in cur.fetchall():
            bugs.append(TravelBug(row[0]))
        return bugs

    def getTravelBugRefs(self):
        '''Returns a list of the ref's of the travel bugs in the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT ref FROM Travelbugs WHERE cache_id = ? ORDER BY ref" , (self.id,))
        return rows2list(cur.fetchall())

    def hasTravelBugs(self):
        '''Returns True if the cache has travel bugs in it at present'''
        return len(self.getTravelBugRefs()) > 0

    def getTravelBugByRef(self,ref):
        '''Returns the travel bug with the given ref if found, otherwise "None"'''
        assert type(ref)==unicode or type(ref)==str
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Travelbugs WHERE cache_id = ? AND ref = ?" , (self.id, ref,))
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return TravelBug(row[0])

    def addTravelBug(self,ref,id,name=u""):
        '''Adds a travel bug to the cache with the given information'''
        travelbug = TravelBug(id)
        travelbug.cache_id = self.id
        travelbug.ref = ref
        travelbug.name = name
        travelbug.save()
        return travelbug

    def getAddWaypoints(self):
        '''Returns a list of the additional waypoints associated with the cache'''
        addWpts=[]
        for code in self.getAddWaypointCodes():
            addWpts.append(Waypoint(code))
        return addWpts

    def getAddWaypointCodes(self):
        '''Returns a list of the codes of the waypoints associated with the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT code FROM Waypoints WHERE cache_id = ? ORDER BY code",(self.id,))
        return rows2list(cur.fetchall())

    def getAddWaypointByCode(self,code):
        '''Returns the additional waypoint with the given code if found, otherwise "None"'''
        assert type(code)==unicode or type(code)==str
        cur = geocacher.db().cursor()
        cur.execute("SELECT code FROM Waypoints WHERE code = ? AND cache_id = ? ORDER BY code",(code, self.id,))
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return Waypoint(row[0])

    def hasAddWaypoints(self):
        '''Returns True if the cache has additional waypoints, otherwise False'''
        return len(self.getAddWaypointCodes()) > 0


    def addAddWaypoint(self,code,lat  = 0,
                                 lon  = 0,
                                 name = u"",
                                 url  = "",
                                 time = None,
                                 cmt  = u"",
                                 sym  = u""):
        '''Adds an additional waypoint to the cache with the given information'''
        addWpt = Waypoint(code)
        addWpt.cache_id = self.id
        addWpt.lat  = lat
        addWpt.lon  = lon
        addWpt.name = name
        addWpt.url  = url
        addWpt.time = time
        addWpt.cmt  = cmt
        addWpt.sym  = sym
        addWpt.save()
        return addWpt

class Log(object):
    def __init__(self, lid=minint):
        cur = geocacher.db().cursor()
        if lid < 0:
            cur.execute("SELECT id FROM Logs WHERE id=?", (lid, ))
            if cur.fetchone() is None:
                cur.execute('SELECT MIN(id) FROM logs')
                row = cur.fetchone()
                if row[0] is None:
                    lid = -1
                else:
                    lid = min(row[0]-1, -1)
        cur.execute("SELECT id FROM Logs WHERE id=?", (lid, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Logs(id) VALUES (?)", (lid,))
            #cur.execute("INSERT INTO Logs(id, cache_id, date, type, finder_id, finder_name, encoded, text) VALUES (?, -1, -0.1, '', 0, '', 0, '')", (lid,))
        cur.execute('SELECT id, cache_id, log_date, type, finder_id, finder_name, encoded, text FROM Logs WHERE id=?', (lid,))
        row = cur.fetchone()
        if type(row) is sqlite3.dbapi2.Row:
            self.logId       = row[0]
            self.cache_id    = row[1]
            self.date        = row[2]
            self.logType     = row[3]
            self.finder_id   = row[4]
            self.finder_name = row[5]
            self.encoded     = row[6]
            self.text        = row[7]
        else:
            raise geocacher.InvalidID('Invalid Log ID: %d' % lid)

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Logs WHERE id=?", (self.logId,))
        cur.execute("INSERT INTO Logs(id, cache_id, log_date, type, finder_id, finder_name, encoded, text) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (self.logId, self.cache_id, self.date, self.logType, self.finder_id, self.finder_name, self.encoded, self.text,))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Logs WHERE id=?", (self.id,))

class Attribute(object):
    def __init__(self, attribid, cacheid):
        cur = geocacher.db().cursor()
        cur.execute("SELECT id, cache_id FROM Attributes WHERE id=? AND cache_id=?", (attribid, cacheid))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Attributes (id, inc, cache_id, description) VALUES (?, ?, ?, ?)",
                        (attribid, True, cacheid, ''))
        cur.execute("SELECT id, inc, cache_id, description FROM Attributes WHERE id=? AND cache_id=?", (attribid, cacheid))
        row = cur.fetchone()
        if type(row) is sqlite3.dbapi2.Row:
            self.attribid    = row[0]
            self.inc         = row[1]
            self.cache_id    = row[2]
            self.description = row[3]
        else:
            raise geocacher.InvalidID('Invalid Attribute/Cache ID pair: %d/%d' % (attribid, cacheid))

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Attributes WHERE id=? AND cache_id=?",
                    (self.attribid, self.cache_id))
        cur.execute("INSERT INTO Attributes (id, inc, cache_id, description) VALUES (?, ?, ?, ?)",
                    (self.attribid, self.inc, self.cache_id, self.description))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Attributes WHERE id=? AND cache_id=?",
                    (self.attribid, self.cache_id))

    def _getIcon(self):
        if self.inc:
            suffix = '-yes'
        else:
            suffix = '-no'
        return os.path.join('attributes',
                            ATTRIB_ICO[self.attribid] + suffix + '.gif')

    icon = property (_getIcon)

class TravelBug(object):
    def __init__(self, tbid=minint):
        cur = geocacher.db().cursor()
        if tbid < 0:
            cur.execute("SELECT id FROM Travelbugs WHERE id=?", (tbid, ))
            if cur.fetchone() is None:
                cur.execute('SELECT MIN(id) FROM Travelbugs')
                row = cur.fetchone()
                if row[0] is None:
                    bid = -1
                else:
                    bid = min(row[0]-1, -1)
        cur.execute("SELECT id FROM Travelbugs WHERE id=?", (tbid, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Travelbugs(id, cache_id, name, ref) VALUES (?, -1, '', '')", (tbid,))
        cur.execute('SELECT id, cache_id, name, ref FROM Travelbugs WHERE id=?', (tbid,))
        row = cur.fetchone()
        if type(row) is sqlite3.dbapi2.Row:
            self.id       = row[0]
            self.cache_id = row[1]
            self.name     = row[2]
            self.ref      = row[3]
        else:
            raise geocacher.InvalidID('Invalid Travel Bug ID: %d' % tbid)

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Travelbugs WHERE id=?", (self.id,))
        cur.execute("INSERT INTO Travelbugs(id, cache_id, name, ref) VALUES(?, ?, ?, ?)", (self.id, self.cache_id, self.name, self.ref,))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Travelbugs WHERE id=?", (self.id,))

class Waypoint(object):
    def __init__(self, code):
        cur = geocacher.db().cursor()
        cur.execute("SELECT code FROM Waypoints WHERE code=?", (code, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Waypoints(code) VALUES (?)", (code,))
            #cur.execute("INSERT INTO Waypoints(code, cache_id, lat, lon, name, url, time, cmt, sym) VALUES (?, -1, 0.0, 0.0, '', '', ?, '', '')", (code,None,))
        cur.execute('SELECT code, cache_id, lat, lon, name, url, time, cmt, sym FROM Waypoints WHERE code=?', (code,))
        row = cur.fetchone()
        if type(row) is sqlite3.dbapi2.Row:
            self.code     = row[0]
            self.cache_id = row[1]
            self.lat      = row[2]
            self.lon      = row[3]
            self.name     = row[4]
            self.url      = row[5]
            self.time     = row[6]
            self.cmt      = row[7]
            self.sym      = row[8]
        else:
            raise geocacher.InvalidID('Invalid Waypoint Code: %d' % bid)

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Waypoints WHERE code=?", (self.code,))
        cur.execute("INSERT INTO Waypoints(code, cache_id, lat, lon, name, url, time, cmt, sym) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.code , self.cache_id, self.lat, self.lon, self.name, self.url, self.time, self.cmt, self.sym,))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Waypoints WHERE code=?", (self.code,))

class Location(object):
    def __init__(self, name):
        cur = geocacher.db().cursor()
        cur.execute("SELECT name FROM Locations WHERE name=?", (name, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO Locations(name, lat, lon, comment) VALUES (?, 0.0, 0.0, '')", (name,))
        cur.execute('SELECT name, lat, lon, comment FROM Locations WHERE name=?', (name,))
        row = cur.fetchone()
        if type(row) is sqlite3.dbapi2.Row:
            self.name    = row[0]
            self.lat     = row[1]
            self.lon     = row[2]
            self.comment = row[3]
        self.origName = self.name

    def save(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Locations WHERE name=?", (self.origName,))
        cur.execute("INSERT INTO Locations(name, lat, lon, comment) VALUES (?, ?, ?, ?)", (self.name, self.lat, self.lon, self.comment,))
        self.origName = self.name

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Locations WHERE name=?", (self.origName,))

if __name__ == "__main__":
    import os.path
    import webbrowser
    path = os.path.abspath('test.html')
    imgPath = os.path.join('..','gfx','default','attributes')
    html = """<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
<html>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />
"""
    html += """<title>Attribute Icons</title>\n"""
    html += """</head>\n"""
    html += """<body>\n"""
    html += """<H1>Attribute Icons</H1>"""
    for i in range(len(ATTRIBUTES)):
        yes = os.path.join(imgPath, "%s-yes.gif" % ATTRIB_ICO[i])
        no = os.path.join(imgPath, "%s-no.gif" % ATTRIB_ICO[i])
        text = ATTRIBUTES[i]
        html += """<p><img src="%s"/><img src="%s"/> %i %s</p>\n""" % (yes, no, i, text)

    html += """</body\n"""
    html += """ </html>"""
    fid = open(path,"wb")
    fid.write(html.encode( "utf-8" ))
    fid.close()
    webbrowser.open(path)
