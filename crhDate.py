# crhDate.py -- date and time utilities (tier 3)
# Copyright (c) 2015 CR Hailey
# v1.01 crh 04-feb-15 -- initial release, using crhGV, crhDebug
# v1.10 crh 02-jun-15 -- Timer class, etc, removed (use crhTimer instead)

#!/usr/local/bin/python
#

import sys
import datetime as dt
from crhGV import gv    # object holding global variables shared across modules & scripts 
import crhDebug

## define variables

epoch = dt.datetime.utcfromtimestamp(0) # the start of python time

## define functions

def now():
    '''now'''

    return dt.datetime.now()

def today():
    '''today'''
    
    return dt.date.today()
    
def yesterday():
    '''yesterday'''
    
    return today() - dt.timedelta(1)
    
# date and time stamp functions
def timeStamp() :
    '''return current time stamp'''
    
    return dt.datetime.today().strftime("%H:%M:%S")

def dateStamp(dateTime = None) :
    '''return current date stamp
    or specified date date stamp'''
    
    if dateTime is None:
        return dt.datetime.today().strftime("%d-%b-%y")
    else:
        return dateTime.strftime("%d-%b-%y")

def dateTimeStamp() :
    '''return current date and time stamp'''
    
    return dt.datetime.today().strftime("%H:%M:%S %d-%b-%y")
    
# delta

def delta(date1 = None, date2 = epoch):
    '''delta time between two dates
    from epoch to today by default'''
    
    if date1 is None:
        date1 = dt.datetime.today()
    delta = date1 - date2
    return delta

def deltaDays(date1 = None, date2 = epoch):
    '''days between two dates
    from epoch to today by default'''
    
    if date1 is None:
        date1 = dt.datetime.today()
    deltaTime = delta(date1, date2)
    return deltaTime.days

def epochDeltaDays(year, month, day):
    '''days between epoch to given date'''
    
    global epoch
    deltaTime = delta(dt.datetime(year, month, day), epoch)
    return deltaTime.days

def deltaSecs(date1 = None, date2 = epoch, truncate = True):
    '''seconds between two dates
    from epoch to now by default'''
    
    if date1 is None:
        date1 = dt.datetime.now()
    deltaTime = delta(date1, date2)
    if truncate:    # remove decimal part of result
        return int(deltaTime.total_seconds())
    else:
        return deltaTime.total_seconds()
    
# helper functions

def _msgDate(message, suppress = False, lf = True):
    """print message to stderr, possibly"""
    
    if not suppress:
        if lf:
            sys.stderr.write(message + gv.getVar('strTermChar'))
        else:
            sys.stderr.write(message)
        if gv.getVar('flush'):
            sys.stderr.flush()

## initialise

## testing code

if __name__ == '__main__':
    _msgDate('Time stamp     : ' + timeStamp())
    _msgDate('Date stamp     : ' + dateStamp())
    _msgDate('Date/Time stamp: ' + dateTimeStamp())
    _msgDate('Yesterday      : ' + dateStamp(yesterday()))
    _msgDate('\nDelta days (a): ' + str(deltaDays()))
    _msgDate('Delta secs (1): ' + str(deltaSecs()))
    _msgDate('Delta secs (2): ' + str(deltaSecs(truncate = False)))
    print delta()
    _msgDate('Delta days (b): ' + str(epochDeltaDays(2015, 1, 1)))
    _msgDate('\ndatetime.date(2015, 10, 25): ' + str(dateStamp(dt.date(2015, 10, 25))))
    _msgDate('\nDelta days (1 jan - 31 dec 2015): ' + str(deltaDays(dt.date(2015, 12, 31), dt.date(2015, 1, 1))))
    _msgDate('Delta secs (31 jan - 1 feb 2015): ' + str(deltaSecs(dt.date(2015, 2, 1), dt.date(2015, 1, 31))))
