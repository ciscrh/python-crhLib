# crhDebug.py -- debug and message utilities (tier 2)
# Copyright (c) 2013-2015 CR Hailey
# v1.00 crh 23-apr-13 -- initial release, using crhGV
# v1.12 crh 25-apr-13 -- revamped to use the object-based crhGV module
# v1.22 crh 30-may-13 -- provide line feed suppression option

#!/usr/local/bin/python
#

import sys
import os
import datetime
from crhGV import gv    # object holding global variables shared across modules & scripts 

## define functions

def getProgName():
    """return program name variable value"""
    
    return gv.getVar('progName')

def setProgName(name = ''):
    """set program name variable value"""
    
    if name:
        gv.setStr('progName', name)
    else:
        gv.setStr('progName', os.path.splitext(os.path.basename(sys.argv[0]))[0])

# basic debug functions
def setDbg(mode = True):
    """set debug mode"""
    
    gv.setBool('debug', mode)

def getDbg():
    """return current debug mode"""
    
    return gv.getVar('debug')

def dbgTimeStamp() :
    """return current timestamp"""
    
    return datetime.datetime.today().strftime("%H:%M:%S")

def dbgDateStamp() :
    """return current datestamp"""
    
    return datetime.datetime.today().strftime("%H:%M:%S %d-%b-%y")

# message functions
def msg(message, suppress = False, lf = True):
    """print message to stdout, possibly"""
    
    if not suppress:
        if lf:
            sys.stdout.write(message + gv.getVar('strTermChar'))
        else:
            sys.stdout.write(message)
        if gv.getVar('flush'):
            sys.stdout.flush()

def errMsg(message, suppress = False, lf = True):
    """print message to stderr, possibly"""
    
    if not suppress:
        if lf:
            sys.stderr.write(message + gv.getVar('strTermChar'))
        else:
            sys.stderr.write(message)
        if gv.getVar('flush'):
            sys.stderr.flush()

def tMsg(message, suppress = False, lf = True):
    """print status message & prepended timestamp to stdout, possibly"""
    
    msg("[{}] {}".format(dbgTimeStamp(), message), suppress, lf)

def errTMsg(message, suppress = False, lf = True):
    """print status message & prepended timestamp to stderr, possibly"""
    
    errMsg("[{}] {}".format(dbgTimeStamp(), message), suppress, lf)

def statusMsg(status, function, message, suppress = False):
    """print status message in standard format to stdout"""
    
    msg("{}-{}-{}--{}".format(status, gv.getVar('progName'), function, message), suppress)

def statusErrMsg(status, function, message, suppress = False):
    """print status message in standard format to stderr"""
    
    errMsg("{}-{}-{}--{}".format(status, gv.getVar('progName'), function, message), suppress)

# debug message functions -- include some exception handling just in case!
def dbgMsg(message, lf = True):
    """print debug message to stderr, possibly"""
    
    if getDbg():
        try:
            errMsg("debug--{}".format(message), False, lf)
        except UnicodeEncodeError:
            errMsg("debug-- dbgMsg(): unicode encode error", False, lf)
        
def dbgTMsg(message, lf = True):
    """print debug & timestamped message to stderr, possibly"""
    
    if getDbg():
        try:
            errMsg("debug--[{}] {}".format(dbgTimeStamp(), message), False, lf)
        except UnicodeEncodeError:
            errMsg("debug-- dbgTMsg(): unicode encode error", False, lf)

def dbgDMsg(message, lf = True):
    """print debug & datestamped message to stderr, possibly"""
    
    if getDbg():
        try:
            errMsg("debug--[{}] {}".format(dbgDateStamp(), message), False, lf)
        except UnicodeEncodeError:
            errMsg("debug-- dbgDMsg(): unicode encode error", False, lf)

## initialise

setProgName()   # set preferred value
setDbg(False)   # set off (default value)

## testing code

if __name__ == '__main__':
    # suppress messages
    msg('msg(1) called', 1)
    errMsg('errMsg(1) called', 1)
    tMsg('tMsg(1) called', 1)
    errTMsg('errTMsg(1) called', 1)
    statusMsg('info', 'test', 'statusMsg(1) called', 1)
    statusErrMsg('info', 'test', 'statusErrMsg(1) called', 1)
    # messages not suppressed
    msg('msg(2) called')
    errMsg('errMsg(2) called')
    tMsg('tMsg(2) called')
    errTMsg('errTMsg(2) called')
    statusMsg('info', 'test', 'statusMsg(2) called')
    statusErrMsg('info', 'test', 'statusErrMsg(2) called')
    # debug not set (debug messages suppressed)
    dbgMsg('dbgMsg(1) called')
    dbgTMsg('dbgTMsg(1) called')
    dbgDMsg('dbgMsg(1) called')
    setDbg(True)
    # debug set (debug messages not suppressed)
    dbgMsg('dbgMsg(2) called')
    dbgTMsg('dbgTMsg(2) called')
    dbgDMsg('dbgDMsg(2) called')
    # play with progName gv
    msg("progName: " + gv.getVar('progName'))
    setProgName('testName')
    msg("progName: " + getProgName())
    setProgName()
    msg("progName: " + getProgName())
