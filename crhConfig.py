# crhConfig.py -- configuration file utilities (tier 3)
# Copyright (c) 2014-2015 CR Hailey
# v1.00 crh 17-jun-14 -- initial release
# v1.12 crh 25-jun-14 -- provide means to specify ini file name as argument

#!/usr/local/bin/python

import ConfigParser as cp
import os
from crhDebug import *

## essential constants & variables

cfgIniFile = getProgName() + '.ini'
config = cp.SafeConfigParser()

## functions

# do not call this function if argparse called in main program!
def getIniFile(defaultIniFile = cfgIniFile):
    '''override default config ini file name using argparse
assumes argparse not called in main program (it falls over)'''
    
    import argparse
    iniFileParser = argparse.ArgumentParser(description = 'get config ini filename')
    iniFileParser.add_argument('-i', '--inifile', action = 'store', dest = 'inifile',
                help = 'config ini file name')
    iniArgs = iniFileParser.parse_args()
    if iniArgs.inifile:
        return iniArgs.inifile
    else:
        return defaultIniFile

## extend SafeConfigParser class

class crhConfigParser(object, cp.SafeConfigParser):

    def __init__(self):
        '''initiate instance'''

        cp.SafeConfigParser.__init__(self)
        self._quiet = False

    def _bool(self, value):
        '''extends function bool()'''

        if isinstance(value, str):
            if value.lower() in ['yes', 'on', 'true', '1']:
                return True
            else:
                return False
        else:
            return bool(value)
            
    def setQuiet(self, status = True):
        '''quiet status of True reduces informational messages issued by instance methods
returns the status before the method was called'''
    
        oldState = self._quiet
        self._quiet = status
        return oldState

    def getQuiet(self):
        '''return the current quiet status'''

        return self._quiet

    def readFile(self, progIni = cfgIniFile):
        '''read and process the config ini file
return True if successful, False otherwise'''

        if not os.path.exists(progIni):
            statusErrMsg('Info', 'crhConfigParser.readFile()', 'Config file not found: {}'.format(progIni), self._quiet)
        elif not os.path.isfile(progIni):
            statusErrMsg('Warn', 'crhConfigParser.readFile()', 'Invalid config file: {}'.format(progIni), self._quiet)
        else:
            try:
                self.read(progIni)
                statusErrMsg('Info','crhConfigParser.readFile()', 'Sections: [{0}]'.format(", ".join(str(i) for i in self.sections())), self._quiet)
                return True
            except Exception as e:
                print e
                statusErrMsg('Warn', 'crhConfigParser.readFile()', 'Unable to initialise config file: {}'.format(progIni), self._quiet)
        return False

    def getOption(self, section, option, defaultValue = None):
        '''return the option value, or the default value if it does not exist'''

        if self.has_option(section, option):
            return self.get(section, option)
        else:
            return defaultValue

    def getStr(self, section, option, defaultValue = None):
        '''return the option value as a string, or the default value if it does not exist'''

        if self.has_option(section, option):
            return str(self.get(section, option))
        else:
            return str(defaultValue)

    def getInt(self, section, option, defaultValue = None):
        '''Return the option value as an integer, or None if unable to comply'''

        if self.has_option(section, option):
            if self.get(section, option) =='':
                return None
            try:
                return self.getint(section, option)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getInt()', "Unable to set option value '{}'".format(self.getOption(section, option, defaultValue)), self._quiet)
                if defaultValue is None:
                    return None
                try:
                    return int(defaultValue)
                except Exception as e:
                    print e
                    statusErrMsg('Error', 'crhConfigParser.getInt()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)
        else:
            if defaultValue is None:
                return None
            try:
                return int(defaultValue)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getInt()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)

    def getFlt(self, section, option, defaultValue):
        '''Return the option value as a floating point number, or None if unable to comply'''
 
        if self.has_option(section, option):
            if self.get(section, option) =='':
                return None
            try:
                return self.getfloat(section, option)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getFlt()', "Unable to set option value '{}'".format(self.getOption(section, option, defaultValue)), self._quiet)
                if defaultValue is None:
                    return None
                try:
                    return float(defaultValue)
                except Exception as e:
                    print e
                    statusErrMsg('Error', 'crhConfigParser.getFlt()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)
        else:
            if defaultValue is None:
                return None
            try:
                return float(defaultValue)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getFlt()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)

    def getBool(self, section, option, defaultValue):
        '''Return the option value as a boolean, or None if unable to comply'''
 
        if self.has_option(section, option):
            if self.get(section, option) =='':
                return None
            try:
                return self.getboolean(section, option)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getBool()', "Unable to set option value '{}'".format(self.getOption(section, option, defaultValue)), self._quiet)
                if defaultValue is None:
                    return None
                try:
                    return self._bool(defaultValue)
                except Exception as e:
                    print e
                    statusErrMsg('Error', 'crhConfigParser.getBool()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)
        else:
            if defaultValue is None:
                return None
            try:
                return self._bool(defaultValue)
            except Exception as e:
                print e
                statusErrMsg('Error', 'crhConfigParser.getBool()', "Unable to set default option value '{}'".format(defaultValue), self._quiet)

## initialise

## testing code
if __name__ == '__main__':
    print 'crhConfig tests...\n'
    # add tests here

    cfg = crhConfigParser()
    cfg.readFile('crhConfig.ini')
#    cfg.setQuiet()
    a = 'a'
    a = cfg.getOption('constants', 'A', a)
    msg('a: {}'.format(a))
    b = 'b'
    b = cfg.getOption('constants', 'B', b)
    msg('b: {}'.format(b))
    c = 'c'
    c = cfg.getOption('constants', 'C', c)
    msg('c: {}'.format(c))
    d = 'd'
    d = cfg.getOption('constants', 'D', d)
    msg('d: {}'.format(d))
    e = 'e'
    e = cfg.getOption('constants', 'E', e)
    msg('e: {}'.format(e))

    one = cfg.getInt('integers', 'one', 11)
    msg('one: {}'.format(one))
    two = cfg.getInt('integers', 'two', 12)
    msg('two: {}'.format(two))
    three = cfg.getInt('integers', 'three', 13)
    msg('three: {}'.format(three))
    four = cfg.getInt('integers', 'four', 14)
    msg('four: {}'.format(four))
    five = cfg.getInt('integers', 'five', 'fifteen')
    msg('five: {}'.format(five))

    flt1 = cfg.getFlt('floats', 'oneFlt', 11.)
    msg('flt1: {}'.format(flt1))
    flt2 = cfg.getFlt('floats', 'twoFlt', 12)
    msg('flt2: {}'.format(flt2))
    flt3 = cfg.getFlt('floats', 'threeFlt', 13)
    msg('flt3: {}'.format(flt3))
    flt4 = cfg.getFlt('floats', 'fourFlt', 14.0)
    msg('flt4: {}'.format(flt4))
    flt5 = cfg.getFlt('floats', 'fiveFlt', 15)
    msg('flt5: {}'.format(flt5))
    flt6 = cfg.getFlt('floats', 'sixFlt', 'sixteen')
    msg('flt6: {}'.format(flt6))

    bool1 = cfg.getBool('booleans', 'onBool', True)
    msg('bool1: {}'.format(bool1))
    bool2 = cfg.getBool('booleans', 'offBool', False)
    msg('bool2: {}'.format(bool2))
    bool3 = cfg.getBool('booleans', 'oneBool', 'no')
    msg('bool3: {}'.format(bool3))
    bool4 = cfg.getBool('booleans', 'zeroBool', 'yes')
    msg('bool4: {}'.format(bool4))
    bool5 = cfg.getBool('booleans', 'trueBool', 1)
    msg('bool5: {}'.format(bool5))
    bool6 = cfg.getBool('booleans', 'falseBool', 0)
    msg('bool6: {}'.format(bool6))
    bool7 = cfg.getBool('booleans', 'yesBool', 'on')
    msg('bool7: {}'.format(bool7))
    bool8 = cfg.getBool('booleans', 'noBool', 'off')
    msg('bool8: {}'.format(bool8))
    bool9 = cfg.getBool('booleans', 'diddly', 'false')
    msg('bool9: {}'.format(bool9))
    bool10 = cfg.getBool('booleans', 'emptyBool', 'no')
    msg('bool10: {}'.format(bool10))
