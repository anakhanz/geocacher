# -*- coding: UTF-8 -*-
'''
Module to build cache stats
'''
import geocacher

DAYS = [_('Monday'),
        _('Tuesday'),
        _('Wednesday'),
        _('Thursday'),
        _('Friday'),
        _('Saturday'),
        _('Sunday')]

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

CACHE_TYPES = ['Traditional Cache',
               'Ape',
               'CITO',
               'Earthcache',
               'Event Cache',
               'Maze',
               'Letterbox Hybrid',
               'Mega',
               'Multi-cache',
               'Unknown Cache',
               'Reverse',
               'Virtual Cache',
               'Webcam Cache',
               'Wherigo Cache',
               'Lost and Found Event Cache']

class cacheStats(object):
    '''
    Provides
    '''


    def __init__(self):
        '''
        Initialises the cacheStats object based on the given database and
        configuration objects.
        '''

        foundCaches = geocacher.db().getFoundCacheList()

        # initialise data tables
        self.difficultyTerrain = {}
        for difficulty in POSSIBLE_STARS:
            self.difficultyTerrain[difficulty] = {}
            for terrain in POSSIBLE_STARS:
                self.difficultyTerrain[difficulty][terrain] = 0
        self.difficultySum = 0
        self.terrainSum = 0
        self.containers = {}
        for continer in CACHE_CONTAINERS:
            self.containers[continer] = 0
        self.types = {}
        for type in CACHE_TYPES:
            self.types[type] = 0
        self.firstDate = None
        self.lastDate = None
        self.days = [0,0,0,0,0,0,0]
        self.months = [0,0,0,0,0,0,0,0,0,0,0,0]
        self.yearMonth = {}
        self.ftf = 0

        # Process individual caches
        for cache in foundCaches:
            if cache.ftf:
                self.ftf += 1
            self.difficultyTerrain[cache.difficulty][cache.terrain] += 1
            self.containers[cache.container] += 1
            self.types[cache.type] += 1
            found_date = cache.found_date
            if self.firstDate == None:
                self.firstDate = found_date
            elif self.firstDate > found_date:
                self.firstDate = found_date
            if self.lastDate == None:
                self.lastDate = found_date
            elif self.lastDate < found_date:
                self.lastDate = found_date
            self.days[found_date.weekday()] += 1
            self.months[found_date.month-1] += 1
            if found_date.year not in self.yearMonth:
                self.yearMonth[found_date.year]={}
            if found_date.month-1 not in self.yearMonth[found_date.year]:
                self.yearMonth[found_date.year][found_date.month-1] = 1
            else:
                self.yearMonth[found_date.year][found_date.month-1] += 1

        # Summary information
        self.distinct = len(foundCaches)
        self.total = self.distinct
        self.difficultyTerrain['Total'] = {}
        self.difficultyTerrain['Total']['Total'] = 0
        for difficulty in POSSIBLE_STARS:
            self.difficultyTerrain[difficulty]['Total'] = 0
            for terrain in POSSIBLE_STARS:
                self.difficultyTerrain[difficulty]['Total'] += \
                    self.difficultyTerrain[difficulty][terrain]
            self.difficultyTerrain['Total']['Total'] += \
                self.difficultyTerrain[difficulty]['Total']
            self.difficultySum += difficulty *\
                             self.difficultyTerrain[difficulty]['Total']
        for terrain in POSSIBLE_STARS:
            self.difficultyTerrain['Total'][terrain] = 0
            for difficulty in POSSIBLE_STARS:
                self.difficultyTerrain['Total'][terrain] += \
                    self.difficultyTerrain[difficulty][terrain]
            self.terrainSum += terrain * self.difficultyTerrain['Total'][terrain]

    def html(self):
        '''
        Returns the stats as a string of html.
        '''
        # Build the actual HTML
        html = '<html><head></head>\n'
        html += '<body>\n'
        html +='<h1>Statistics for %s</h1>' % geocacher.config().GCUserName
        html += '<p>Total caches %d (Distinct %d)</p>\n' % (self.total,self.distinct)
        html += '<h2>Chaching Cronology</h2>\n'
        html += '<p>First Cache found on %s</p>\n' % self.firstDate.strftime('%x')
        html += '<p>Last Cache found on %s</p>\n' % self.lastDate.strftime('%x')
        # Add Longest Streak
        # Add Longest Slump
        # Add biggest frenzy
        # Add Finds per month graph
        # Add cumulative finds per month

        html += '<h3>Days</h3>\n'
        html += '<table border=1>\n'
        for i in range(7):
            html += '<tr><td>%s</td><td>%d (%f%%)</td></tr>\n' % (DAYS[i],
                        self.days[i],
                        float(self.days[i])/float(self.total)*100.0)
        html += '</table>\n'

        html += '<h3>Months</h3>\n'
        html += '<table border=1>\n'
        for i in range(12):
            html += '<tr><td>%s</td><td>%d (%f%%)</td></tr>\n' % (MONTHS[i],
                        self.months[i],
                        float(self.months[i])/float(self.total)*100.0)
        html += '</table>\n'
        # Yearly Breakdown

        html += '<h2>Cache types</h2>\n'
        html += '<table border=1>\n'
        for type in CACHE_TYPES:
            html += '<tr><td>%s</td><td>%d (%0.1f%%)</td></tr>\n' % (type,
                        self.types[type],
                        float(self.types[type])/float(self.total)*100.0)
        html += '</table>\n'

        html += '<h2>Container types</h2>\n'
        html += '<table border=1>\n'
        for container in CACHE_CONTAINERS:
            html += '<tr><td>%s</td><td>%d (%0.1f%%)</td></tr>\n' % (container,
                        self.containers[container],
                        float(self.containers[container])/float(self.total)*100.0)
        html += '</table>\n'

        html += '<h2>Difficulty and Terrain</h2>\n'
        html += '<p>Average difficulty %0.2f</p>\n' % (float(self.difficultySum) / float(self.distinct))
        html += '<p>Average terrain %0.2f</p>\n' % (float(self.terrainSum) / float(self.distinct))

        rc = POSSIBLE_STARS + ['Total']
        html += '<p><table border=1>\n'
        html += '<tr><td></td>'
        for c in rc:
            if c == 'Total':
                html += '<td>Total</td>'
            else:
                html += '<td>%0.1f</td>' % c

        html += '</tr>\n'
        for r in rc:
            if r == 'Total':
                html += '<tr><td>Total</td>'
            else:
                html += '<tr><td>%0.1f</td>' % r

            for c in rc:
                html += '<td>%i</td>' % self.difficultyTerrain[r][c]
            html += '</tr>\n'
        html += '</table></p>\n'

        html += '</body>'
        html += '</html>'

        return html