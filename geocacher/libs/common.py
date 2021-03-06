# -*- coding: utf-8 -*-

import logging
import os
import datetime
from time import mktime

def boolToText(b):
    '''Converts a text string to a boolean'''
    return str(b)


def textToBool(t):
    '''Converts a boolean to a text string'''
    assert type(t)==unicode or type(t)==str
    if t =="True":
        return True
    else:
        return False


def dateTimeToText(dt):
    '''Converts a datetime object to an iso string with zulu time'''
    if dt == None:
        return ""
    else:
        return dt.isoformat()+'Z'


def textToDateTime(t):
    '''Converts a date/time string in iso format to a datetime object'''
    assert type(t)==unicode or type(t)==str
    if t == "":
        return None
    else:
        return datetime.datetime(int(t[:4]),int(t[5:7]),int(t[8:10]),
                                  int(t[11:13]),int(t[14:16]),int(t[17:19]))

def wxDateTimeToPy(wxDateTime):
    '''Converts a wx.DateTime object to a datetime object'''
    return datetime.datetime(wxDateTime.GetYear(),
                             wxDateTime.GetMonth()+1,
                             wxDateTime.GetDay(),
                             wxDateTime.GetHour(),
                             wxDateTime.GetMinute(),
                             wxDateTime.GetSecond(),
                             wxDateTime.GetMillisecond()*1000)


def getTextFromPath(root, relativePath, nameSpaces=None, default=None):
    '''
    Returns the text from the first instance found of a given XML path within
    an ElementTree object or the supplied default if the path is not found.

    Arguments:
        root         - ElementTree to find the text within
        relativePath - Path to find
    Keyword Arguments:
        nameSpaces   - Name spaces to use during the search if requider
        default      - Default value to return if the path is not found or it
                       has no text value
    '''

    if nameSpaces==None:
        try:
            ret = root.find(relativePath).text
            logging.debug("'%s' found at path: '%s'" % (ret,relativePath))
        except:
            ret = default
            logging.debug("'%s' path not found" % relativePath)
    else:
        try:
            ret = root.find(relativePath, namespaces=nameSpaces).text
            logging.debug("'%s' found at path: '%s'" % (ret,relativePath))
        except:
            ret = default
            logging.debug("'%s' path not found" % relativePath)
    if ret == None: ret = default
    return ret


def getAttribFromPath(root, relativePath, attrib, nameSpaces=None, default=None):
    '''
    Returns the given attribute text from the first instance found of a given
    XML path within an ElementTree object or the supplied default if the path
    is not found.

    Arguments:
        root         - ElementTree to find the text within
        relativePath - Path to find
        attrib       - Attribute to get the value from
    Keyword Arguments:
        nameSpaces   - Name spaces to use during the search if requider
        default      - Default value to return if the path is not found or it
                       has no text value
    '''

    if nameSpaces==None:
        try:
            ret = root.find(relativePath).attrib[attrib]
            logging.debug("'%s' found at path: '%s', attribute: '%s'" % (ret,relativePath, attrib))
        except:
            ret = default
            logging.debug("'%s' path or '%s' attribute not found" % (relativePath, attrib))
    else:
        try:
            ret = root.find(relativePath, namespaces=nameSpaces).attrib[attrib]
            logging.debug("'%s' found at path: '%s', attribute: '%s'" % (ret,relativePath, attrib))
        except:
            ret = default
            logging.debug("'%s' path or '%s' attribute not found" % (relativePath, attrib))
    return ret

def nl2br(s):
    return '<br />\n'.join(s.split('\n'))

def listFiles(folder):
    """
    Recursively builds and returns a list of valid image files in a given
    directory

    Keyword Arguments:
    folder - Folder to recursively list image files from
    """
    fileList=[]
    dirList = os.listdir(folder)
    dirList.sort()
    for name in dirList:
        path = os.path.join(folder, name)
        if os.path.isfile( path):
            fileList.append(path)
        elif (os.path.isdir(path)):
            fileList += listFiles(path)
    return fileList

def escape(s):
    # you can also use
    # from xml.sax.saxutils import escape
    # Caution: you have to escape '&' first!
    s = s.replace(u'&',u'&amp;')
    s = s.replace(u'<',u'&lt;')
    s = s.replace(u'>',u'&gt;')
    return s

def dateCmp(x,y):
    '''Comparrison function for dates where some items may be of the 'None' type'''
    if x == None and y == None:
        return 0
    elif x == None and y != None:
        return 1
    elif x != None and y == None:
        return -1
    elif x > y:
        return 1
    elif x == y:
        return 0
    else:
        return -1

def rows2list(rows):
    retList = []
    for row in rows:
        retList.append(row[0])
    return retList

def date2float(date):
    if date is None:
        return -0.1
    else:
        return mktime(date.timetuple())

def float2date(f):
    if f < 0:
        return None
    else:
        return datetime.datetime.fromtimestamp(f)
