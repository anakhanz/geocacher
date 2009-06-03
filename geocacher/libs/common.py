# -*- coding: utf-8 -*-

import logging
import datetime
from string import digits

def boolToText(bool):
    if bool:
        return "True"
    else:
        return "False"

def textToBool(t):
    assert type(t)==unicode or type(t)==str
    if t =="True":
        return True
    else:
        return False

def dateTimeToText(dt):
    if dt == None:
        return ""
    else:
        return dt.isoformat()+'Z'

def textToDateTime(t): # TODO: add microsecond
    assert type(t)==unicode or type(t)==str
    if t == "":
        return None
    else:
        return datetime.datetime(int(t[:4]),int(t[5:7]),int(t[8:10]),int(t[11:13]),int(t[14:16]),int(t[17:19]))

def getTextFromPath(root, relativePath, nameSpaces=None, default=None):
    if nameSpaces==None:
        try:
            ret = root.xpath(relativePath)[0].text
            logging.debug("'%s' found at path '%s'" % (ret,relativePath))
        except:
            ret = default
            logging.debug("'%s' path not found" % relativePath)
    else:
        try:
            ret = root.xpath(relativePath, namespaces=nameSpaces)[0].text
            logging.debug("'%s' found at path '%s'" % (ret,relativePath))
        except:
            ret = default
            logging.debug("'%s' path not found" % relativePath)
    return ret

def getAttribFromPath(root, relativePath, attrib, nameSpaces=None, default=None):
    if nameSpaces==None:
        try:
            ret = root.xpath(relativePath)[0].attrib[attrib]
        except:
            ret = default
    else:
        try:
            ret = root.xpath(relativePath, namespaces=nameSpaces)[0].attrib[attrib]
        except:
            ret = default
    return ret