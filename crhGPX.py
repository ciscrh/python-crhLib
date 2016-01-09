# crhGPX.py -- GPX (xml) data utilities (tier 4)
# Copyright (c) 2015 CR Hailey
# v1.00 crh 20-jun-15 -- initial release
# v1.12 crh 01-jul-15 -- cater for gpx files with no namespaces defined, etc
# v1.24 crh 19-oct-15 -- output more delta time stats, etc
# optimised for gpx files created for walks or by satnav devices on walks

#!/usr/local/bin/python

import re
import datetime
import time
from StringIO import StringIO
from lxml import etree

from crhDebug import *
from crhString import *
from crhMap import *

maxDeltaL = 400.0  # exceeding this triggers warning message (m)
maxDeltaV = 30.0   # exceeding this triggers warning message (m)
maxDeltaS = 250.0  # exceeding this triggers information message (sec)

decimalSecs = re.compile(r'\.\d+')  # used to remove decimal secs part of time stamp

class gpx(object):
    '''
    process a gpx data file
    '''
    ## class variables
    bsvHdr = 'latitude|longitude|elevation|easting|northing|ngr'    # default
    bsvHdrTime = 'latitude|longitude|elevation|timestamp|easting|northing|ngr'  # + time
    bsvHdrDelta = 'latitude|longitude|elevation|timestamp|easting|northing|ngr|deltaL|deltaV|deltaS'   # + time + deltas
    xmlDecl = '<?xml version="1.0" encoding="ASCII"?>'
    xmlNamespace = 'http://crhailey.com/gpx/crhGPX/1'   # standard value (ignored by default)
    tags = ['trkpt', 'rtept']   # possible gpx way-point element tags (track or route)
    quiet = False       # suppress some informational messages
    verbose = False     # provide additional informational messages
    tolerL = 5          # horizontal length tolerance (m) for discarding adjacent BSV record
    tolerV = 5          # vertical tolerance (m) for disregarding height gain/loss increment
    tolerT = 12         # time tolerance (sec) for discarding adjacent gpx way-point record
    precision = 8       # nat grid ref precision (6|6|10 digits)
    
    ## instance methods
    def __init__(self, inputF, time = True, delta = False, tolerT = None, tolerV = None, tolerL = None, precision = None):
        '''
        initialise object
        inputF -- gpx data file
        '''
        if tolerT is None:  # can't refer to class/instance variables in method params!
            self._tolerT = gpx.tolerT   # time tolerance (sec)
        else:
            self._tolerT = tolerT
        if tolerV is None:
            self._tolerV = gpx.tolerV   # vertical tolerance (m)
        else:
            self._tolerV = tolerV
        if tolerL is None:
            self._tolerL = gpx.tolerL   # horizontal length tolerance (m)
        else:
            self._tolerL = tolerL
        if precision is None:
            self._precision = gpx.precision   # nat grid ref precision
        else:
            self._precision = precision
        self.mxDeltaL = maxDeltaL  # way-point length delta trigger (m)
        self.mxDeltaV = maxDeltaV  # way-point height delta trigger (m)
        self.mxDeltaS = maxDeltaS  # way-point time delta trigger (sec)
        self._xml = None    # input xml document tree
        self._root = None   # root element (<gpx>) of _xml
        self._namespace = None  # required namespace from root element of _xml
        self._timeTags = True   # time tags processed
        self._stats = {}    # summary route statistics
        self._tag = None    # current route way-point element tag used
        self._wayPts = []   # list of (lat, lon, elev, ts) tuples generated from way-point elements
        self._bsvs = []     # list of bsvs
        self._deltas = []   # list of (deltaL, deltaV, deltaS) tuples generated from way-point elements
        self._time = time   # process time data if present in gpx document
        self._delta = delta
        self._gpxName = None    # gpx document name tag value, if present
        self._gpxDesc = None    # gpx document desc tag value, if present
        self._importGPX(inputF)
        self._setWayPts()
        if self.validData():
            self._setElevs()

    def validData(self):
        '''
        returns True if valid data present
        '''
        return not self._wayPts == []

    def genXML(self, pretty = True, bsv = True, track = True, xmlns = None):
        '''
         return xml document as StringIO instance
         pretty -- generate pretty output (default: True)
         bsv    -- generate compact xml document based on BSV data
         track  -- create track (default) or route gpx document (bsv only)
         xmlns  -- add xmlns attribute to document root (ignore by default)
                   (standard value if True, custom value if text, ignore if False or None)
        '''
        if bsv:
            return self._genXML(pretty = pretty, track = track, xmlns = xmlns)
        else:
            statusErrMsg('info', 'gpx.genXML()', 'track switch ignored for gpx file xml', gpx.quiet)
            xmlDecl = gpx.xmlDecl + '\n'
            xmlDoc = StringIO()
            xmlDoc.write(xmlDecl)
            errMsg('>> create xml document from {} way-points...\n'.format(self._stats['nr']), gpx.quiet)
            self._xml.write(xmlDoc, pretty_print = pretty)
            return xmlDoc

    def genStats(self):
        '''
        generate route statistics & return as StringIO instance
        '''
        statsDoc = StringIO()
        errMsg('>> create route statistics...\n', gpx.quiet)
        statsDoc.write('GPX way-points processed  :{:6}\n'.format(self._stats['nr']))
        if not self._time:
            statsDoc.write('Way-points discarded (t)  : n/a\n')
        elif self._timeTags and 'discardT' in self._stats:
            statsDoc.write('Way-points discarded (t)  :{:6}\n'.format(self._stats['discardT']))
            statsDoc.write('Way-points retained       :{:6}\n'.format(self._stats['nr'] - self._stats['discardT']))
        if self._stats['bsvDup'] is not None:
            statsDoc.write('Duplicate BSVs discarded  :{:6}\n'.format(self._stats['bsvDup']))
            statsDoc.write('BSVs retained             :{:6}\n'.format(self._stats['bsvNr']))
        statsDoc.write('Distance                  :{:9.2f}km\n'.format(self._stats['dist']))
        statsDoc.write('Max length delta          :{:8.1f}m\n'.format(self._stats['deltaL']))
        if self._stats['deltaV'] is None:
            statsDoc.write('Max vertical delta        : n/a\n')
        else:
            statsDoc.write('Max vertical delta        :{:+8.1f}m\n'.format(self._stats['deltaV']))
        if self._stats['deltaS'] is None:
            statsDoc.write('Max time delta            : n/a\n')
        else:
            statsDoc.write('Max time delta            :{:8.1f}sec\n'.format(self._stats['deltaS']))
        if 'vi' in self._stats:
            statsDoc.write('Height increments ignored :{:6}\n'.format(self._stats['vi']))
        else:
            statsDoc.write('Height increments ignored : n/a\n')
        if self._stats['up'] is None:
            statsDoc.write('Adjusted height gain      : n/a\n')
        else:
            statsDoc.write('Adjusted height gain      :{:6}m\n'.format(self._stats['up']))
        if self._stats['dn'] is None:
            statsDoc.write('Adjusted height loss      : n/a\n')
        else:
            statsDoc.write('Adjusted height loss      :{:6}m\n'.format(self._stats['dn']))
        if self._stats['start'] is None:
            statsDoc.write('Start way-point elevation : n/a\n')
        else:
            statsDoc.write('Start way-point elevation :{:8.1f}m\n'.format(self._stats['start']))
        if self._stats['end'] is None:
            statsDoc.write('End way-point elevation   : n/a\n')
        else:
            statsDoc.write('End way-point elevation   :{:8.1f}m\n'.format(self._stats['end']))
        if self._stats['hi'] is None:
            statsDoc.write('High way-point elevation  : n/a\n')
        else:
            statsDoc.write('High way-point elevation  :{:8.1f}m\n'.format(self._stats['hi']))
        if self._stats['lo'] is None:
            statsDoc.write('Low way-point elevation   : n/a\n')
        else:
            statsDoc.write('Low way-point elevation   :{:8.1f}m\n'.format(self._stats['lo']))
        if self._stats['start'] < self._stats['end']:
            statsDoc.write('Net height gain           :{:8.1f}m\n'.format(round(self._stats['end'] - self._stats['start'], 1)))
        elif self._stats['end'] < self._stats['start']:
            statsDoc.write('Net height loss           :{:8.1f}m\n'.format(round(self._stats['start'] - self._stats['end'], 1)))
        if self._stats['endX'] is not None:
            diffL = int(sqrt(1.0 * ((self._stats['endX'] - self._stats['startX'])**2 + (self._stats['endY'] - self._stats['startY'])**2)))
            if diffL > 999:
                diffL = round(0.001 * diffL, 2)
                statsDoc.write('Start-end separation (gpx):{:9.2f}km\n'.format(diffL))
            else:
                statsDoc.write('Start-end separation (gpx):{:6}m\n'.format(diffL))
        if self._time:
            if self._stats['startTs'] is None:
                statsDoc.write('Start timestamp           : n/a\n')
            else:
                statsDoc.write('Start timestamp           : {}\n'.format(self._stats['startTs']))
            if self._stats['endTs'] is None:
                statsDoc.write('End timestamp             : n/a\n')
            else:
                statsDoc.write('End timestamp             : {}\n'.format(self._stats['endTs']))
                if not self._stats['startTs'] is None:
                    startTs = self._stats['startTs'][:19]   # remove end of string beyond integer seconds
                    endTs = self._stats['endTs'][:19]       # remove end of string beyond integer seconds
                    startDT = datetime.datetime.strptime(startTs, '%Y-%m-%dT%H:%M:%S')
                    endDT = datetime.datetime.strptime(endTs, '%Y-%m-%dT%H:%M:%S')
                    statsDoc.write('Elapsed time (H:M:S)      : {}\n'.format(endDT - startDT))
        if gpx.verbose:
            statsDoc.write('\n')
            if not self._gpxName is None:
                statsDoc.write('GPX xml name tag          : {}\n'.format(self._gpxName))
            if not self._gpxDesc is None:
                statsDoc.write('GPX xml desc tag          : {}\n'.format(self._gpxDesc))
            statsDoc.write('Max Delta L (BSV)         :{:8.1f}m\n'.format(self.mxDeltaL))
            statsDoc.write('Max Delta V (elevation)   :{:8.1f}m\n'.format(self.mxDeltaV))
            statsDoc.write('Max Delta S (time)        :{:8.1f}sec\n'.format(self.mxDeltaS))
            if self._stats['up'] is not None:
                statsDoc.write('Reported height gain      :{:6}m\n'.format(self._stats['upAbs']))
            if self._stats['dn'] is not None:
                statsDoc.write('Reported height loss      :{:6}m\n'.format(self._stats['dnAbs']))
            statsDoc.write('Precision (NGR)           :{:6} digits\n'.format(self._precision))
            statsDoc.write('Tolerance L (BSV)         :{:6}m\n'.format(self._tolerL))
            statsDoc.write('Tolerance V (cumulative)  :{:6}m\n'.format(self._tolerV))
            statsDoc.write('Tolerance T (way-point)   :{:6}sec\n'.format(self._tolerT))
        return statsDoc

    def genBSV(self, precision = None, tolerL = None):
        '''
        generate BSV records & return as StringIO instance
        precision -- ngr precision (6|8|10)
        tolerL    -- length tolerance (m) for discarding duplicate BSVs
        '''
        if precision is not None:
            self._precision = precision
        if tolerL is not None:
            self._tolerL = tolerL
        bsvDoc = StringIO()
        bsvLst = self._getBSVlst()
        if self._delta:
            deltaLst = self._deltas
        errMsg('>> create {} bsv records...\n'.format(self._stats['bsvNr']), gpx.quiet)
        if self._delta:
            bsvDoc.write(gpx.bsvHdrDelta + '\n')
        elif self._time:
            bsvDoc.write(gpx.bsvHdrTime + '\n')
        else:
            bsvDoc.write(gpx.bsvHdr + '\n')
        for line in bsvLst:
            bsvDoc.write(line +'\n')
        self._bsvDoc = bsvDoc
        return bsvDoc

    def getStats(self):
        '''
        return copy of _stats
        '''
        return self._stats.copy()

    ## private methods
    def _importGPX(self, inputF):
        '''
        import gpx data from file
        '''
        # lxml element names use Clark notation (ie: {namespace}elementName)
        
        try:
            self._xml = etree.parse(inputF)
        except etree.XMLSyntaxError as e:
            statusErrMsg('fatal', 'gpx._importGPX()', 'malformed XML: {}'.format(e.error_log))
            exit(1)
        self._root = self._xml.getroot()
        if self._root.nsmap:    # namespace map (well, dictionary really)
            self._namespace = str(self._root.nsmap[None])
        else:   # empty dictionary
            statusErrMsg('info', 'gpx._importGPX()', 'no namespaces defined in gpx file')
            self._namespace = ''
        nsTagTrack = '{' + self._namespace + '}trk'   # for gpx docs describing tracks
        nsTagRoute = '{' + self._namespace + '}rte'   # for gpx docs describing routes
        nsTagName = '{' + self._namespace + '}name'
        nsTagDesc = '{' + self._namespace + '}desc'
        # retrieve name and description for later use, assume <trk> tag used
        for child in self._root.iterchildren(nsTagTrack):
            for grandchild in child.iterchildren(nsTagName, nsTagDesc):
                if grandchild.tag == nsTagName:
                    self._gpxName = grandchild.text
                if grandchild.tag == nsTagDesc:
                    self._gpxDesc = grandchild.text
            errMsg('name1  = {}'.format(self._gpxName))
            errMsg('desc1  = {}'.format(self._gpxDesc))
        # try again with <rte> tag if name not found
        if not hasattr(self, '_gpxName'):
            for child in self._root.iterchildren(nsTagRoute):
                for grandchild in child.iterchildren(nsTagName, nsTagDesc):
                    if grandchild.tag == nsTagName:
                        self._gpxName = grandchild.text
                    if grandchild.tag == nsTagDesc:
                        self._gpxDesc = grandchild.text
            errMsg('name2  = {}'.format(self._gpxName))
            errMsg('desc2  = {}'.format(self._gpxDesc))

    def _setWayPts(self):
        '''
        retrieve all <ele> & <time> (possibly) tag values, lat/lon attributes, convert them to float values,
        populate the _wayPts list with (lat, lon, elev, ts) tuples 
        & the deltas list with (deltaL, deltaV, deltaS) tuples
        '''
        nsTag1 = '' # way-point tag determined below
        nsTag2 = '{' + self._namespace + '}ele'
        nsTag3 = '{' + self._namespace + '}time'
        nsTag4 = '{' + self._namespace + '}name'
        nsTag5 = '{' + self._namespace + '}desc'
        hPrev = ePrev = nPrev = tPrev = secsPrev = pt = discardT = 0
        deltaV = deltaL = distance = 0.0
        self._stats['nr'] = 0
        self._stats['deltaL'] = 0.0
        self._stats['deltaV'] = None
        self._stats['deltaS'] = None
        self._stats['startTs'] = None
        self._stats['endTs'] = None
        self._stats['startX'] = None
        self._stats['endX'] = None
        self._stats['startY'] = None
        self._stats['endY'] = None
        start = True
        tsCount = 0
        tagOK = False
        if gpx.verbose:
            if self._time and self._tolerT:
                errMsg('gpx file way-point time tolerance = {} sec'.format(self._tolerT))
            elif self._time:
                errMsg('gpx file way-point time tolerance disabled')
            else:
                errMsg('gpx file time tags ignored')
        # first determine which way-point tag used in gpx file
        for tag in gpx.tags:  # try possible tags
            self._tag = tag
            nsTag1 = '{' + self._namespace + '}' + self._tag
            wayPts = self._xml.getiterator(nsTag1)
            for wayPt in wayPts:    # check if tag found
                tagOK = True
                break
            if tagOK:
                break
            else:
                statusErrMsg('info', 'gpx._setWayPts()', 'no <{}> elements found'.format(self._tag), gpx.quiet)
        if not tagOK:   # none of tags worked
            statusErrMsg('error', 'gpx._setWayPts()', 'unable to parse gpx file')
            return False
        wayPts = self._xml.getiterator(nsTag1)  # start again
        for wayPt in wayPts:    # parse the gpx file
            self._stats['nr'] += 1
            lat = float(wayPt.get('lat'))
            lon = float(wayPt.get('lon'))
            try:
                elev = float(wayPt.findtext(nsTag2))
            except TypeError as te:  # assume no <ele> element
                elev = None
            if self._time:
                try:
                    ts = decimalSecs.sub('', wayPt.findtext(nsTag3))  # remove decimal part of seconds from time stamp
                    secs = self._seconds(ts)
                    if self._tolerT and not start:
                        deltaT = secs - tPrev
                        if deltaT >= self._tolerT:
                            tPrev = secs
                        else:   # discard reading (time interval too low)
                            discardT += 1
                            continue
                    tsCount += 1
                except TypeError as te:  # assume no <time> element
                    ts = None
                    secs = None
            else:
                ts = None
            self._wayPts.append((lat, lon, elev, ts))
            ht = elev
            pt += 1
            if start:
                self._stats['startTs'] = ts
                start = False
            else:
                self._stats['endTs'] = ts
            # generate way-point deltas & route length as well
            (east, north) = wgs2osgb(lat, lon)
            if (ePrev == 0) and (nPrev == 0):   # first value
                self._stats['startX'] = east
                self._stats['startY'] = north
                ePrev = east
                nPrev = north
                hPrev = ht
                secsPrev = secs
                if gpx.verbose and self._delta:
                    if (ht is None) and (ts is None):
                        errMsg('way-point {:5.0f}: deltaL {:5.1f}m'.format(pt, 0.0))
                    elif ht is None:
                        errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaS {:4.0f}sec'.format(pt, 0.0, 0.0))
                    elif ts is None:
                        errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaV {:+7.1f}m'.format(pt, 0.0, 0.0))
                    else:
                        errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaV {:+7.1f}m, deltaS {:4.0f}'.format(pt, 0.0, 0.0, 0.0))
                self._deltas.append((None, None, None))
                continue
            self._stats['endX'] = east
            self._stats['endY'] = north
            deltaL = sqrt(1.0 * ((east - ePrev)**2 + (north - nPrev)**2))
            if not ((ht is None) and (hPrev is None)):
                deltaV = round(ht - hPrev, 1)
                if self._stats['deltaV'] is None:
                    self._stats['deltaV'] = deltaV
                elif (abs(deltaV) > abs(self._stats['deltaV'])): 
                    self._stats['deltaV'] = deltaV
            else:
                deltaV = None
            if not ((secs is None) and (secsPrev is None)):
                deltaS = secs - secsPrev
                if self._stats['deltaS'] is None:
                    self._stats['deltaS'] = deltaS
                elif (deltaS > self._stats['deltaS']): 
                    self._stats['deltaS'] = deltaS
            else:
                deltaS = None
            distance += deltaL
            deltaL = round(deltaL, 1)
            if deltaL > self._stats['deltaL']:
                self._stats['deltaL'] = deltaL
            ePrev = east
            nPrev = north
            hPrev = ht
            secsPrev = secs
            self._deltas.append((deltaL, deltaV, deltaS))
            if gpx.verbose and self._delta:
                if (deltaV is None) and (deltaS is None):
                    errMsg('way-point {:5.0f}: deltaL={:5.1f}m'.format(pt, deltaL))
                elif deltaV is None:
                    errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaS {:4.0f}sec'.format(pt, deltaL, deltaS))
                elif deltaS is None:
                    errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaV {:+7.1f}sec'.format(pt, deltaL, deltaV))
                else:
                    errMsg('way-point {:5.0f}: deltaL {:5.1f}m, deltaV {:+7.1f}m, deltaS {:4.0f}sec'.format(pt, deltaL, deltaV, deltaS))
            # highlight potential delta errors
            if deltaL > self.mxDeltaL:
                statusErrMsg('warn', 'gpx._setWayPts()', 'way-point {:5} generating large delta length ({}m, {}m)'.format(pt, int(deltaL), int(distance)))
            if (deltaV is not None) and (abs(deltaV) > self.mxDeltaV):
                statusErrMsg('warn', 'gpx._setWayPts()', 'way-point {:5} generating large delta height ({:+2}m, {}m)'.format(pt, int(deltaV), int(elev)))
            if (deltaS is not None) and (deltaS > self.mxDeltaS):
                statusErrMsg('info', 'gpx._setWayPts()', 'way-point {:5} generating large delta time ({}sec, {})'.format(pt, int(deltaS), ts))

        if self._tolerT:
            self._stats['discardT'] = discardT
        self._stats['dist'] = round(distance / 1000.0, 2)
        if self._wayPts == []:  # should not be triggered
            statusErrMsg('fatal', 'gpx._setWayPts()', 'no <{}> elements found'.format(self._tag))
            exit(1)
        elif self._time and (tsCount == 0):
            statusErrMsg('warn', 'gpx._setWayPts()', 'no <time> elements found')
            self._timeTags = False
            return False
        return True

    def _getWayPtBSV(self, wayPt, deltas = None):
        '''
        wayPt     -- way-point data tuple (lat, lon, elev  ts)
        precision -- ngr precision (6|8|10 digits)
        deltas    -- delta value information tuple, or None
        calculate & return a bsv record for a wayPt
        '''
        (lat, lon, elev, ts) = wayPt
        if deltas is not None:
            (deltaL, deltaV, deltaS) = deltas
        else:
            (deltaL, deltaV) = (None, None)
        (east, north) = wgs2osgb(lat, lon)
        ngr = osgb2ngr((east, north), self._precision)
        if (elev is None) and self._time and (ts is None):
            bsvRcd = '{:+010.5f}|{:+010.5f}|||{}|{}|{}'.format(lat, lon, east, north, ngr)
        elif (elev is None) and time:
            bsvRcd = '{:+010.5f}|{:+010.5f}||{}|{}|{}|{}'.format(lat, lon, ts, east, north, ngr)
        elif (ts is None) and self._time:
            bsvRcd = '{:+010.5f}|{:+010.5f}|{:+07.1f}||{}|{}|{}'.format(lat, lon, elev, east, north, ngr)
        else:
            bsvRcd = '{:+010.5f}|{:+010.5f}|{:+07.1f}|{}|{}|{}|{}'.format(lat, lon, elev, ts, east, north, ngr)
        if deltas is None:  # deltas not required
            return bsvRcd
        if deltaL is None:
            bsvRcd += '|'
        else:
            bsvRcd += '|{:04}'.format(int(deltaL))
        if deltaV is None:
            bsvRcd += '|'
        else:
            bsvRcd += '|{:+04}'.format(int(round(deltaV, 0)))
        if deltaS is None:
            bsvRcd += '|'
        else:
            bsvRcd += '|{:04}'.format(int(deltaS))
        return bsvRcd

    def _getBSVlst(self):
        '''
        generate & return list of BSV records from document
        precision -- ngr precision (6|8|10 digits, giving 100|10|1m precision)
        tolerL    -- length tolerance (m) for discarding duplicate readings
        '''
        tolerL = self._tolerL   # might need to temporarily set tolerL to 0
        prevEastNorth = (1, 1)  # suitable nonsense initial value
        dupCount = 0
        bsvLst = []
        if self._delta and tolerL:
            statusErrMsg('warn', 'gpx._getBSVlst()', 'length tolerance mode disabled')
            tolerL = 0  # _tolerL not affected :-)
        if gpx.verbose:
            if tolerL:
                errMsg('bsv ngr precision = {}; bsv length tolerance = {}m'.format(self._precision, tolerL))
            else:
                errMsg('bsv ngr precision = {}; bsv length tolerance disabled'.format(self._precision))
        for idx in range(0, len(self._wayPts)):
            if self._delta:
                bsvLst.append(self._getWayPtBSV(self._wayPts[idx], self._deltas[idx]))
            elif tolerL:
                (lat, lon, elev, ts) = self._wayPts[idx]
                (east, north) = wgs2osgb(lat, lon)
                if abs(east - prevEastNorth[0]) + abs(north - prevEastNorth[1]) > tolerL:
                    bsvLst.append(self._getWayPtBSV(self._wayPts[idx]))
                    prevEastNorth = tuple([east, north])
                else:   # discard (near) duplicate bsv record
                    dupCount += 1
                    continue
            else:
                bsvLst.append(self._getWayPtBSV(self._wayPts[idx]))
        if tolerL:
            statusErrMsg('info', 'gpx._getBSVlst()', '{} duplicate bsv records discarded)'.format(dupCount), gpx.quiet)
            self._stats['bsvDup'] = dupCount
            self._stats['bsvNr'] = self._stats['nr'] - self._stats['discardT'] - dupCount
        else:
            self._stats['bsvDup'] = None
            self._stats['bsvNr'] = self._stats['nr']

        self._bsvs = bsvLst[:]
        return bsvLst
        
    def _setElevs(self):
        '''
        retrieve all <ele> tag values, convert them to float values & set _stats
        '''
        noneCount = ignoreCount = 0
        self._stats['start'] = None
        self._stats['end'] = None
        self._stats['up'] = 0.0
        self._stats['dn'] = 0.0
        self._stats['hi'] = 0.0
        self._stats['lo'] = 0.0
        self._stats['upAbs'] = 0.0
        self._stats['dnAbs'] = 0.0
        if 'bsvDup' not in self._stats:
            self._stats['bsvDup'] = None
        prevElev = None
        if gpx.verbose:
            if self._tolerV:
                errMsg('gpx vertical tolerance = {}m'.format(self._tolerV))
            else:
                errMsg('height tolerance mode disabled')
        for wayPt in self._wayPts:
            elev = wayPt[2]
            if elev is None:
                print ' elev is None'
                noneCount += 1
                continue
            if prevElev is None:    # first value
                self._stats['hi'] = elev
                self._stats['lo'] = elev
                self._stats['start'] = elev
                prevElev = elev
                prevElevAbs = elev
            else:
                deltaV = elev - prevElev
                deltaVAbs = elev -prevElevAbs
#                errMsg('prevElev, elev, upAbs, dnAbs, deltaV = {}, {}, {}, {}, {}'.format(prevElev, elev, self._stats['upAbs'], self._stats['dnAbs'], deltaV))
                if deltaVAbs > 0:
                    self._stats['upAbs'] += deltaVAbs
                elif deltaVAbs < 0:
                    self._stats['dnAbs'] -= deltaVAbs
                prevElevAbs = elev
                if self._stats['hi'] < elev:
                    self._stats['hi'] = elev
                elif self._stats['lo'] > elev:
                    self._stats['lo'] = elev
                if deltaV > self._tolerV:
                    self._stats['up'] += deltaV
                    prevElev = elev
                elif deltaV < - self._tolerV:
                    self._stats['dn'] -= deltaV
                    prevElev = elev
                elif deltaV != 0:
                    ignoreCount += 1
                
            self._stats['end'] = elev
        if noneCount == self._stats['nr']:  # no elevations
            statusErrMsg('warn', 'gpx._setElevs()', 'no <ele> elements present', gpx.quiet)
            self._stats['up'] = None
            self._stats['dn'] = None
            self._stats['hi'] = None
            self._stats['lo'] = None
            self._stats['upAbs'] = None
            self._stats['dnAbs'] = None
        else:
            self._stats['up'] = int(round(self._stats['up'], 0))
            self._stats['dn'] = int(round(self._stats['dn'], 0))
            self._stats['vi'] = ignoreCount
            self._stats['upAbs'] = int(round(self._stats['upAbs'], 0))
            self._stats['dnAbs'] = int(round(self._stats['dnAbs'], 0))

    def _genXML(self, pretty = True, track = True, xmlns = None):
        '''
         return xml document based on BSV data as StringIO instance
         pretty -- generate pretty output (default: True)
         track  -- create track (default) or route gpx document
         xmlns  -- add xmlns attribute to document root
        '''
        if gpx.verbose:
            if track:
                errMsg('generate track gpx document from BSVs')
            else:
                errMsg('generate route gpx document from BSVs')
        xmlDecl = gpx.xmlDecl + '\n'
        if (xmlns is None) or (xmlns is False): # ignore
            gpxBSV = etree.Element('gpx', version = '1.0', creator = 'crhGPX')
        elif xmlns is True: # standard value
            gpxBSV = etree.Element( 'gpx', xmlns = gpx.xmlNamespace, version = '1.0', creator = 'crhGPX')
        else:   # custom text
            gpxBSV = etree.Element( 'gpx', xmlns = xmlns, version = '1.0', creator = 'crhGPX')
        xmlDoc = etree.ElementTree(gpxBSV)
        if track:
            trkRte = etree.SubElement(gpxBSV, 'trk')
        else:
            trkRte = etree.SubElement(gpxBSV, 'rte')
        if hasattr(self, '_gpxName') and self._gpxName is not None:
            trkRteName =etree.SubElement(trkRte, 'name')
            trkRteName.text = self._gpxName
        if hasattr(self, '_gpxDesc') and self._gpxDesc is not None:
            trkRteDesc =etree.SubElement(trkRte, 'desc')
            trkRteDesc.text = self._gpxDesc
        if track:
            segment = etree.SubElement(trkRte, 'trkseg')
        if len(self._bsvs):
            bsvLst = self._bsvs[:]
        else:
            bsvLst = self._getBSVlst()
        for bsv in bsvLst:
            bsvFlds = bsv.split('|')
            if track:
                point = etree.SubElement(segment, 'trkpt', lat = bsvFlds[0], lon = bsvFlds[1])
            else:
                point = etree.SubElement(trkRte, 'rtept', lat = bsvFlds[0], lon = bsvFlds[1])
            elevation = etree.SubElement(point, 'ele')
            elevation.text = bsvFlds[2]
            if track and self._time and (bsvFlds[3] != ''):
                time = etree.SubElement(point, 'time')
                time.text = bsvFlds[3]
        doc = StringIO()
        doc.write(xmlDecl)
        errMsg('>> create gpx document from {} BSVs...\n'.format(len(bsvLst)), gpx.quiet)
        xmlDoc.write(doc, pretty_print = pretty)
        return doc

    def _seconds(self, gpxTime):
        '''
        gpxTime -- gpx <time> element string
        return time in seconds (integer) for comparative purposes, etc
        '''
        ts = gpxTime[:19]  # remove end of string beyond seconds digits
        ts = ts.replace('T', ' ')
        ts = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        return int(time.mktime(ts.timetuple()))
        
## initialise

## testing code
# (testing handled by crhGPX-test.py)

if __name__ == '__main__':
    text = '2015-06-08T09:56:51.9531659+01:00'
    ts = text[:19]  # remove end of string beyond seconds digits
    ts = ts.replace('T', ' ')
    ts = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
    secs = int(time.mktime(ts.timetuple()))
    print text
    print ts
    print secs
