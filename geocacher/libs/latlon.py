# -*- coding: UTF-8 -*-

from math import sqrt, degrees, radians, sin, cos, atan2

def distance(lat1, lon1, lat2, lon2, miles = False):
    '''
    Takes a pair of cordinates and returns the distance between them in
    Kilometers or Miles.

    Arguments:
        lat1  - Lattitude of the first pair of cordinates
        lon1  - Longitude of the first pair of cordinates
        lat2  - Lattitude of the second pair of cordinates
        lon2  - Longitude of the second pair of cordinates
    Keyword Argument:
        miles - Sets the output unit to Miles instead of Kilometers if defined
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
    Takes a pair of cordinates and returns the bearing in degrees from the
    first pair of cordinates to the second pair of cordinates.

    Arguments:
        lat1  - Lattitude of the first pair of cordinates
        lon1  - Longitude of the first pair of cordinates
        lat2  - Lattitude of the second pair of cordinates
        lon2  - Longitude of the second pair of cordinates
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
    Takes a pair of cordinates and returns the bearing as a cardinal point from
    the first pair of cordinates to the second pair of cordinates.

    Arguments:
        lat1  - Lattitude of the first pair of cordinates
        lon1  - Longitude of the first pair of cordinates
        lat2  - Lattitude of the second pair of cordinates
        lon2  - Longitude of the second pair of cordinates
    '''
    return toCardinal(bearing(lat1, lon1, lat2, lon2))

if __name__ == "__main__":
    hLat = -41-(16.301/60)
    hLon = 174+(45.461/60)
    print "Home"
    print " Lat is %0.4f, lon is %0.4f" % (hLat, hLon)

    lat = -41-(15.959/60)
    lon = 174+(45.554/60)
    print "GC1QBQC Splashing Out - Wonderful Wilton Waterfall (Wgtn)"
    print " Lat is %0.4f, lon is %0.4f" % (lat, lon)
    print "Geocaching: %0.2f, Bearing %s" % (0.65, 'N')
    print "Calculated: %0.2f, Bearing %s" % (
        distance(hLat,hLon,lat,lon),
        cardinalBearing(hLat,hLon,lat,lon))

    lat = -41-(16.581/60)
    lon = 174+(45.846/60)
    print "GC155CE The NZ InfoTech Lookout Cache (Wellington)"
    print " Lat is %0.4f, lon is %0.4f" % (lat, lon)
    print "Geocaching: %0.2f, Bearing %s" % (0.75, 'SE')
    print "Calculated: %0.2f, Bearing %s" % (
        distance(hLat,hLon,lat,lon),
        cardinalBearing(hLat,hLon,lat,lon))

    lat = -41-(18.378/60)
    lon = 174+(47.089/60)
    print "GCYJZ7 GG's Backyard (Wellington)"
    print " Lat is %0.4f, lon is %0.4f" % (lat, lon)
    print "Geocaching: %0.2f, Bearing %s" % (4.5, 'SE')
    print "Calculated: %0.2f, Bearing %s" % (
        distance(hLat,hLon,lat,lon),
        cardinalBearing(hLat,hLon,lat,lon))