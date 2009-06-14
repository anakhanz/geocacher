# -*- coding: utf-8 -*-

import logging
import datetime
from string import digits


def boolToText(bool):
    '''Converts a text string to a boolean'''
    return str(bool)


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


def textToDateTime(t): # TODO: add microsecond
    '''Converts a date/time string in iso format to a datetime object'''
    assert type(t)==unicode or type(t)==str
    if t == "":
        return None
    else:
        return datetime.datetime(int(t[:4]),int(t[5:7]),int(t[8:10]),
                                  int(t[11:13]),int(t[14:16]),int(t[17:19]))


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
            ret = root.xpath(relativePath)[0].attrib[attrib]
        except:
            ret = default
    else:
        try:
            ret = root.xpath(relativePath, namespaces=nameSpaces)[0].attrib[attrib]
        except:
            ret = default
    return ret


def escape(str):
    # you can also use
    # from xml.sax.saxutils import escape
    # Caution: you have to escape '&' first!
    str = str.replace(u'&',u'&amp;')
    str = str.replace(u'<',u'&lt;')
    str = str.replace(u'>',u'&gt;')
    return str
