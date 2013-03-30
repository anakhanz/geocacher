# -*- coding: UTF-8 -*-

from math import sqrt, degrees, radians, sin, cos, atan2

import re

def distance(lat1, lon1, lat2, lon2, miles = False):
    '''
    Takes a pair of coordinates and returns the distance between them in
    Kilometres or Miles.

    Arguments:
        lat1  - Latitude of the first pair of coordinates
        lon1  - Longitude of the first pair of coordinates
        lat2  - Latitude of the second pair of coordinates
        lon2  - Longitude of the second pair of coordinates
    Keyword Argument:
        miles - Sets the output unit to Miles instead of Kilometres if defined
                as True
    '''
    # Convert to radians
    rLat1 = radians(lat1)
    rLon1 = radians(lon1)
    rLat2 = radians(lat2)
    rLon2 = radians(lon2)

    # Calculate the differences in radians
    dLat = rLat2 - rLat1
    dLon = rLon2 - rLon1

    # mean radius of Earth in km
    r = 6372.797

    a = sin(dLat / 2) * sin(dLat / 2) + cos(rLat1) * cos(rLat2) * sin(dLon / 2) * sin(dLon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = r * c
    if miles:
        return(km * 0.621371192)
    else:
        return km

def bearing(lat1, lon1, lat2, lon2):
    '''
    Takes a pair of coordinates and returns the bearing in degrees from the
    first pair of coordinates to the second pair of coordinates.

    Arguments:
        lat1  - Latitude of the first pair of coordinates
        lon1  - Longitude of the first pair of coordinates
        lat2  - Latitude of the second pair of coordinates
        lon2  - Longitude of the second pair of coordinates
    '''
    # Convert to radians
    rLat1 = radians(lat1)
    rLon1 = radians(lon1)
    rLat2 = radians(lat2)
    rLon2 = radians(lon2)

    # Calculate the differences in radians
    dLon = rLon2 - rLon1

    y = sin(dLon) * cos(rLat2);
    x = cos(rLat1) * sin(rLat2) - sin(rLat1) * cos(rLat2) * cos(dLon)
    rBearing = atan2(y, x)
    return (degrees(rBearing)+360)%360

def toCardinal(bearing):
    '''Converts the given bearing to one of the eight cardinal points'''
    assert bearing >= 0 and bearing <= 360

    ranges = [
        ['N',    0.0,  22.5],
        ['NE',  22.5,  67.5],
        ['E',   67.5, 112.5],
        ['SE', 112.5, 157.5],
        ['S',  157.5, 202.5],
        ['SW', 202.5, 247.5],
        ['W',  247.5, 292.5],
        ['NW', 292.5, 337.5],
        ['N',  337.5, 360.1]]

    for r in ranges:
        if bearing >= r[1] and bearing < r[2]:
            return r[0]

def cardinalBearing(lat1, lon1, lat2, lon2):
    '''
    Takes a pair of coordinates and returns the bearing as a cardinal point from
    the first pair of coordinates to the second pair of coordinates.

    Arguments:
        lat1  - Latitude of the first pair of coordinates
        lon1  - Longitude of the first pair of coordinates
        lat2  - Latitude of the second pair of coordinates
        lon2  - Longitude of the second pair of coordinates
    '''
    return toCardinal(bearing(lat1, lon1, lat2, lon2))

def strToDeg (s, mode='pure'):
    '''
    Reads a lon/lat/pure angle from the given string in the given mode and
    returns it if valid, otherwise returns None
    '''
    if mode=='lat':
        pos = '+N'
        neg = '-S'
        minimum = -90.0
        maximum = +90.0
    elif mode=='lon':
        pos = '+E'
        neg = '-W'
        minimum = -180.0
        maximum = +180.0
    else: #assume pure degrees mode
        pos = '+'
        neg = '-'
        minimum = 0.0
        maximum = 360.0
    reStart = '^[' + neg + pos + ']?'

    s = s.capitalize()
    #Check if the value is negative before stripping the sign character
    negative = s[0] in neg

    # Extract the single float value from the text
    # hdd.ddddd
    if re.match(reStart + '\d{1,3}\.\d{2,}$', s):
        if not s[0].isdigit():
            s = s[1:]
        d = float(s)
    # hdd mm.mmm
    elif re.match(reStart + '\d{1,3} [0-5]\d\.\d{2,}$', s):
        if not s[0].isdigit():
            s = s[1:]
        deg, minute = s.split(' ')
        d = float(deg) + float(minute)/60
    # hdd mm ss.s
    elif re.match(reStart + '\d{1,3} [0-5]\d [0-5]\d(\.\d+)?$', s):
        if not s[0].isdigit():
            s = s[1:]
        deg, minute, sec = s.split(' ')
        d = float(deg) + float(minute)/60 +float(sec)/360
    else:
        return None
    # Check to see if changing sign is necessary
    if negative:
        d = -d
    # Check that value is within range
    if minimum <= d <= maximum:
        return d
    else:
        return None

def strToLon (s):
    '''
    Reads a longitude from the given string and returns it if valid, otherwise
    returns None
    '''
    return strToDeg(s, 'lon')

def strToLat (s):
    '''
    Reads a latitude from the given string and returns it if valid, otherwise
    returns None
    '''
    return strToDeg(s, 'lat')

def degToStr (d, format='hdd.ddddd', mode='pure'):
    '''
    Returns the given angle in the given format using the given mode as a
    string.
    '''
    if mode=='lat':
        pos = 'N'
        neg = 'S'
        minimum = -90.0
        maximum = +90.0
    elif mode=='lon':
        pos = 'E'
        neg = 'W'
        minimum = -180.0
        maximum = +180.0
    else: #assume pure degrees mode
        pos = ''
        neg = '-'
        minimum = 0.0
        maximum = 360.0

    assert minimum <= d <= maximum

    if d < 0:
        sign = neg
    else:
        sign = pos
    d = abs(d)

    if format == 'hdd mm.mmm':
        deg = int(d)
        minute = (d -deg)*60.0
        return '%s%02i %06.3f' % (sign,deg,minute)
    elif format == 'hdd mm ss.s':
        deg = int(d)
        minute = int((d-deg)*60)
        sec = ((d-deg)*60.0-minute)*60.0
        return '%s%i %02i %04.1f' % (sign,deg,minute,sec)
    else: # assume hdd.ddddd
        return '%s%0.5f' % (sign,d)

def latToStr(d, format='hdd mm.mmm'):
    '''Returns the given latitude in the given format as a string.'''
    return degToStr(d, format=format, mode='lat')

def lonToStr(d, format='hdd mm.mmm'):
    '''Returns the given longitude in the given format as a string.'''
    return degToStr(d, format=format, mode='lon')

