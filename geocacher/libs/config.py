# -*- coding: UTF-8 -*-

import os
import os.path
import sys

import wx

import geocacher

class Config(object):
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        if not hasattr(self, "config"):
            self.config = wx.Config(geocacher.appname)
            wx.Config.Set(self.config)

    def getMainWinSize(self):
        self.config.SetPath('/MainWin')
        size = wx.Size()
        size.width = self.config.ReadInt('Width', 700)
        size.height = self.config.ReadInt('Height', 500)
        return size

    def setMainWinSize(self, size):
        self.config.SetPath('/MainWin')
        return self.config.WriteInt('Width', size.width) or\
               self.config.WriteInt('Height', size.height)

    def getDetailSplitPos(self):
        self.config.SetPath('/MainWin')
        return self.config.ReadInt('DetailSplitPos', 400)

    def setDetailSplitPos(self, pos):
        self.config.SetPath('/MainWin')
        return self.config.WriteInt('DetailSplitPos', pos)

    def getDbPath(self):
        return(os.sep.join([wx.StandardPaths.GetUserConfigDir(wx.StandardPaths.Get()), geocacher.appname]))

    def getDbFile(self):
        self.config.SetPath('/PerMachine')
        if not self.config.HasEntry('LastOpenedDb'):
            return os.sep.join([self.dbpath, '%s.sqlite' % (geocacher.appname)])
        else:
            return os.sep.join([self.dbpath, self.config.Read('LastOpenedDb')])

    def getDbFileBase(self):
        self.config.SetPath('/PerMachine')
        if not self.config.HasEntry('LastOpenedDb'):
            return geocacher.appname
        else:
            return os.path.splitext(self.config.Read('LastOpenedDb'))[0]

    def setDbFile(self, lastdb):
        self.config.SetPath('/PerMachine')
        isinstance(lastdb, str)
        dbfile = lastdb.replace('%s%s' % (self.dbpath, os.sep), '')
        if dbfile == lastdb:
            raise Exception('Invalid Database Location. Database must be under %s' % (self.dbpath))
        return self.config.Write('LastOpenedDb', dbfile)

    def getCacheColumnOrder(self):
        self.config.SetPath("/OptionsUI")
        if not self.config.HasEntry("CacheColumnOrder"):
            return ["code","id","lat","lon","name","found","type","size","distance","bearing"]
        else:
            colOrderString = str(self.config.Read("CacheColumnOrder"))
            return colOrderString.split(",")

    def setCacheColumnOrder(self, colOrderList):
        self.config.SetPath("/OptionsUI")
        orderString = ",".join(colOrderList)
        return self.config.Write("CacheColumnOrder", orderString)

    def getCacheSortColumn(self):
        self.config.SetPath("/OptionsUI")
        return str(self.config.Read("CacheSortColumn", "code"))

    def setCacheSortColumn(self, column):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("CacheSortColumn", column)

    def getCacheSortDescend(self):
        self.config.SetPath("/OptionsUI")
        return self.config.ReadBool("CacheSortDescend", False)

    def setCacheSortDescend(self, b):
        self.config.SetPath("/OptionsUI")
        return self.config.WriteBool("CacheSortDescend", b)

    def getUserData1Label(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("UserData1Label", _("User Data 1"))

    def setUserData1Label(self, label):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("UserData1Label", label)

    def getUserData2Label(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("UserData2Label", _("User Data 2"))

    def setUserData2Label(self, label):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("UserData2Label", label)

    def getUserData3Label(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("UserData3Label", _("User Data 3"))

    def setUserData3Label(self, label):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("UserData3Label", label)

    def getUserData4Label(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("UserData4Label", _("User Data 4"))

    def setUserData4Label(self, label):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("UserData4Label", label)

    def getCurrentLocation(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("CurrentLocation", "Default")

    def setCurrentLocation(self, location):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("CurrentLocation", location)

    def getCurrentLatLon(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT lat, lon FROM Locations WHERE name = ?",(self.currentLocation,))
        row = cur.fetchone()
        if row is None:
            return (0.0, 0.0)
        else:
            return (row[0], row[1])

    def getIconTheme(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("IconTheme", "default")

    def setIconTheme(self, theme):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("IconTheme", theme)

    def getCoordinateFormat(self):
        self.config.SetPath("/OptionsUI")
        return self.config.Read("CoordinateFormat", "hdd mm.mmm")

    def setCoordinateFormat(self, fmt):
        self.config.SetPath("/OptionsUI")
        return self.config.Write("CoordinateFormat", fmt)

    def getImperialUnits(self):
        self.config.SetPath("/OptionsUI")
        return self.config.ReadBool("ImperialUnits", )

    def setImperialUnits(self, b):
        self.config.SetPath("/OptionsUI")
        return self.config.WriteBool("ImperialUnits", b)

    def getShowFilter(self):
        self.config.SetPath("/OptionsUI")
        return self.config.ReadBool("ShowFilter", True)

    def setShowFilter(self, show):
        self.config.SetPath("/OptionsUI")
        self.config.WriteBool("ShowFilter", show)

    def getFilterMine(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadBool("Mine", True)

    def setFilterMine(self, b):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteBool("Mine", b)

    def getFilterFound(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadBool("Found", True)

    def setFilterFound(self, b):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteBool("Found", b)

    def getFilterDisabled(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadBool("Disabled", True)

    def setFilterDisabled(self, b):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteBool("Disabled", b)

    def getFilterArchived(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadBool("Archived", True)

    def setFilterArchived(self, b):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteBool("Archived", b)

    def getFilterOverDist(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadBool("OverDist", True)

    def setFilterOverDist(self, b):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteBool("OverDist", b)

    def getFilterMaxDist(self):
        self.config.SetPath("/CacheFilter")
        return self.config.ReadFloat("MaxDist", 50.0)

    def setFilterMaxDist(self, f):
        self.config.SetPath("/CacheFilter")
        return self.config.WriteFloat("MaxDist", f)

    def getGCUserName(self):
        self.config.SetPath("/Geocaching.com")
        return self.config.Read("UserName", "")

    def setGCUserName(self, s):
        self.config.SetPath("/Geocaching.com")
        return self.config.Write("UserName", s)

    def getGCUserID(self):
        self.config.SetPath("/Geocaching.com")
        return self.config.Read("UserID", "")

    def setGCUserID(self, s):
        self.config.SetPath("/Geocaching.com")
        return self.config.Write("UserID", s)

    def getDisplayedCache(self):
        self.config.SetPath("/State")
        return self.config.Read("DisplayedCache", "")

    def setDisplayedCache(self, s):
        self.config.SetPath("/State")
        return self.config.Write("DisplayedCache", s)

    def getGpsType(self):
        self.config.SetPath("/GPS")
        return self.config.Read("Type", "Garmin")

    def setGpsType(self, s):
        self.config.SetPath("/GPS")
        return self.config.Write("Type", s)

    def getGpsConnection(self):
        self.config.SetPath("/GPS")
        return self.config.Read("Connection", "usb:")

    def setGpsConnection(self, s):
        self.config.SetPath("/GPS")
        return self.config.Write("Connection", s)

    def getExportType(self):
        self.config.SetPath("/Export")
        return self.config.Read("Type", "")

    def setExportType(self, s):
        self.config.SetPath("/Export")
        return self.config.Write("Type", s)

    def exportPath(self):
        self.config.SetPath("/Export/" + self.getExportType())

    def getExportFile(self):
        self.exportPath()
        return self.config.Read("File", "")

    def setExportFile(self, f):
        self.exportPath()
        return self.config.Write("File", f)

    def getExportFilterDisp(self):
        self.exportPath()
        return self.config.ReadBool("FilterDisp", True)

    def setExportFilterDisp(self, b):
        self.exportPath()
        return self.config.WriteBool("FilterDisp", b)

    def getExportFilterSel(self):
        self.exportPath()
        return self.config.ReadBool("FilterSel", False)

    def setExportFilterSel(self, b):
        self.exportPath()
        return self.config.WriteBool("FilterSel", b)

    def getExportFilterUser(self):
        self.exportPath()
        return self.config.ReadBool("FilterUser", False)

    def setExportFilterUser(self, b):
        self.exportPath()
        return self.config.WriteBool("FilterUser", b)

    def getExportScope(self):
        self.exportPath()
        return self.config.Read("Scope", "simple")

    def setExportScope(self, s):
        self.exportPath()
        return self.config.Write("Scope", s)

    def getExportGc(self):
        self.exportPath()
        return self.config.ReadBool("Gc", False)

    def setExportGc(self, b):
        self.exportPath()
        return self.config.WriteBool("Gc", b)

    def getExportLogs(self):
        self.exportPath()
        return self.config.ReadBool("Logs", False)

    def setExportLogs(self, b):
        self.exportPath()
        return self.config.WriteBool("Logs", b)

    def getExportTbs(self):
        self.exportPath()
        return self.config.ReadBool("Tbs", False)

    def setExportTbs(self, b):
        self.exportPath()
        return self.config.WriteBool("Tbs", b)

    def getExportAddWpts(self):
        self.exportPath()
        return self.config.ReadBool("AddWpts", False)

    def setExportAddWpts(self, b):
        self.exportPath()
        return self.config.WriteBool("AddWpts", b)

    def getExportSepAddWpts(self):
        self.exportPath()
        return self.config.ReadBool("SepAddWpts", False)

    def setExportSepAddWpts(self, b):
        self.exportPath()
        return self.config.WriteBool("SepAddWpts", b)

    def getExportAdjWpts(self):
        self.exportPath()
        return self.config.ReadBool("AdjWpts", True)

    def setExportAdjWpts(self, b):
        self.exportPath()
        return self.config.WriteBool("AdjWpts", b)

    def getExportAdjWptSufix(self):
        self.exportPath()
        return self.config.Read("AdjWptSufix", "-a")

    def setExportAdjWptSufix(self, s):
        self.exportPath()
        return self.config.Write("AdjWptSufix", s)

    def getExportLimitLogs(self):
        self.exportPath()
        return self.config.ReadBool("LimitLogs", False)

    def setExportLimitLogs(self, b):
        self.exportPath()
        return self.config.WriteBool("LimitLogs", b)

    def getExportMaxLogs(self):
        self.exportPath()
        return self.config.ReadInt("MaxLogs", 4)

    def setExportMaxLogs(self, i):
        self.exportPath()
        return self.config.WriteInt("MaxLogs", i)

    def getExportLogOrder(self):
        self.exportPath()
        return self.config.ReadInt("LogOrder", 0)

    def setExportLogOrder(self, i):
        self.exportPath()
        return self.config.WriteInt("LogOrder", i)

    def getImportFolder(self):
        self.config.SetPath("/Import")
        return self.config.Read("ImportFolder", wx.StandardPaths.GetDocumentsDir(wx.StandardPaths.Get()))

    def setImportFolder(self, s):
        self.config.SetPath("/Import")
        return self.config.Write("ImportFolder", s)

    def getImportFile(self):
        self.config.SetPath("/Import")
        return self.config.Read("ImportFile", "")

    def setImportFile(self, s):
        self.config.SetPath("/Import")
        return self.config.Write("ImportFile", s)

    def getImportMode(self):
        self.config.SetPath("/Import")
        return self.config.Read("ImportMode", "update")

    def setImportMode(self, s):
        self.config.SetPath("/Import")
        return self.config.Write("ImportMode", s)


    mainWinSize        = property(getMainWinSize,       setMainWinSize)
    detailSplit        = property(getDetailSplitPos,    setDetailSplitPos)
    displayedCache     = property(getDisplayedCache,    setDisplayedCache)
    showFilter         = property(getShowFilter,        setShowFilter)
    filterMine         = property(getFilterMine,        setFilterMine)
    filterFound        = property(getFilterFound,       setFilterFound)
    filterDisabled     = property(getFilterDisabled,    setFilterDisabled)
    filterArchived     = property(getFilterArchived,    setFilterArchived)
    filterOverDist     = property(getFilterOverDist,    setFilterOverDist)
    filterMaxDist      = property(getFilterMaxDist,     setFilterMaxDist)
    currentLocation    = property(getCurrentLocation,   setCurrentLocation)
    currentLatLon      = property(getCurrentLatLon)
    iconTheme          = property(getIconTheme,         setIconTheme)
    coordinateFormat   = property(getCoordinateFormat,  setCoordinateFormat)
    imperialUnits      = property(getImperialUnits,     setImperialUnits)
    cacheColumnOrder   = property(getCacheColumnOrder,  setCacheColumnOrder)
    cacheSortColumn    = property(getCacheSortColumn,   setCacheSortColumn)
    cacheSortDescend   = property(getCacheSortDescend,  setCacheSortDescend)
    userData1Label     = property(getUserData1Label,    setUserData1Label)
    userData2Label     = property(getUserData2Label,    setUserData2Label)
    userData3Label     = property(getUserData3Label,    setUserData3Label)
    userData4Label     = property(getUserData4Label,    setUserData4Label)
    GCUserName         = property(getGCUserName,        setGCUserName)
    GCUserID           = property(getGCUserID,          setGCUserID)
    dbpath             = property(getDbPath)
    dbfile             = property(getDbFile,            setDbFile)
    dbfilebase         = property(getDbFileBase)
    gpsType            = property(getGpsType,           setGpsType)
    gpsConnection      = property(getGpsConnection,     setGpsConnection)
    exportType         = property(getExportType,        setExportType)
    exportFile         = property(getExportFile,        setExportFile)
    exportFilterDisp   = property(getExportFilterDisp,  setExportFilterDisp)
    exportFilterSel    = property(getExportFilterSel,   setExportFilterSel)
    exportFilterUser   = property(getExportFilterUser,  setExportFilterUser)
    exportScope        = property(getExportScope,       setExportScope)
    exportGc           = property(getExportGc,          setExportGc)
    exportLogs         = property(getExportLogs,        setExportLogs)
    exportTbs          = property(getExportTbs,         setExportTbs)
    exportAddWpts      = property(getExportAddWpts,     setExportAddWpts)
    exportSepAddWpts   = property(getExportSepAddWpts,  setExportSepAddWpts)
    exportAdjWpts      = property(getExportAdjWpts,     setExportAdjWpts)
    exportAdjWptSufix  = property(getExportAdjWptSufix, setExportAdjWptSufix)
    exportLimitLogs    = property(getExportLimitLogs,   setExportLimitLogs)
    exportMaxLogs      = property(getExportMaxLogs,     setExportMaxLogs)
    exportLogOrder     = property(getExportLogOrder,    setExportLogOrder)
    importFolder       = property(getImportFolder,      setImportFolder)
    importFile         = property(getImportFile,        setImportFile)
    importMode         = property(getImportMode,        setImportMode)