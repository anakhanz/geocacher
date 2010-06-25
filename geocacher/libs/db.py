# -*- coding: UTF-8 -*-

#import datetime.datetime

import datetime
import os
import os.path
import sqlite3
import shutil
import tempfile
import zipfile

import wx

import geocacher
from geocacher.libs.common import rows2list
from geocacher.libs.dbobjects import Cache, Location


class Database(object):
    __shared_state = {}

    def __init__(self, debugging=False):
        __sharde_state = {}
        self.__dict__ = self.__shared_state
        if not hasattr(self, "allstatements"):
            self.allstatements = sorted(filter(lambda x: x.startswith("statements_v"), Database.__dict__.keys()))
        if not hasattr(self, "database"):
            self.open(geocacher.config().dbfile, debugging)

    def open(self, dbfile=None, debugging=False):
        if dbfile is None: dbfile = geocacher.config().dbfile
        self.close()
        if debugging:
            self.prepdb(":memory:", True)
        else:
            geocacher.config().dbfile = dbfile
            if not os.path.isdir(geocacher.config().dbpath):
                os.makedirs(geocacher.config().dbpath)
            self.prepdb(geocacher.config().dbfile, True)

    def close(self):
        if hasattr(self, "database"):
            self.database.close()
            del self.database

    def cursor(self):
        return self.database.cursor()

    def commit(self):
        return self.database.commit()

    def prepdb(self, dbname, debug=False):
        self.database = sqlite3.connect(database=dbname, timeout=1.0)
        #self.database.create_function("distance", 4, cache901.util.distance_exact)
        self.database.row_factory = sqlite3.Row
        cur = self.database.cursor()
        try:
            cur.execute("select version from version")
            row = cur.fetchone()
            vname = 'statements_v%03d' % row[0]
            print vname
            for stgrp in self.allstatements[self.allstatements.index(vname)+1:]:
                stmts = Database.__dict__[stgrp]
                self.sqlexec(stmts, debug)
                vnum = int(stgrp[-3:])
                cur.execute("UPDATE version SET version=?", (vnum, ))
                self.database.commit()
        except sqlite3.OperationalError:
            for stgrp in self.allstatements:
                stmts = Database.__dict__[stgrp]
                self.sqlexec(stmts, debug)
                vnum = int(stgrp[-3:])
                cur.execute("UPDATE version SET version=?", (vnum, ))
                self.database.commit()

    def _getVersion(self, item):
        assert type(item) == str or type(item) == unicode
        sql = "SELECT version FROM Versions WHERE name=?"
        data = self.c.execute(sql, (version,)).fetchall()
        if len(data) == 0:
            version = 0.0
            sql = "INSERT INTO Versions VALUES(?, ?)"
            self.c.execute(sql, (item, version,))
        else:
            version = float(data[0][0])
        return version

    def sqlexec(self, statements, debug=False):
        cur = self.cursor()
        for stmt in statements:
            if debug:
                print "---------------------------------"
                print stmt
                print "---------------------------------"
            cur.execute(stmt)

    def maintdb(self):
        cur = self.cursor()
        #cache901.notify('Recovering unused disk space')
        cur.execute("vacuum")
        #cache901.notify('Rebuilding database indices')
        cur.execute("analyze")
        self.commit()

    def backup(self):
        self.close()
        dbpath = geocacher.config().dbpath
        today = datetime.date.today().isoformat()
        ext = "-%s.zip" % (today)
        zfilename = os.sep.join([dbpath, 'Geocacher_Backup%s' % ext])
        z=zipfile.ZipFile(zfilename, "w", allowZip64=True)
        for dbfile in filter(lambda x:x.lower().endswith('.sqlite'), os.listdir(geocacher.config().dbpath)):
            dbfile = os.sep.join([dbpath, dbfile.encode('ascii')])
            arcname = "%s-%s.sqlite" % (os.path.splitext(os.path.split(dbfile)[1])[0], today)
            arcname = arcname.encode('ascii')
            #cache901.notify('Backing up %s into %s' % (arcname, zfilename))
            z.write(dbfile, arcname, compress_type=zipfile.ZIP_DEFLATED)
        z.close()
        self.open()

    def restore(self, backup_file):
        self.close()
        dbpath = geocacher.config().dbpath
        tempDir = tempfile.mkdtemp()
        sucess = False
        try:
            z = zipfile.ZipFile(backup_file, mode='r')
            for f in z.namelist():
                print f
                if f[:9] == geocacher.appname and os.path.splitext(f)[1] == '.sqlite':
                    z.extract(f, tempDir)
                    sucess = True
                    break
            z.close()
        except:
            sucess = False
        if sucess:
            print f
            shutil.move(os.path.join(tempDir, f), geocacher.config().dbfile)
            print tempDir
        shutil.rmtree(tempDir)
        self.open()
        return sucess

    statements_v001 = [
        "CREATE TABLE version (version integer)",
        "INSERT INTO Version(version) VALUES(1)",
        # Caches.cid: unique int (comes from groundspeak:cache tag, id attribute)
        # Caches.locked: boolean
        # Caches.user_date: datetime (reporesented by unix timestamp)
        # Caches.user_date: datetime (reporesented by unix timestamp)
        # Caches.gpx_date: datetime (reporesented by unix timestamp)
        # Caches.placed
        # Caches.avaliable: boolean
        # Caches.archived: boolean
        # Caches.short_desc_html: boolean
        # Caches.long_desc_html: boolean
        # Caches.ftf: boolean
        # Caches.found: boolean
        # Caches.found_date: datetime (reporesented by unix timestamp)
        # Caches.dnf: boolean
        # Caches.dnf_date: datetime (reporesented by unix timestamp)
        # Caches.own_log_encoded: boolean
        # Caches.corrected: boolean
        # Caches.user_flag: boolean
        """
        CREATE TABLE Caches (
            id INTEGER PRIMARY KEY,
            code TEXT,
            lat REAL,
            lon REAL,
            name TEXT,
            url TEXT,
            locked INTEGER,
            user_date REAL,
            gpx_date REAL,
            placed REAL,
            placed_by TEXT,
            owner TEXT,
            owner_id INTEGER,
            container TEXT,
            difficulty REAL,
            terrain REAL,
            type TEXT,
            available INTEGER,
            archived INTEGER,
            state TEXT,
            country TEXT,
            short_desc TEXT,
            short_desc_html INTEGER,
            long_desc TEXT,
            long_desc_html INTEGER,
            encoded_hints TEXT,
            ftf INTEGER,
            found INTEGER,
            found_date REAL,
            dnf INTEGER,
            dnf_date REAL,
            own_log_id INTEGER,
            source TEXT,
            corrected INTEGER,
            clat REAL,
            clon REAL,
            cnote TEXT,
            user_comments TEXT,
            user_flag INTEGER,
            user_data1 TEXT,
            user_data2 TEXT,
            user_data3 TEXT,
            user_data4 TEXT)
        """,
        "CREATE INDEX caches_code ON Caches(code)",
        "CREATE INDEX caches_name ON Caches(name)",
        # Logs.cache_id: int, links to Cache.id
        # Logs.date: : datetime (reporesented by unix timestamp)
        # Logs.encoded: boolean
        """
        CREATE TABLE Logs (
            id INTEGER PRIMARY KEY,
            cache_id INTEGER,
            date FLOAT,
            type TEXT,
            finder_id INTEGER,
            finder_name TEXT,
            encoded INTEGER,
            text TEXT)
        """,
        "CREATE INDEX logs_cache_id ON Logs(cache_id)",
        # Travelbugs.cache_id: int, links to Cache.id
        """
        CREATE TABLE Travelbugs (

            id INTEGER PRIMARY KEY,
            cache_id INTEGER,
            name TEXT,
            ref TEXT)
        """,
        "CREATE INDEX travelbugs_cache_id ON Travelbugs(cache_id)",
        # Waypoints.cache_id: int, links to Cache.id
        """
        CREATE TABLE Waypoints (
            code TEXT PRIMARY KEY,
            cache_id INTERGER,
            lat FLOAT,
            lon FLOAT,
            name TEXT,
            url TEXT,
            time REAL,
            cmt TEXT,
            sym TEXT)
        """,
        "CREATE INDEX waypoints_cache_id ON Waypoints(cache_id)",
        "CREATE INDEX waypoints_code ON Waypoints(code)",
        """
        CREATE TABLE Locations (
            name TEXT PRIMARY KEY,
            lat REAL,
            lon REAL,
            comment TEXT)""",
        """
        INSERT INTO Locations(name, lat, lon, comment)
        VALUES('Default', 0.0, 0.0, '')
        """
    ]

    def getCacheList(self):
        '''
        Returns a list of the caches in the database
        '''
        cur = self.cursor()
        cur.execute("SELECT id FROM Caches ORDER BY code")
        cacheList = []
        for row in cur.fetchall():
            cacheList.append(Cache(row[0]))
        return cacheList

    def getCacheCodeList(self):
        '''
        Returns a list of the codes of each cache in the database
        '''
        cur = self.cursor()
        cur.execute("SELECT code FROM Caches ORDER BY code")
        return rows2list(cur.fetchall())

    def getNumberCaches(self):
        '''
        Returns the number of caches in the database
        '''
        cur = self.cursor()
        cur.execute("SELECT id FROM Caches")
        return len(cur.fetchall())

    def getCacheByCode(self,code):
        '''
        Returns the cache with the given code if found, otherwise "None"

        Argument
        code: code of the cache to be returned
        '''
        cur = self.cursor()
        cur.execute("SELECT id FROM Caches WHERE code = ?", (code,))
        id_row = cur.fetchone()
        if id_row is None:
            return None
        else:
            return Cache(id_row[0])

    def getFoundCacheList(self):
        '''
        Returns a list of found caches.
        '''
        cur = self.cursor()
        cur.execute("SELECT id FROM Caches WHERE found = 1 ORDER BY code")
        cacheList = []
        for row in cur.fetchall():
            cacheList.append(Cache(row[0]))
        return cacheList

    def addCache(self,code,id,
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
                        own_log_id=0,
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
        cache = Cache(id)
        cache.code            = code
        cache.lat             = lat
        cache.lon             = lon
        cache.name            = name
        cache.url             = url
        cache.locked          = locked
        cache.user_date       = user_date
        cache.gpx_date        = gpx_date
        cache.type            = type
        cache.placed          = placed
        cache.placed_by       = placed_by
        cache.owner           = owner
        cache.owner_id        = owner_id
        cache.container       = container
        cache.difficulty      = difficulty
        cache.terrain         = terrain
        cache.available       = available
        cache.archived        = archived
        cache.state           = state
        cache.country         = country
        cache.short_desc      = short_desc
        cache.short_desc_html = short_desc_html
        cache.long_desc       = long_desc
        cache.long_desc_html  = long_desc_html
        cache.encoded_hints   = encoded_hints
        cache.found           = found
        cache.ftf             = ftf
        cache.found_date      = found_date
        cache.dnf             = dnf
        cache.dnf_date        = dnf_date
        cache.own_log_id      = own_log_id
        cache.source          = source
        cache.corrected       = corrected
        cache.clat            = clat
        cache.clon            = clon
        cache.cnote           = cnote
        cache.user_comments   = user_comments
        cache.user_flag       = user_flag
        cache.user_data1      = user_data1
        cache.user_data2      = user_data2
        cache.user_data3      = user_data3
        cache.user_data4      = user_data4
        cache.save()
        cache.refreshOwnLog()

        return cache

    def getLocationList(self):
        '''
        Returns a list of home locations
        '''
        locationList = []
        for name in self.getLocationNameList():
            locationList.append(Location(name))
        return locationList

    def getLocationNameList(self):
        '''
        Returns a list of home location names
        '''
        cur = self.cursor()
        cur.execute("SELECT name FROM Locations ORDER BY name")
        return rows2list(cur.fetchall())

    def getLocationByName(self,name):
        '''
        Returns the location with the given name if found, otherwise "None

        Argument
        name: Name of the location to return
        "'''
        cur = self.cursor()
        cur.execute("SELECT name FROM Locations WHERE name = ?", (name,))
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return Location(row[0])

    def addLocation(self,name,lat=0.0,lon=0.0,comment=""):
        '''Adds a new location with the given data'''
        location = Location(name)
        location.lat = lat
        location.lon = lon
        location.comment = comment
        location.save()
        return location

def main ():
    # set-up old xml db for import
    from datetime import datetime
    from geocacher.libs.xmldb import Geocacher
    old_db = Geocacher(True).db

##    # Import old Locations
##    for loc in old_db.getLocationList():
##        geocacher.db().addLocation(loc.name, loc.lat, loc.lon)
##    geocacher.db().close()
##
##    # Import old caches
##    c = 0
##    total_waypoints = 0
##    total_logs = 0
##    total_travelbugs = 0
##    for cache in old_db.getCacheList():
##        c += 1
##        print " cache %i" % c
##        new_cache = geocacher.db().addCache(cache.code, cache.id, cache.lat, cache.lon, cache.name, cache.url, cache.locked, cache.user_date, cache.gpx_date, cache.symbol, cache.placed, cache.placed_by, cache.owner, cache.owner_id, cache.container, cache.difficulty, cache.terrain, cache.type, cache.available, cache.archived, cache.state, cache.country, cache.short_desc, cache.short_desc_html, cache.long_desc, cache.long_desc_html, cache.encoded_hints, cache.ftf, cache.found, cache.found_date, cache.dnf, cache.dnf_date, 0, cache.source, cache.corrected, cache.clat, cache.clon, cache.cnote, cache.user_comments, cache.user_flag, cache.user_data1, cache.user_data2, cache.user_data3, cache.user_data4)
##        w = 0
##        l = 0
##        t = 0
##        for wp in cache.getAddWaypoints():
##            w += 1
##            print "    waypoint %i" % w
##            new_wp = new_cache.addAddWaypoint(wp.code, wp.lat, wp.lon, wp.name, wp.url, wp.time, wp.cmt, wp.sym)
##        for log in cache.getLogs():
##            l += 1
##            print "    log %i" % l
##            new_log = new_cache.addLog(log.id, log.date, log.type, log.finder_id, log.finder_name, log.encoded, log.text)
##        for tb in cache.getTravelBugs():
##            t += 1
##            print "    travel bug %i" % t
##            new_tb = new_cache.addTravelBug(tb.ref, tb.id, tb.name)
##        total_waypoints += w
##        total_logs += l
##        total_travelbugs += t
##
##    print "Totals:"
##    print "    Caches     %i" % c
##    print "    Waypoints  %i" % total_waypoints
##    print "    Logs       %i" % total_logs
##    print "    Travel bug %i" % total_travelbugs
    geocacher.db().maintdb()
    geocacher.db().backup()


if __name__ == "__main__":
    main()