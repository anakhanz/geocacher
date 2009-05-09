# -*- coding: UTF-8 -*-

from lxml.etree import Element,ElementTree
import os

from libs import dict4ini

class DB:

    def __init__(self,file):
        """Load the DB or initalise if missing"""
        if os.path.isfile(file):
            self.root = ElementTree(file=file).getroot()
        else:
            self.root = Element("db")
        self.file = file
    
    def save(self):
        """Save the DB"""
        fid = open(self.file,"w")
        fid.write("""<?xml version="1.0" encoding="UTF-8"?>""")
        ElementTree(self.root).write(fid,encoding="utf-8")
        fid.close()

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
        d = {'common':{'lastFolder':Geocacher.getHomeDir()},
             'gc'    :{'userName'  :'',
                       'userId'    :''}}
        Geocacher.conf = dict4ini.DictIni( Geocacher.getConfFile("geocacher.conf"), values=d)

##    @staticmethod
##    def dbgPrint(message, level=1):
##        if level >= Geocacher.debugLevel:
##            print "Debug L%i: %s" % (level, message)