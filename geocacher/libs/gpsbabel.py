# -*- coding: UTF-8 -*-

from subprocess import Popen,PIPE

class GpsCom:
    def __init__ (self, gps='garmin',port='usb:'):
        self.gps=gps
        self.port=port

    def setGps(self,gps):
        self.gps = gps

    def setPort(self,port):
        self.port = port

    def gpxToGps(self, fileName):

        p = Popen(['gpsbabel','-i','gpx','-f',fileName,'-o',self.gps,'-F',self.port],stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return p.returncode==0,stderr+stdout

    def getCurrentPos(self):
        p = Popen(['gpsbabel','-i',self.gps+',get_posn','-f',self.port],stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            blank,latStr,lonStr,name = stdout.splitlines()[1].split(' ') #@UnusedVariable
            lat = float(latStr[:-1])
            if latStr[-1:] == 'S': lat = - lat
            lon = float(lonStr[:-1])
            if lonStr[-1:] == 'W': lon = - lon
            return True, lat, lon, stderr
        else:
            return False, None, None, stderr+stdout


if __name__ == "__main__":
    gps = GpsCom()
    print gps.gpxToGps('../data/GC1P61C.gpx')
    print gps.getCurrentPos()