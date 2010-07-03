# -*- coding: UTF-8 -*-

import sys
import sqlite3

import geocacher
from geocacher.libs.common import rows2list

minint = 0-sys.maxint



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
            #cur.execute("INSERT INTO Caches(id, code, lat, lon, name, url, locked, user_date, gpx_date, placed,placed_by, owner, owner_id, container, difficulty, terrain, type, available, archived, state, country, short_desc, short_desc_html, long_desc, long_desc_html, encoded_hints, ftf, found, found_date, dnf, dnf_date, own_log_id, source, corrected, clat, clon, cnote, user_comments, user_flag, user_data1, user_data2, user_data3, user_data4) VALUES(?, '', 0.0, 0.0, '', '', 0, -0.1, -0.1, -0.1, '', '', 0, '', 1.0, 1.0, '', 1, 0, '', '', '', 0, '', 0, '', 0, 0, -0.1, 0, -0.1, 0, '', 0, 0.0, 0.0, '', '', '', '', '', '', '')", (cid,))
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
        cur.execute("DELETE FROM Logs WHERE cache_id=?", (self.id,))

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
            sql = sql + " ORDER BY date"
        if descending:
            sql = sql + " DESC"
        cur.execute(sql , (self.id,))
        rows = cur.fetchall()
        if maxLen is not None:
            rows = rows[:maxLen]
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

    def getTravelBugs(self):
        '''Returns a list of the travel bugs in the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Travelbugs WHERE cache_id = ? ORDER BY ref" , (self.id,))
        bugs=[]
        for row in cur.fetchall():
            bugs.append(TravelBug(row[0]))
        return bugs

    def getTravelBugRefs(self):
        '''Returns a list of th ref's of the travel bugs in the cache'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT ref FROM Travelbugs WHERE cache_id = ? ORDER BY ref" , (self.id,))
        return rows2list(cur.fetchall())

    def hasTravelBugs(self):
        '''Returns True if the cache has travel bugs in it at present'''
        cur = geocacher.db().cursor()
        cur.execute("SELECT id FROM Travelbugs WHERE cache_id = ?" , (self.id,))
        return len(cur.fetchall()) > 0

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
        cur.execute('SELECT id, cache_id, date, type, finder_id, finder_name, encoded, text FROM Logs WHERE id=?', (lid,))
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
        cur.execute("INSERT INTO Logs(id, cache_id, date, type, finder_id, finder_name, encoded, text) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (self.logId, self.cache_id, self.date, self.logType, self.finder_id, self.finder_name, self.encoded, self.text,))

    def delete(self):
        cur = geocacher.db().cursor()
        cur.execute("DELETE FROM Logs WHERE id=?", (self.id,))

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
