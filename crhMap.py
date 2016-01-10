# crhMap.py -- mapping utilities (tier 3)
# Copyright (c) 2015 CR Hailey
# v0.90 crh 07-may-15 -- under development
# v1.02 crh 21-may-15 -- initial release
# v1.10 crh 29-dec-15 -- wgs2osgb()accepts list/tuple argument & exceptions not always fatal
# v1.20 crh 07-jan-16 -- more constants added & names rationalised, & some functions added

# derived from BNG.py (John A Stevenson / @volcan01010 http://all-geo.org/volcan01010) &
# python functions by Hannah Fry (www.hannahfry.co.uk)

#!/usr/local/bin/python

import re
from math import floor, sqrt, pi, sin, cos, tan, atan2 as arctan2
from datetime import date
import numpy as np

from crhDebug import *

fatalException = True   # generates fatal exceptions as required if set true (default)

gridRef  = re.compile(r'^[A-Za-z]{2}(\d{4}|\d{6}|\d{8}|\d{10})$')

# region codes for 100 km grid squares
_regions=[['HL','HM','HN','HO','HP','JL','JM'],
      ['HQ','HR','HS','HT','HU','JQ','JR'],
      ['HV','HW','HX','HY','HZ','JV','JW'],
      ['NA','NB','NC','ND','NE','OA','OB'],
      ['NF','NG','NH','NJ','NK','OF','OG'],
      ['NL','NM','NN','NO','NP','OL','OM'],
      ['NQ','NR','NS','NT','NU','OQ','OR'],
      ['NV','NW','NX','NY','NZ','OV','OW'],
      ['SA','SB','SC','SD','SE','TA','TB'],
      ['SF','SG','SH','SJ','SK','TF','TG'],
      ['SL','SM','SN','SO','SP','TL','TM'],
      ['SQ','SR','SS','ST','SU','TQ','TR'],
      ['SV','SW','SX','SY','SZ','TV','TW']]

# constants used by customised wgs2osgb() & osgb2wgs() functions,
# calculate them once here instead of every time the functions are called :-)

H = 0   # third spherical coord.

# GRS80 ellipsoid (_G)...
A_G, B_G =6378137.000, 6356752.3141 # GSR80 semi-major and semi-minor axes used for WGS84 (m)
E2_G = 1- (B_G*B_G)/(A_G*A_G)   # eccentricity of the GRS80 ellipsoid
# Helmut transform (_GA, to go from GRS80 (_G) to Airy 1830 (_A))...
S = 20.4894*10**-6  # the Scale factor -1
TX_GA, TY_GA, TZ_GA = -446.448, 125.157, -542.060    # translations along x,y,z axes resp
RXS_GA,RYS_GA,RZS_GA = -0.1502, -0.2470, -0.8421 # rotations along x,y,z respectively, in seconds
RX_GA, RY_GA, RZ_GA = RXS_GA*pi/(180*3600.), RYS_GA*pi/(180*3600.), RZS_GA*pi/(180*3600.) # in radians

# Airy 1830 ellipsoid (_A)...
A_A, B_A =6377563.396, 6356256.909 # Airy semi-major and semi-minor axes used for OSGB36 (m)
E2_A = 1- (B_A*B_A)/(A_A*A_A) # eccentricity of the Airy 1830 ellipsoid
# Helmut transform (_AG, to go from Airy 1830 (_A) to GRS80 (_G))...
S = 20.4894*10**-6  # the Scale factor -1
TX_AG, TY_AG, TZ_AG = 446.448, -125.157, 542.060    # translations along x,y,z axes resp
RXS_AG, RYS_AG, RZS_AG = 0.1502, 0.2470, 0.8421 # rotations along x,y,z respectively, in seconds
RX_AG, RY_AG, RZ_AG = RXS_AG*pi/(180*3600.), RYS_AG*pi/(180*3600.), RZS_AG*pi/(180*3600.) # in radians

# UK National Grid coordinates - eastings and northings...
F0 = 0.9996012717   # scale factor on the central meridian
LAT0 = 49*pi/180    # latitude of true origin (radians)
LON0 = -2*pi/180    # longtitude of true origin and central meridian (radians)
N0, E0 = -100000, 400000    # northing & easting of true origin (m)
N_A = (A_A - B_A)/(A_A + B_A)

def wgs2osgb(lat, lon = None): # derived from WGS84toOSGB36() by Hannah Fry
    '''
    convert WGS84 latitude, longitude coordinates to OSGB36 numeric coordinates
    arguments are either pair of floats, or a double list/tuple of floats
    return double tuple of east, west integers
    does not check validity of argument values
    '''
    # check for single list or tuple, or 2 arguments
    if lon is None: # assume lat is list or tuple
        lon = lat[1]    # order matters!
        lat = lat[0]

    # convert to radians
    # these are on the wrong ellipsoid currently: GRS80. (Denoted by _G)
    lat_G = lat*pi/180
    lon_G = lon*pi/180

    nu_G = A_G/sqrt(1-E2_G*sin(lat_G)**2)

    # convert to cartesian from spherical polar coordinates
    x_G = (nu_G + H)*cos(lat_G)*cos(lon_G)
    y_G = (nu_G + H)*cos(lat_G)*sin(lon_G)
    z_G = ((1 - E2_G)*nu_G + H)*sin(lat_G)

    # perform Helmut transform (to go from GRS80 (_G) to Airy 1830 (_A))
    x_A = TX_GA + (1+S)*x_G + (-RZ_GA)*y_G + (RY_GA)*z_G
    y_A = TY_GA + (RZ_GA)*x_G+ (1 + S)*y_G + (-RX_GA)*z_G
    z_A = TZ_GA + (-RY_GA)*x_G + (RX_GA)*y_G +(1 + S)*z_G

    # back to spherical polar coordinates from cartesian
    # need some of the characteristics of the new ellipsoid
    p_A = sqrt(x_A**2 + y_A**2)

    # latitude is obtained by iteration
    lat = arctan2(z_A,(p_A*(1 - E2_A)))   # initial value
    latold = 2*pi
    while abs(lat - latold)>10**-16:
        lat, latold = latold, lat
        nu_A = A_A/sqrt(1 - E2_A*sin(latold)**2)
        lat = arctan2(z_A + E2_A*nu_A*sin(latold), p_A)

    # longitude and height are then pretty easy
    lon = arctan2(y_A,x_A)
    h = p_A/cos(lat) - nu_A

    # east, north are the UK National Grid coordinates - eastings and northings
    # meridional radius of curvature
    rho = A_A*F0*(1 - E2_A)*(1 - E2_A*sin(lat)**2)**(-1.5)
    eta2 = nu_A*F0/rho-1

    m1 = (1 + N_A + (5/4)*N_A**2 + (5/4)*N_A**3) * (lat-LAT0)
    m2 = (3*N_A + 3*N_A**2 + (21/8)*N_A**3) * sin(lat - LAT0) * cos(lat + LAT0)
    m3 = ((15/8)*N_A**2 + (15/8)*N_A**3) * sin(2*(lat - LAT0)) * cos(2*(lat + LAT0))
    m4 = (35/24)*N_A**3 * sin(3*(lat - LAT0)) * cos(3*(lat + LAT0))

    # meridional arc
    m = B_A * F0 * (m1 - m2 + m3 - m4)

    i = m + N0
    ii = nu_A*F0*sin(lat)*cos(lat)/2
    iii = nu_A*F0*sin(lat)*cos(lat)**3*(5- tan(lat)**2 + 9*eta2)/24
    iiia = nu_A*F0*sin(lat)*cos(lat)**5*(61- 58*tan(lat)**2 + tan(lat)**4)/720
    iv = nu_A*F0*cos(lat)
    v = nu_A*F0*cos(lat)**3*(nu_A/rho - tan(lat)**2)/6
    vi = nu_A*F0*cos(lat)**5*(5 - 18* tan(lat)**2 + tan(lat)**4 + 14*eta2 - 58*eta2*tan(lat)**2)/120

    north = i + ii*(lon - LON0)**2 + iii*(lon - LON0)**4 + iiia*(lon - LON0)**6
    east = E0 + iv*(lon - LON0) + v*(lon - LON0)**3 + vi*(lon - LON0)**5 

    # round down to nearest metre and return as integer value double tuple
    return (int(east), int(north))

def osgb2wgs(east, north = None):   # derived from OSGB36toWGS84() by Hannah Fry
    '''
    convert OSGB36 numeric coordinates to WGS lat, lon coordinates
    arguments are either a pair of integers, or a NGR
    return double tuple of lat, lon floats to precision of 5dp
    '''
    
    # check for single tuple or double argument
    if north is None:   # assume NGR
        (east, north) = ngr2osgb(east)
    east, north = int(east), int(north)

    # Initialise the iterative variables
    lat, m = LAT0, 0

    while north - N0 - m >= 0.00001: #Accurate to 0.01mm
        lat = (north - N0 - m)/(A_A*F0) + lat;
        m1 = (1 + N_A + (5./4)*N_A**2 + (5./4)*N_A**3) * (lat - LAT0)
        m2 = (3*N_A + 3*N_A**2 + (21./8)*N_A**3) * sin(lat - LAT0) * cos(lat + LAT0)
        m3 = ((15./8)*N_A**2 + (15./8)*N_A**3) * sin(2*(lat - LAT0)) * cos(2*(lat + LAT0))
        m4 = (35./24)*N_A**3 * sin(3*(lat - LAT0)) * cos(3*(lat + LAT0))
        #meridional arc
        m = B_A * F0 * (m1 - m2 + m3 - m4)          

    # transverse radius of curvature
    nu_A = A_A*F0/sqrt(1 - E2_A*sin(lat)**2)

    # meridional radius of curvature
    rho = A_A*F0*(1 - E2_A)*(1 - E2_A*sin(lat)**2)**(-1.5)
    eta2 = nu_A/rho-1

    secLat = 1./cos(lat)
    vii = tan(lat)/(2*rho*nu_A)
    viii = tan(lat)/(24*rho*nu_A**3)*(5+3*tan(lat)**2+eta2 - 9*tan(lat)**2*eta2)
    ix = tan(lat)/(720*rho*nu_A**5)*(61 + 90*tan(lat)**2 + 45*tan(lat)**4)
    x = secLat/nu_A
    xi = secLat/(6*nu_A**3)*(nu_A/rho+2*tan(lat)**2)
    xii = secLat/(120*nu_A**5)*(5+28*tan(lat)**2 + 24*tan(lat)**4)
    xiia = secLat/(5040*nu_A**7)*(61 + 662*tan(lat)**2 + 1320*tan(lat)**4 + 720*tan(lat)**6)
    dE = east - E0

    # these are on the wrong ellipsoid currently: Airy1830 (denoted by _A)
    lat_A = lat - vii*dE**2 + viii*dE**4 - ix*dE**6
    lon_A = LON0 + x*dE - xi*dE**3 + xii*dE**5 - xiia*dE**7

    # convert to the GRS80 ellipsoid (denoted by _G). 
    # first convert to cartesian from spherical polar coordinates
    H = 0   # third spherical coord. 
    x_A = (nu_A/F0 + H)*cos(lat_A)*cos(lon_A)
    y_A = (nu_A/F0+ H)*cos(lat_A)*sin(lon_A)
    z_A = ((1 - E2_A)*nu_A/F0 + H)*sin(lat_A)

    # Perform Helmut transform (to go from Airy 1830 to GRS80)
    x_G = TX_AG + (1 + S)*x_A + (-RZ_AG)*y_A + (RY_AG)*z_A
    y_G = TY_AG + (RZ_AG)*x_A  + (1 + S)*y_A + (-RX_AG)*z_A
    z_G = TZ_AG + (-RY_AG)*x_A + (RX_AG)*y_A + (1 + S)*z_A

    # back to spherical polar coordinates from cartesian
    # need a characteristic of the new ellipsoid    
    p_G = sqrt(x_G**2 + y_G**2)

    # lat is obtained by an iterative procedure:   
    lat = arctan2(z_G,(p_G*(1 - E2_G))) #Initial value
    latold = 2*pi
    while abs(lat - latold)>10**-16: 
        lat, latold = latold, lat
        nu_G = A_G/sqrt(1 - E2_G*sin(latold)**2)
        lat = arctan2(z_G + E2_G*nu_G*sin(latold), p_G)

    #Lon and height are then pretty easy
    lon = arctan2(y_G, x_G)
    H = p_G/cos(lat) - nu_G

    #Convert to degrees & returns floats double tuple
    lat = lat*180/pi
    lon = lon*180/pi
    return (round(lat, 5), round(lon, 5))

def osgb2ngr(coords, nDigits=6):  # based on from_osgb36() by John Stevenson
    '''
    Reformat OSGB36 numeric coordinates to British National Grid references
    return values can be 4, 6, 8 or 10 figure NGRs, as specified by the nDigits keyword

    Single double integer tuple value
    >>> osgb2ngr((327550, 672950))
    'NT276730'
 
    For multiple tuple values, use the zip function
    >>> x = [443143, 363723, 537395]
    >>> y = [1139158, 356004, 35394]
    >>> xy = zip(x, y)
    >>> osgb2ngr(xy, nDigits=4)
    ['HU4339', 'SJ6456', 'TV3735']
    '''
    if (type(coords) == list):
        return [osgb2ngr(c, nDigits=nDigits) for c in coords]
    elif type(coords)==tuple:   # input is a tuple of numeric coordinates
        x, y = coords
        x_box=np.floor(x/100000.0)  # Convert offset to index in 'regions'
        y_box=np.floor(y/100000.0)
        x_offset=100000*x_box
        y_offset=100000*y_box
        try: # Catch coordinates outside the region
            region=_regions[x_box, y_box]
        except IndexError:
            if fatalException:  # terminate program (default)
                statusErrMsg('fatal', 'crhMap.osgb2ngr()', 'invalid coordinates (outside UK region): {}'.format(str(coords)))
                exit(1)
            else:   # raise RuntimeError exception
                statusErrMsg('err', 'crhMap.osgb2ngr()', 'invalid coordinates (outside UK region): {}'.format(str(coords)))
                raise RuntimeError('crhMap.osgb2ngr() -- invalid input')
        # Format the output based on nDigits
        formats={4:'%s%02i%02i', 6:'%s%03i%03i', 8:'%s%04i%04i', 10:'%s%05i%05i'}
        factors={4:1000.0, 6:100.0, 8:10.0, 10:1.0}
        try:    # catch bad number of figures
            coords=formats[nDigits] % (region, np.floor((x - x_offset)/factors[nDigits]), np.floor((y - y_offset)/factors[nDigits]))
        except KeyError:
            if fatalException:  # terminate program (default)
                statusErrMsg('fatal', 'crhMap.osgb2ngr()', 'invalid input for nDigits: {}'.format(nDigits))
                exit(1)
            else:   # raise RuntimeError exception
                statusErrMsg('err', 'crhMap.osgb2ngr()', 'invalid input for nDigits: {}'.format(nDigits))
                raise RuntimeError('crhMap.osgb2ngr() -- invalid input')
        return coords
    else:   # invalid input
        if fatalException:  # terminate program (default)
            statusErrMsg('fatal', 'crhMap.osgb2ngr()', 'invalid input: {}'.format(str(coords)))
            exit(1)
        else:   # raise RuntimeError exception
            statusErrMsg('err', 'crhMap.osgb2ngr()', 'invalid input: {}'.format(coords))
            raise RuntimeError('crhMap.osgb2ngr() -- invalid input')

def ngr2osgb(ngr, fatal = fatalException): # based on to_osgb36() by John Stevenson
    '''
    Reformat British National Grid references to OSGB36 numeric coordinates,
    arguments can be 4, 6, 8 or 10 figure NGRs.  Returns tuples of x, y

    Single value
    >>> ngr2osgb('NT2755072950')
    (327550, 672950)

    For multiple values, use the zip function
    >>> gridrefs = ['HU431392', 'SJ637560', 'TV374354']
    >>> xy=ngr2osgb(gridrefs)
    >>> x, y = zip(*xy)
    >>> x
    (443100, 363700, 537400)
    >>> y
    (1139200, 356000, 35400)
    '''
    # check for individual coord, or list, tuple or array of ngr
    if type(ngr)==list:
        return [ngr2osgb(c) for c in ngr]
    elif type(ngr)==tuple:
        return tuple([ngr2osgb(c) for c in ngr])
    elif type(ngr)==type(np.array('string')):
        return np.array([ ngr2osgb(str(c))  for c in list(ngr) ])
    # input is grid reference...
    elif type(ngr)==str and gridRef.match(ngr):
        region=ngr[0:2].upper()
        x_box, y_box = np.where(_regions == region)
        try: # catch bad region codes
            x_offset = 100000 * x_box[0] # Convert index in 'regions' to offset
            y_offset = 100000 * y_box[0]
        except IndexError:  # terminate program (default)
            if fatalException:
                statusErrMsg('fatal', 'crhMap.ngr2osgb()', 'invalid 100km grid square code: {}'.format(ngr))
                exit(1)
            else:   # raise RuntimeError exception
                statusErrMsg('err', 'crhMap.ngr2osgb()', 'invalid 100km grid square code: {}'.format(ngr))
                raise RuntimeError('crhMap.ngr2osgb() -- invalid input')
        nDigits = (len(ngr)-2)/2
        factor = 10**(5-nDigits)
        x,y = (int(ngr[2:2 + nDigits])*factor + x_offset,
               int(ngr[2 + nDigits:2 + 2*nDigits])*factor + y_offset)
        return x, y
    else:
        if fatalException:  # terminate program (default)
            statusErrMsg('fatal', 'crhMap.ngr2osgb()', 'invalid input: {}'.format(ngr))
            exit(1)
        else:   # raise RuntimeError exception
            statusErrMsg('err', 'crhMap.ngr2osgb()', 'invalid input: {}'.format(ngr))
            raise RuntimeError('crhMap.ngr2osgb() -- invalid input')

# utility functions

def validCoords(east, north = None):
    '''
    checks if OSGB36 numeric coord values are within UK region
    return True if valid, False otherwise, but an
    unexpected exception will also give a warning status message
    '''
    if north is None:   # east supplied as tuple
        north = east[1]
        east = east[0]
    x, y = east, north
    x_box=np.floor(x/100000.0)  # Convert offset to index in 'regions'
    y_box=np.floor(y/100000.0)
    x_offset=100000*x_box
    y_offset=100000*y_box
    try: # Catch coordinates outside the region
        region=_regions[x_box, y_box]
        return True
    except IndexError:  # expected error
        return False
    except Error:   # unexpected error!
        statusErrMsg('warn', 'crhMap.validCoords()', 'invalid input: {}, {}'.format(east, north))
        return False

def validNGR(ngr):
    '''
    checks if argument is valid UK NGR
    return True if valid, False otherwise, but an
    unexpected exception will also give a warning status message
    '''
    if type(ngr) == str and gridRef.match(ngr):
        region=ngr[0:2].upper()
        x_box, y_box = np.where(_regions == region)
        try: # catch bad region codes
            x_offset = 100000 * x_box[0] # Convert index in 'regions' to offset
            y_offset = 100000 * y_box[0]
            return True
        except IndexError:  # expected error
            return False
        except Error:   # unexpected error!
            statusErrMsg('warn', 'crhMap.validNGR()', 'invalid input (1): {}'.format(ngr))
    else:   # unexpected error!
        statusErrMsg('warn', 'crhMap.validNGR()', 'invalid input (2): {}'.format(ngr))
    return False

def deg2dms(degrees):
    '''
    convert decimal degrees reading to (degrees, minutes, seconds) tuple
    argument type can be float or integer, result is always triple integer tuple
    '''
    if isinstance(degrees, int):    # special case
        return (degrees, int(0), int(0))
    negative = (degrees < 0.0)
    if negative: degrees = abs(degrees)
    decimalDeg = degrees - floor(degrees)
    minutes = decimalDeg * 60.0
    decimalMin  = minutes - floor(minutes)
    seconds = decimalMin * 60.0
    seconds = int(seconds + 0.5)

    # make some boundary adjustments, possibly [eg: to avoid returning (1, 19, 60)]
    # and convert minutes, degrees from float to integer type
    if seconds == 60:
        seconds = 0
        minutes  += 1.0
    minutes = int(minutes)
    if minutes == 60:
        minutes = 0
        degrees += 1.0
    degrees = int(degrees)

    if negative:
        return (-degrees, -minutes, -seconds)
    else:
        return (degrees, minutes, seconds)

def dms2deg(dmsTpl):
    '''
    convert (degrees, minutes, seconds) tuple to decimal degrees
    tuple element types can be float or integer, result is always a single float value
    '''
    (deg, min, sec) = dmsTpl
    (deg, min, sec) = (float(deg), abs(float(min)), abs(float(sec)))
    negative = (deg < 0.0)
    if negative: deg = abs(deg)
    decimalDeg = deg + min/60.0 + sec/3600.0
    if negative:
        return - round(decimalDeg, 4)
    else:
        return round(decimalDeg, 4)

## initialise

# codes for 100 km grid squares -- shuffle so indices correspond to offsets
_regions=np.array( [ _regions[x] for x in range(12,-1,-1) ] )
_regions=_regions.transpose()

## testing code

if __name__ == '__main__':  # add tests here
    print 'crhMap.py -- mapping utilities (tier 3)'
    print 'use crhMap-Test.py to test this module'
