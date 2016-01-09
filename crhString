# crhString.py -- string functions (tier 1)
# Copyright (c) 2013-2015 CR Hailey
# coding: latin-1
# v0.91 crh 22-apr-13 -- under development
# v1.06 crh 29-mar-14 -- initial release

#!/usr/local/bin/python
#

import sys
import collections
import unicodedata

## essential variables

## define functions
def singural(nr, singleStr, pluralStr, preStr = '', postStr = ''):
    '''
    return string with required singular/plural case
    nr        -- number (integer)
    singleStr -- string used if nr = 1|-1, placed after nr
    pluralStr -- string used in all other cases, placed after nr
    preStr    -- string placed before nr (default = '')
    postStr   -- string placed after singleStr/pluralStr (default = '')
    '''
    if (nr == 1) or (nr == -1):
        return preStr + str(nr) + singleStr + postStr
    else:
        return preStr + str(nr) + pluralStr + postStr


def trueFalse(test, trueStr, falseStr, preStr = '', postStr = ''):
    '''
    return string with required true/false case
    test     -- evaluated as True or False
    trueStr  -- string used if test True
    falseStr -- string used if test False
    preStr   -- string placed before trueStr|falseStr (default = '')
    postStr  -- string placed after trueStr|falseStr (default = '')
    '''
    if test:
        return preStr + trueStr + postStr
    else:
        return preStr + falseStr + postStr

def prettyStr(text, escape = False):
    '''
    return text as string with non-printable characters removed
    '''
    pretty = ''
    for char in str(text):
        if (char >= ' ') and (char <= '~'):
            pretty += char
#        elif char == "poundsign":
#            pretty += "poundsign"
        elif escape:
            if char == "\t":
                pretty += r'\t'
            elif char == "\n":
                pretty += r'\n'
            elif char == "\r":
                pretty += r'\r'
        else:
            if (char == "\t") or (char == "\n") or (char == "\r"):
                pretty += char
    return pretty

def listStr(lst):
    '''
    return simply formatted string of list items
    eg: ['one','two','three'] --> 'one, two, three'
    note items do not have to be strings or lst a list :-)
    '''
    if isinstance(lst, basestring):
        return lst
    try:
        iterator = iter(lst)
    except TypeError:
        return str(lst)
    else:
        listStr = ''
        for item in lst:
            listStr += str(item) + ', '
        return listStr[0:-2]

def us2Spc(text):
    '''
    convert double underscores in text  to single space & return result
    '''
    return text.replace('__', ' ')

def pad(text, width, padChar = ' ', left = True):
    '''
    pad  (not justify))text to give specified width
    '''
    if type(text) != type('111'):
        text = str(text)
    padLen = width - len(text)
    if padLen > 0:  # work to do
        if left: return text.rjust(width, padChar)
        else: return text.ljust(width, padChar)
    else: return text

def zeroPadNr(nr, width):
    '''
    return string padded number with leading zeros as required
    '''
    strNr = ''
    if type(nr) == type('111'):
        strNr = nr
        nr = int(nr)
    elif type(nr) == type(111):
        strNr = str(nr)
    else:   # neither int nor string
        return ''
    if len(strNr) > width:
        return ''
    formatStr = '{:0' + str(width) + 'd}'
    return formatStr.format(nr)
    
def bsvTuple(bsvStr):
    '''
    return tuple of fields extracted from bsv string
    '''
    return tuple(bsvStr.rstrip('\n').split('|'))

def csvTuple(csvStr):
    '''
    return tuple of fields extracted from csv string
    beware: does not correctly handle quoted values with embedded commas
    '''
    return tuple(csvStr.rstrip('\n').split(','))

def parseDate(dateStr, strict = False):
    '''
    convert candidate date string into standard format (YYYY-MM-DD)
    more relaxed on what is a valid date string if strict mode not invoked.
    includes many checks but doesn't trap everything (eg: 2014-02-30 accepted)
    '''
    month = 1   # not strict: assumed value if not present
    day = 1 # not strict: assumed value if not present

    try:
        if not type(dateStr) == type('111'):
            raise ValueError    # guard against accepting numbers or numeric expressions
        if '-' in dateStr:  # (YYYY[-MM[-DD]])
            cmpnts = dateStr.split('-')
            if (len(cmpnts) > 3) or (strict and len(cmpnts < 3)):
                raise ValueError
            if len(cmpnts[0]) > 4: raise ValueError
            year = int(cmpnts[0])
            if len(cmpnts) == 3:
                if len(cmpnts[2]) > 2: raise ValueError
                day = int(cmpnts[2])
            if len(cmpnts) >= 2:
                if len(cmpnts[1]) > 2: raise ValueError
                month = int(cmpnts[1])
        elif ' ' in dateStr: # (YYYY[ MM[ YY]])
            cmpnts = dateStr.split(' ')
            if (len(cmpnts) > 3) or (strict and len(cmpnts < 3)):
                raise ValueError
            if len(cmpnts[0]) > 4: raise ValueError
            year = int(cmpnts[0])
            if len(cmpnts) == 3:
                if len(cmpnts[2]) > 2: raise ValueError
                day = int(cmpnts[2])
            if len(cmpnts) >= 2:
                if len(cmpnts[1]) > 2: raise ValueError
                month = int(cmpnts[1])
        else:   # assume no separator (YYYY[MM[DD]])
            if len(dateStr) == 8:
                year = int(dateStr[:4])
                month = int(dateStr[4:6])
                day = int(dateStr[6:])
            elif not strict and (len(dateStr) == 6):
                year = int(dateStr[:4])
                month = int(dateStr[4:6])
            elif not strict and (len(dateStr) == 4):
                year = int(dateStr)
            else:   # wrong  number of chars
                raise ValueError
        if (month < 1) or (month > 12) or (day < 1) or (day > 31):
            raise ValueError    # only partial check
        return zeroPadNr(year, 4) + '-' + zeroPadNr(month, 2) + '-' + zeroPadNr(day, 2)
    except: # unable to parse as date
        return None

## initialise

## testing code
if __name__ == '__main__':
    sys.stdout.write("crhString tests...\n")
    # add tests here
    sys.stdout.write(singural(0, ' item', ' items') + "\n")
    sys.stdout.write(singural(1, ' item', ' items') + "\n")
    sys.stdout.write(singural(2, ' item', ' items') + "\n")
    sys.stdout.write(singural(0, ' item', ' items', 'begin with ') + "\n")
    sys.stdout.write(singural(1, ' item', ' items', 'begin with ') + "\n")
    sys.stdout.write(singural(2, ' item', ' items', 'begin with ') + "\n")
    sys.stdout.write(singural(0, ' item', ' items', 'begin with ', ' and no more') + "\n")
    sys.stdout.write(singural(1, ' item', ' items', 'begin with ', ' and no more') + "\n")
    sys.stdout.write(singural(2, ' item', ' items', 'begin with ', ' and no more') + "\n")
    sys.stdout.write(trueFalse(True, 'true (ok)', 'false (nok)') + "\n")
    sys.stdout.write(trueFalse(False, 'true (nok)', 'false (ok)') + "\n")
    sys.stdout.write('zeroPadNr("123", 5) -> ' + zeroPadNr('123', 5) + '\n')
    sys.stdout.write('zeroPadNr(123, 5) -> ' + zeroPadNr(123, 5) + '\n')
    sys.stdout.write('zeroPadNr("123", 2) -> ' + zeroPadNr('123', 2) + '\n')
    sys.stdout.write('zeroPadNr(123, 2) -> ' + zeroPadNr(123, 2) + '\n')
    sys.stdout.write('zeroPadNr([1, 2, 3], 5) -> ' + zeroPadNr([1, 2, 3], 5) + '\n')
    sys.stdout.write('pad("abc", 5") >>' + pad('abc', 5) + '<<\n')
    sys.stdout.write('pad("abc", 5, " ", False) >>' + pad('abc', 5, ' ', False) + '<<\n')
    sys.stdout.write('parseDate("2014 04 01") >>' + str(parseDate("2014 04 01")) + '<<\n')
    sys.stdout.write('parseDate(2014-04-01) >>' + str(parseDate(2014-04-01)) + '<<\n')
    sys.stdout.write('parseDate("20140401") >>' + str(parseDate("20140401")) + '<<\n')
    sys.stdout.write('parseDate("2014") >>' + str(parseDate("2014")) + '<<\n')
    sys.stdout.write('us2Spc("CR__Hailey") >>' + us2Spc("CR__Hailey") + '<<\n')
    sys.stdout.write('bsvTuple("one|two||four|\\n") >>' + str(bsvTuple("one|two||four|\n")) + '<<\n')
    sys.stdout.write('csvTuple("one,two,,four,\\n") >>' + str(csvTuple("one,two,,four,\n")) + '<<\n')
