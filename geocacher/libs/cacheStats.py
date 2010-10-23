# -*- coding: UTF-8 -*-
'''
Module to build cache stats
'''
import datetime

import geocacher
from geocacher.libs.iso3166 import country2code
from geocacher.libs.latlon import latToStr, lonToStr

if __name__ == "__main__":
    def _(s):
        return s

DAYS = [_('Sunday'),
        _('Monday'),
        _('Tuesday'),
        _('Wednesday'),
        _('Thursday'),
        _('Friday'),
        _('Saturday')]

MONTHS = [_('January'),
          _('February'),
          _('March'),
          _('April'),
          _('May'),
          _('June'),
          _('July'),
          _('August'),
          _('September'),
          _('October'),
          _('November'),
          _('December')]

POSSIBLE_STARS = [1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0]

CACHE_CONTAINERS = ['Micro',
                    'Small',
                    'Regular',
                    'Large',
                    'Not chosen',
                    'Virtual',
                    'Other']

CACHE_TYPES = {'Traditional Cache': [_('Traditional'), 2],
               'Multi-cache': [_('Multi'), 3],
               'Ape': [_('Project A.P.E.'), 7],
               'Unknown Cache': [_('Mystery'), 8],
               'Letterbox Hybrid': [_('Letterbox'), 5],
               'Wherigo Cache': [_('Wherigo'), 1858],
               'Event Cache': [_('Event'), 6],
               'Mega': [_('Mega Event'), 453,],
               'CITO': [_('CITO'), 13],
               'Earthcache': [_('Earth'), 137],
               'Maze': [_('Maze'), 1304],
               'Virtual Cache': [_('Virtual'), 4],
               'Webcam Cache': [_('Webcam'), 11],
               #'10 Years Event Cache': [_('10 Years! Event Cache'), , 'type = ""'],
               'Reverse': [_('Reverse'), 12],
               }

class cacheStats(object):
    '''
    Provides
    '''

    def __init__(self):
        '''
        Initialises the cacheStats object based on the given database and
        configuration objects.
        '''
        self.userName = geocacher.config().GCUserName
        self.userId = geocacher.config().GCUserID

        cur = geocacher.db().cursor()
        cur.execute('SELECT COUNT(id) From Caches WHERE found = 1')
        self.found =  cur.fetchone()[0]


    def html(self):

        date = datetime.date.today().strftime(geocacher.config().dateFormat)
        title = '%s has %d Finds' % (self.userName, self.found)
        html =  """<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
<html>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />
"""
        html += """<title>%s</title>\n""" % title
        html += """</head>\n"""
        html += """<body>\n"""
        html += """<div align='center' style='width:770px;  background: #dedeee; font-family: Verdana, Arial, sans-serif; font-size: 12px; color: black; margin: 1px; border: outset; line-height: normal;'>
\n"""

        html += """<span style='font-family: Tahoma, Arial, sans-serif; font-size: 16px; font-weight: bold;'>\n"""
        html += """%s\n""" % title
        html += """</span>\n"""
        html += """<br />\n"""
        html += """<br />Statistics generated on %s\n""" % date
        html += """<br /><br />\n"""
        html += self.numbers()
        html += self.milestones()
        html += self.twoUp(self.findsByType(), self.findsByContainer())
        html += self.twoUp(self.findsByDifficulty(), self.findsByTerrain())
        html += self.findsByTerrainDifficulty()
        html += self.twoUp(self.findsByBearing(), self.avgDistanceByBearing())
        html += self.twoUp(self.findsByWeekday(), self.findsByMonth())
        html += self.twoUp(self.findsByYear(), self.findsByYearPlaced())
        html += self.findsPerDay()


        html += """</div>\n"""
        html += """</body></html>\n"""
        return html

    def twoUp(self, left, right):
        html = """<table border='0'>\n"""
        html += """<tr>\n"""
        html += """<td valign='top'>\n"""
        html += left
        html += """</td>"""
        html += """<td valign='top'>\n"""
        html += right
        html += """</td>"""
        html += """</tr>"""
        html += """</table>"""
        return html


    def findsByBearing(self):
        cur = geocacher.db().cursor()
        cur.execute('SELECT bearing, COUNT(bearing) AS cnt FROM (SELECT bearing(lat, lon) AS bearing FROM Caches WHERE found = 1) GROUP BY bearing')
        data = {}
        for row in cur.fetchall():
            data[row[0]] = [row[1], row[1]]
        html = self.titleNarrow('Finds by Bearing')
        html += self.radarChart(data, 0)
        html += """<br /><br />\n"""
        return html

    def avgDistanceByBearing(self):
        if geocacher.config().imperialUnits:
            unit =' mi'
        else:
            unit = ' km'
        cur = geocacher.db().cursor()
        cur.execute('SELECT bearing, COUNT(bearing) AS cnt, SUM(distance) AS totdist FROM (SELECT bearing(lat, lon) AS bearing, distance(lat, lon) AS distance FROM Caches WHERE found = 1) GROUP BY bearing')
        data = {}
        for row in cur.fetchall():
            value = row[2]/float(row[1])
            data[row[0]] = [value, '%0.1f%s' % (value, unit)]
        html = self.titleNarrow('Average Distance by Bearing')
        html += self.radarChart(data, '0'+unit)
        html += """<br /><br />\n"""
        return html

    def findsByContainer(self):
        cur = geocacher.db().cursor()
        cur.execute('SELECT container, COUNT(container) AS cnt FROM Caches WHERE found = 1 GROUP BY container ORDER  BY container')
        data =  cur.fetchall()
        html = self.titleNarrow('Finds by Container')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByDifficulty(self):
        cur = geocacher.db().cursor()
        cur.execute('SELECT difficulty, COUNT(difficulty) AS cnt FROM Caches WHERE found = 1 GROUP BY difficulty ORDER  BY difficulty')
        data =  cur.fetchall()
        html = self.titleNarrow('Finds by Difficulty Rating')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByMonth(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT month, count(month) FROM (SELECT  STRFTIME('%m',found_date) AS month FROM Caches WHERE found = 1) GROUP BY month ORDER BY month")
        data = []
        for row in cur.fetchall():
            data.append([MONTHS[int(row[0])-1], row[1]])
        html = self.titleNarrow('Finds by Month')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByTerrain(self):
        cur = geocacher.db().cursor()
        cur.execute('SELECT terrain, COUNT(terrain) AS cnt FROM Caches WHERE found = 1 GROUP BY terrain ORDER BY terrain')
        data =  cur.fetchall()
        html = self.titleNarrow('Finds by Terrain Rating')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByTerrainDifficulty(self):
        cur = geocacher.db().cursor()
        html = self.titleWide('Difficulty / Terrain Chart')
        html += '<table>\n'
        html += '<tr>\n'
        html += self.hrCell('')
        html += self.hrCell ('Terrain', colspan=10, align='center')
        html += '<tr/>\n'
        html += '<tr>\n'
        html += self.hrCell('Difficulty', rowspan=10, align='center')
        html += self.tCell('')
        ttotals = {}
        combinations = 0
        hard = 0
        for tstar in POSSIBLE_STARS:
            html += self.tCell('<b>%0.1f</b>' % tstar, width=60, align='center')
            ttotals[tstar]=0
        html += "<td width='60'></td>\n"
        html += '</tr>\n'
        for dstar in POSSIBLE_STARS:
            dtotal = 0
            html += '<tr>\n'
            html += self.tCell('<b>%0.1f</b>' % dstar, width=60, align='center')
            for tstar in POSSIBLE_STARS:
                cur.execute("SELECT COUNT(id) AS cnt FROM Caches WHERE found = 1 AND difficulty = ? AND terrain = ?", (dstar, tstar,))
                value = cur.fetchone()[0]
                if value == 0:
                    html += self.cCell('', width=60, align='center')
                else:
                    html += self.cCell('%i' % value, width=60, align='center')
                    dtotal += value
                    ttotals[tstar] += value
                    combinations += 1
                    if dstar >=3.0 or tstar >= 3.0:
                        hard += value
            html += self.tCell('%i' % dtotal, width=60, align='center')
            html += '</tr>\n'
        html += '<tr>\n'
        html += "<td width='60'></td>\n"
        html += "<td width='60'></td>\n"
        for tstar in POSSIBLE_STARS:
            html += self.tCell('%i' % ttotals[tstar], width=60, align='center')
        html += '</tr>\n'
        html += '</table>'
        html += '<br /><i><b>%i</b> (%i%%) Difficulty / Terrain combinations found, out of <b>81</b>\n' % (combinations, (combinations * 100)/81)
        html += '<br /><b>%i</b> (%0.2f%%) finds were rated with Diff or Terr of 3 or greater</i>\n' % (hard, (float(hard)/float(self.found))*100.0)
        html += '<br /><br />\n'
        return html

    def findsByType(self):
        cur = geocacher.db().cursor()
        cur.execute('SELECT type, COUNT(type) AS cnt FROM Caches WHERE found = 1 GROUP BY type ORDER BY cnt DESC')
        rows =  cur.fetchall()
        html = self.titleNarrow('Finds by Type')
        #html += self.pieGraph(data)
        data = []
        maxVal = 0
        for row in rows:
            data.append([('%s %s' % (self.cacheIcon(row[0]), CACHE_TYPES[row[0]][0])),
                         row[1]])
            if row[1] > maxVal:
                maxVal = row[1]
        html += self.horizTable(data, maxVal, 130)
        html += """<br /><br />\n"""
        return html

    def horizTable(self, data, maxVal, maxLength, pool=None):
        if pool is None:
            pool = self.found
        html = "<table border='0' summary='' width='375' style='text-align: left;'>\n"
        html += "<tr>\n"
        html += self.hrCell('&nbsp;')
        html += self.hrCell('Number')
        html += self.hrCell('Percent')
        html += self.hrCell('&nbsp;')
        html += "<tr>\n"
        for row in data:
            title = row[0]
            value = row[1]
            percentage = (float(value)/float(pool)) * 100
            if value == maxVal:
                color = 'red'
            else:
                color = 'blue'
            html += "<tr>\n"
            html += self.tCell(title)
            html += self.cCell('%i' % value)
            html += self.cCell("% 0.2f %%" % percentage)
            html += self.cCell(self.chartBar(value, maxVal, maxLength, color, False, 15), maxLength)
            html += "</tr>\n"
        html += "</table>"

        return html

    def findsByWeekday(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT weekday, count(weekday) FROM (SELECT  STRFTIME('%w',found_date) AS weekday FROM Caches WHERE found = 1) GROUP BY weekday ORDER BY weekday")
        data = []
        for row in cur.fetchall():
            data.append([DAYS[int(row[0])], row[1]])
        html = self.titleNarrow('Finds by Weekday')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByYear(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT year, count(year) FROM (SELECT  STRFTIME('%Y',found_date) AS year FROM Caches WHERE found = 1) GROUP BY year ORDER BY year")
        data = cur.fetchall()
        html = self.titleNarrow('Finds by Year')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsByYearPlaced(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT year, count(year) FROM (SELECT  STRFTIME('%Y',placed) AS year FROM Caches WHERE found = 1) GROUP BY year ORDER BY year")
        data = cur.fetchall()
        html = self.titleNarrow('Finds by Year Placed')
        html += self.pieGraph(data)
        html += """<br /><br />\n"""
        return html

    def findsPerDay(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT MAX(finds) FROM (SELECT COUNT(found_date) as finds from Caches WHERE found = 1 GROUP BY found_date)")
        maxFinds = cur.fetchone()[0]
        cur.execute("SELECT MAX(cnt) FROM (SELECT COUNT(finds) AS cnt FROM (SELECT COUNT(found_date) as finds from Caches WHERE found = 1 GROUP BY found_date) GROUP BY finds)")
        maxCount = cur.fetchone()[0]
        chd = []
        chxl0 = []
        chxl2 = []
        for finds in range(1, maxFinds+1):
            cur.execute("SELECT COUNT(finds) AS cnt FROM (SELECT COUNT(found_date) as finds from Caches WHERE found = 1 GROUP BY found_date) WHERE finds = ?", (finds, ))
            chd.append(str((cur.fetchone()[0]*100)/maxCount))
            chxl0.append(str(finds))
            if finds == maxFinds/2:
                chxl2.append('Caches%20Found%20In%20a%20Day')
            else:
                chxl2.append('')
        if maxCount % 5 == 0:
            axisMax = maxCount
        else:
            axisMax = (maxCount/5 +1) * 5
        tickSpacing = (100/float(axisMax))*2.5
        html = self.titleWide('Finds per Day')
        html += "<img src='http://chart.apis.google.com/chart?cht=bvs&chs=740x300"
        html += "&chxs=0,,9|1,,9" # axis label format
        html += "&chbh=a" # Bar width use all avaliable
        html += "&chco=0044BB" # Bar colours
        html += "&chf=bg,s,dedeee" # Background fill
        html += "&chg=0,%0.1f,3,3,0,0" % tickSpacing
        html += "&chxt=x,y,x" # use x,y labels
        html += "&chxr=1,0,%i,5" % axisMax
        html += "&chd=t:" + ",".join(chd) # chart labels
        html += "&chxl=0:|" + "|".join(chxl0) + "|2:|" + "|".join(chxl2) # data series labels
        html += "&chdl=Number%20of%20times%20finds/day%20has%20been%20achieved"
        html += "&chdlp=t' />"
        return html

    def milestones(self):
        cur = geocacher.db().cursor()
        cur.execute("SELECT code, found_date FROM Caches WHERE found = 1 ORDER BY found_date")
        rows = cur.fetchall()
        dateFormat = geocacher.config().dateFormat
        html = self.titleWide('Milestones')
        html += "<table width='750' style='text-align: left;'>\n"
        html += "<tr>\n"
        html += self.hrCell('Milestone')
        html += self.hrCell('Date')
        html += self.hrCell('Interval')
        html += self.hrCell('&nbsp;')
        html += self.hrCell('Code')
        html += self.hrCell('&nbsp;')
        html += self.hrCell('Cache Name')
        html += "</tr>\n"
        row, prevDate = self.mileStoneRow(rows[0][0], 1)
        html += row
        index = 100
        numFound = len(rows)
        while index < numFound:
            row, prevDate =  self.mileStoneRow(rows[index][0], index, prevDate)
            html += row
            index += 100
        row, prevDate = self.mileStoneRow(rows[numFound-1][0], numFound, prevDate)
        html += row
        html += "</table>\n"
        firstDay = rows[0][1].date()
        lastDay = rows[numFound-1][1].date()
        elapsedDays = (lastDay - firstDay).days +1
        elapsedRate = float(numFound)/float(elapsedDays)
        cur.execute("SELECT COUNT(*) FROM (SELECT DISTINCT DATE(found_date) FROM Caches WHERE found = 1)")
        cacheDays = cur.fetchone()[0]
        cacheRate = float(numFound)/float(cacheDays)
        elapsedNext = roundUp((index - numFound)/elapsedRate)
        cacheNext = roundUp((index - numFound)/cacheRate)
        nextDate = lastDay + datetime.timedelta(days=elapsedNext)
        html += "<i><br />%s should reach <b>%i</b> finds in <b>%i</b> days (<b>%i</b> Caching days) on <b>%s</b> </i><br />\n" % (self.userName, index, elapsedNext, cacheNext, nextDate.strftime(geocacher.config().dateFormat))
        index += 100
        elapsedNext = roundUp((index - numFound)/elapsedRate)
        cacheNext = roundUp((index - numFound)/cacheRate)
        nextDate = lastDay + datetime.timedelta(days=elapsedNext)
        html += "and <b>%i</b> finds in <b>%i</b> days (<b>%i</b> Caching days) on <b>%s</b> </i><br />\n" % (index, elapsedNext, cacheNext, nextDate.strftime(geocacher.config().dateFormat))
        html += """<br /><br />\n"""
        return html

    def mileStoneRow(self, code, milestone, prevDate=None):
        cache = geocacher.db().getCacheByCode(code)
        curDate = cache.found_date.date()
        if prevDate is None:
            interval = ''
        else:
            interval = '%i days' % (curDate - prevDate).days
        html = "<tr>\n"
        html += self.tCell("<b>%i</b>" % milestone, align='right')
        html += self.cCell("<A href='http://www.geocaching.com/seek/log.aspx?LID=%i'>%s</a>" %
                            (cache.own_log_id,
                             cache.found_date.strftime(geocacher.config().dateFormat)))
        html += self.cCell(interval, align='right')
        html += self.cCell(self.flag(cache.country))
        html += self.cCell(self.cacheLink(cache.code))
        html += self.cCell(self.cacheIcon(cache.type))
        html += self.tCell(cache.name)
        html += "</tr>\n"
        return html, curDate


    def numbers(self):
        cur = geocacher.db().cursor()
        dateFormat = geocacher.config().dateFormat
        html = self.titleWide('Some Numbers')
        html += "<table width='750' style='text-align: left;'>\n"
        html += "<col width='250px' />\n"
        html += "<tr>\n"
        html += self.tCell("Overall Total Finds:")
        html += self.cCell("<b>%i</b> finds</td>\n" % (self.found,))
        html += "</tr>\n"
        cur.execute("SELECT COUNT(ftf) as ftfs from Caches WHERE ftf = 1 GROUP BY ftf")
        html += "<tr>\n"
        html += self.tCell("Total FTF's:")
        html += self.cCell("<b>%i</b>" % cur.fetchone()[0])
        html += "</tr>\n"
        cur.execute("SELECT MAX(finds) FROM (SELECT COUNT(found_date) as finds from Caches WHERE found = 1 GROUP BY found_date)")
        html += "<tr>\n"
        html += self.tCell("Most Caches Found in a Day:")
        html += self.cCell("<b>%i</b>" % cur.fetchone()[0])
        html += "</tr>\n"
        cur.execute("SELECT distance(lat, lon) AS distance, name, code, country FROM Caches WHERE found = 1 ORDER BY distance ASC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Nearest Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatDist(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT distance(lat, lon) AS distance, name, code, country FROM Caches WHERE found = 1 ORDER BY distance DESC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Furtherst Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatDist(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT lat, name, code, country FROM Caches WHERE found = 1 ORDER BY lat DESC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Most Northerly Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatLat(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT lat, name, code, country FROM Caches WHERE found = 1 ORDER BY lat ASC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Most Southerly Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatLat(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT lon, name, code, country FROM Caches WHERE found = 1 ORDER BY lon DESC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Most Easterly Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatLon(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT lon, name, code, country FROM Caches WHERE found = 1 ORDER BY lon ASC")
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Most Westerly Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (self.formatLon(row[0]), row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT strftime(?, placed), name, code, country FROM Caches WHERE found = 1 ORDER BY placed ASC",
                    (dateFormat,))
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Oldest Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (row[0], row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute("SELECT strftime(?, placed), name, code, country FROM Caches WHERE found = 1 ORDER BY placed DESC",
                    (dateFormat,))
        row = cur.fetchone()
        html += "<tr>\n"
        html += self.tCell("Youngest Cache Found:")
        html += self.cCell("<b>%s</b>, %s %s %s" % (row[0], row[1], self.cacheLink(row[2]), self.flag(row[3])))
        html += "</tr>\n"
        cur.execute('SELECT COUNT(id) From Caches WHERE found = 1 AND archived = 1')
        archived =  cur.fetchone()[0]
        html += "<tr>\n"
        html += self.tCell("Caches found which are now archived:")
        html += self.cCell("<b>%i</b>, (%0.2f %%)" % (archived, (float(archived)/float(self.found))*100))
        html += "</tr>\n"
        cur.execute("SELECT found_date FROM Caches WHERE found = 1 ORDER BY found_date")
        data = cur.fetchall()
        slump = 0
        slumpStart = None
        slumpEnd = None
        streak = 1
        curStreak = 1
        streakStart = None
        streakEnd = None
        previous = None
        timeDiff = None
        for row in data:
            current = row[0].date()
            if previous is None:
                #Special case for first row
                curStreakStart = current
                streakStart = current
                streakEnd = current
            else:
                # all other rows
                timeDiff = (current - previous).days
                # Slump
                if timeDiff > slump:
                    slump = timeDiff
                    slumpStart = previous
                    slumpEnd = current
                # Streak
                if timeDiff == 1:
                    #Add a day to the Streak
                    curStreak += 1
                elif timeDiff != 0:
                    # Streak broken
                    if curStreak > streak:
                        # New Longest streak (ended on prevous item)
                        streak = curStreak
                        streakStart = curStreakStart
                        streakEnd = previous
                    # Reset current streak
                    curStreak = 1
                    curStreakStart = current
            previous = current
        html += "<tr>\n"
        html += self.tCell("Longest Streak:")
        html += self.cCell("<b>%i</b> consecutive days with a find from %s to %s" % (
            streak, streakStart.strftime(dateFormat), streakEnd.strftime(dateFormat)))
        html += "</tr>\n"
        html += "<tr>\n"
        html += self.tCell("Longest Slump:")
        html += self.cCell("<b>%i</b> consecutive days without a find from %s to %s" % (
            slump, slumpStart.strftime(dateFormat), slumpEnd.strftime(dateFormat)))
        html += "</tr>\n"
        html += "</table>\n"
        html += "<br /><br />\n"

        return html


    def pieGraph(self, data):
        chdl = []
        chll = []
        chcol = []
        for row in data:
            label = row[0]
            percent = float(row[1])/float(self.found)*100
            chdl.append('%0.1f' % percent)
            chll.append('%s (%0.1f%%)' % (label, percent))

        c1 = '8080f0'
        c2 = '2020f0'
        cmax = 'ff0000'
        mn, mx = self.findMinMaxPos(data)
        odd = True
        for i in range(0,len(data)):
            if i == mx:
                chcol.append(cmax)
            else:
                if odd:
                    chcol.append(c1)
                else:
                    chcol.append(c2)
                odd = not odd

        chd = ",".join(chdl)
        chl = "|".join(chll)
        chco = ",".join(chcol)

        chart = "<img src='http://chart.apis.google.com/chart?cht=p3&chs=375x120&chf=bg,s,dedeee"
        chart += "&chd=t:" + chd + "&chl=" + chl + "&chco=" + chco + "' />"

        return chart

    def radarChart(self, data, defaultLable):
        chdl = []
        chxll = []
        for b in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            if b not in data.keys():
                data[b] = [0, defaultLable]
            chxll.append(b + ' (' + str(data[b][1]) + ')')
        for b in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']:
            chdl.append('%0.1f' % float(data[b][0]))
        chd = ",".join(chdl)
        chxl = "|".join(chxll)

        chart = "<img src='http://chart.apis.google.com/chart?cht=r&chs=260x220&chco=0000FF"
        chart += "&chls=3,3,0&chxt=x&chxr=0,0.0,360.0"
        chart += "&chm=B,76A4FB80,0,0,0|h,808080,0,0.9,1|h,808080,0,0.5,1"
        chart += "&chf=bg,s,dedeee"
        chart += "&chd=t:" + chd + "&chxl=0:|" + chxl
        chart += "' />"
        return chart

    def chartBar(self, value, maxVal, maxLengh, color='green', vertical=False, thickness=15):
        barLength = (value * maxLengh) / maxVal
        if barLength == 0 and value > 0:
            barLength = 1
        if vertical:
            barImage = "http://wallace.gen.nz/geocacher/stats/%s-v.png" % color
            return "<img src='%s' border='0' width='%i' height='%i' alt='%i' title='%i' />" % (barImage, thickness, barLength, value, value)
        else:
            barImage = "http://wallace.gen.nz/geocacher/stats/%s-h.png" % color
            return "<img src='%s' border='0' width='%i' height='%i' alt='%i' title='%i' />" % (barImage, barLength, thickness, value, value)

    def findMinMaxPos(self, data):
        mn = 0
        mx = 0
        for i in range(1,len(data)):
            if data[mn][1] > data[i][1]:
                mn = i
            if data[mx][1] < data[i][1]:
                mx = i
        return (mn, mx)

    def flag(self, country):
        return("<img align ='top' vspace='1'  alt='%s' title='%s' src='http://wallace.gen.nz/geocacher/stats/flags/%s.png'/>" % (country, country, country2code(country).lower()))

    def cacheIcon(self, cacheType):
        return("<img align='top' src='http://www.geocaching.com/images/wpttypes/sm/%i.gif' />" % CACHE_TYPES[cacheType][1])

    def titleNarrow(self, t):
        return self.title(t, 375)

    def titleWide(self, t):
        return self.title(t, 750)

    def formatDist(self, distance):
        if geocacher.config().imperialUnits:
            if distance < 1.0:
                return '%i yd' % int(distance * 1760)
            else:
                return '%0.2f mi' % distance
        else:
            if distance < 1.0:
                return '%i m' % int(distance * 1000)
            else:
                return '%0.2f km' % distance

    def formatLat(self, lat):
        return latToStr(lat, geocacher.config().coordinateFormat)

    def formatLon(self, lon):
        return lonToStr(lon, geocacher.config().coordinateFormat)

    def title(self, t, width):
        html = """<div style='width:%ipx; background: #666699; font-weight: bold; line-height: 20px; font-size: 13px; color: white; border: 1px solid #000000;   text-align: center;; '>\n""" % width
        html += t
        html += """</div><br />\n"""
        return html

    def hrCell(self, content, width=None, height=None, rowspan=None, colspan=None, align=None):
        return self.cell("<b>%s</b>" % content, 'C8C8DD', width, height, rowspan, colspan, align)

    def tCell(self, content, width=None, height=None, rowspan=None, colspan=None, align=None):
        return self.cell(content, 'CCCCD4', width, height, rowspan, colspan, align)

    def cCell(self, content, width=None, height=None, rowspan=None, colspan=None, align=None):
        return self.cell(content, 'BABADD', width, height, rowspan, colspan, align)

    def cell(self, content, background, width=None, height=None, rowspan=None, colspan=None, align=None):
        ret = "<td style='background: #%s;'" % background
        if width is not None:
            assert type(width) is int
            assert width >= 0
            ret += " width='%i'" % width
        if height is not None:
            assert type(height) is int
            assert height >= 0
            ret += " height='%i'" % height
        if colspan is not None:
            assert type(colspan) is int
            assert colspan >= 1
            ret += " colspan='%i'" % colspan
        if rowspan is not None:
            assert type(rowspan) is int
            assert rowspan >= 1
            ret += " rowspan='%i'" % rowspan
        if align is not None:
            assert align in ['left', 'center', 'right']
            ret += " align='%s'" % align
        ret += " >%s</td>\n" %content
        return ret

    def cacheLink(self, cache):
        return """<a href="http://coord.info/%s">%s</a>""" % (cache, cache)

if __name__ == "__main__":
    import os.path
    import webbrowser
    path = os.path.abspath('test.html')
    stats = cacheStats()
    fid = open(path,"w")
    fid.write(stats.html())
    fid.close()
    webbrowser.open(path)
