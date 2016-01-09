# crhFileRename.py -- file rename utilities (tier 4), extends crhFile
# Copyright (c) 2014-2015 CR Hailey
# v1.01 crh 07-jul-14 -- initial release

#!/usr/local/bin/python

import io
import re
import os
import glob
from datetime import date
#from os import name as osName
#from sys import platform as osPlatform
import sys
from crhGV import *
from crhDebug import *
from crhString import pad as padStr # resolve name clash
from crhString import *
from crhFile import *

## define essential constants and variables

DELETE = '?'
KEEP = '%'
PAD = '~'
SEQ = '#'
YEAR = 'Y'
MON = 'M'
DAY = 'D'
SEQNR = 1
BASEDIR =  osPath('./')
FILEGLOB = '*.*'
TEMPLATE = '.'
INSMODE = False
MONTHS = ('', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec')

## define functions

def templCmpnts (template):
    '''determine name and extension components of template
return (name, extension) tuple
note that it will allow multiple dot chars in the template (eg "ab.cd.ef")'''

    nam = ext = ''
    if '.' in template:
        (nam, ext) = template.rsplit('.', 1)
        ext = '.' + ext
    else:
        nam = template
    return (nam, ext)

def subDateCmpnts1(template, fileDate = date.today(), year = YEAR, mon = MON, day = DAY):
    '''substitute actual date elements for template date chars
return updated template or None if template date char formatting error detected.
uses the date class to provide the date value'''

    if fileDate is None: 
        return template    # nothing to do
    elif isinstance(fileDate, datetime.date):
        return subDateCmpnts(template, fileDate.year, fileDate.month, fileDate.day, year, mon, day)
    else:
        return subDateCmpnts(template, fileDate[0], fileDate[1], fileDate[2], year, mon, day)

def subDateCmpntsExif(template, exifDate, year = YEAR, mon = MON, day = DAY):
    '''substitute actual date elements for template date chars
return updated template or None if template date char formatting error detected.
uses an exif date or date time tuple from the crhExif module to provide the date value'''

    if exifDate is None: return template    # nothing to do
    return subDateCmpnts(template, str(exifDate[0]), str(exifDate[1]), str(exifDate[2]), year, mon, day)

def subDateCmpnts(template, yr, mn, dy, year = YEAR, mon = MON, day = DAY):
    '''substitute actual date elements for template date chars
return updated template or None if template date char formatting error detected.
year, month and day arguments can be supplied as integer or string values'''

    yr = zeroPadNr(yr, 4)   # can be integer or string, converted to string
    mn = zeroPadNr(mn, 2)   # as above
    dy = zeroPadNr(dy, 2)   # as above
    shortYr = year*2
    longYr = year*4
    shortMn = mon
    mediumMn = mon*2
    longMn = mon*3
    shortDy = day
    longDy = day*2

    if longYr in template:
        template = template.replace(longYr, yr)
    if shortYr in template:
        template = template.replace(shortYr, yr[-2:])
    if year in template: return None  # an odd number of year chars is an error
    if longMn in template:
        template = template.replace(longMn, MONTHS[int(mn)])
    if mediumMn in template:
        template = template.replace(mediumMn, mn)
    if shortMn in template:
        template = template.replace(shortMn, mn.lstrip('0'))
    if longDy in template:
        template = template.replace(longDy, dy)
    if shortDy in template:
        template = template.replace(shortDy, dy.lstrip('0'))
    return template

def insertCheck(template, insMode = INSMODE, 
    delete = DELETE, keep = KEEP, pad = PAD):
    '''check for invalid character markers in template with regard to insert mode
return (ok, error message) tuple'''

    ok = True
    errorMsg = ''
    if insMode:
        if (delete in template) or (keep in template):
            errorMsg= 'delete or keep markers in template (insert mode)'
            ok = False
    elif pad in template:
        errorMsg = 'pad markers in template (overwrite mode)'
        ok = False
    return (ok, errorMsg)

def sequenceWidth(template, seq = SEQ):
    '''determine sequence field width in template
return (ok, width) tuple: (True, 0) means no sequent field present)'''

    width = 0
    seqFields = re.findall(seq + '+', template)
    lsf = len(seqFields)
    if lsf == 1:    # ok, 1 field found
        return (True, len(seqFields[0]))
    elif lsf > 1:   # nok, multiple fields found
        return (False, lsf)
    else:   # ok, no field found
        return (True, 0)

def sequenceStr(seqWidth, seqNr = 0):
    '''return zero padded sequence number string & increment persistent counter
function uses attribute to provide persistent variable of sequence nr
call without seqNr argument to provide next padded nr in sequence
call with seqNr argument to set up initial sequence nr value (not incremented)'''

    if not hasattr(sequenceStr, 'counter'): sequenceStr.counter = 1
    if seqNr < 0: return sequenceStr.counter
    elif seqNr > 0:
        sequenceStr.counter = seqNr
    if len(str(sequenceStr.counter)) > seqWidth: # nr exceeds allocated width!
        paddedNr = str(sequenceStr.counter)[-seqWidth:]  # deal with it
    else:
        paddedNr = zeroPadNr(sequenceStr.counter, seqWidth)
    sequenceStr.counter += 1
    return paddedNr

def sequenceStart(seqNr = 0):
    '''set the sequenceStr() function persistent counter
uses sequenceStr.counter attribute to provide persistent variable of sequence nr'''

    if seqNr <= 0: return sequenceStr.counter
    else: 
        sequenceStr(6, 0)  # ensure counter attribute exists
        sequenceStr.counter = seqNr
        return sequenceStr.counter

def renameFile(fileName, template = '.', insMode = False,
    delete = DELETE, keep = KEEP, pad = PAD, seq = SEQ):
    '''determine new file name and extensions elements by applying template to original file name
default template keeps original file name
return (name, extension) tuple
You should call insertCheck() first to verify template validity'''

    fileName = os.path.basename(fileName)   # remove path component, if present
    (namTmpl, extTmpl) = templCmpnts(template)
    (namTmp, extTmp) = templCmpnts(template)
    lenNam = len(namTmp)
    lenExt = len(extTmp)
    oldNam = os.path.splitext(fileName)[0]
    oldExt = os.path.splitext(fileName)[1]
    tmpNam = tmpExt = ''
    index = padIdx = seqIdx = 0
    char = oldChar = newNam = newExt = ''
    seqWidth = sequenceWidth(template, seq)[1]

    if insMode and (lenNam == 0):   # insert mode: no template name component
        newNam = oldNam
    elif (not insMode) and (len(oldNam) > lenNam):
        namTmp = padStr(namTmp, len(oldNam), pad)
        lenNam = len(namTmp)
    elif len(oldNam) > lenNam:  # left pad template with spaces (for loop)
        namTmp = padStr(namTmp, len(oldNam))
        lenNam = len(namTmp)
    if insMode and (lenExt == 0):   # no template ext component
        newExt = oldExt
    elif (not insMode) and (len(oldExt) > lenExt):
        extTmp = padStr(extTmp, len(oldExt), pad, False)
        lenExt = len(extTmp)
    elif len(oldExt) < lenExt:
        oldExt  = padStr(oldExt, lenExt, pad, False)

    if namTmpl == '':   # always keep existing name
        newNam = oldNam
    elif (not insMode) or (insMode and (namTmp != '')):   # set new name, working from right to left
        if len(oldNam) < len(namTmpl): oldNam = padStr(oldNam, len(namTmpl))
        for index in range(lenNam - 1, -1, -1):
            char = namTmp[index]
            if char == ' ': break   # either mode: effective end of template reached
            elif char == delete: continue   # do nothing (non-insert mode)
            elif (not insMode) and (char == pad): continue # do nothing (non-insert mode)
            elif char == pad:   # insert mode
                oldChar = oldNam[index + padIdx]
                if oldChar != pad: tmpNam = tmpNam + oldChar
            elif char == seq:   # sequence code (either mode)
                padIdx += 1
                seqIdx += 1
                if seqIdx == seqWidth: tmpNam = tmpNam + sequenceStr(seqWidth)[::-1]
            elif char == keep:  # non-insert mode
                if oldNam[index] == ' ': pass # do nothing
                elif oldNam[index] != pad: tmpNam = tmpNam + oldNam[index]
            else:   # use template char (either mode)
                padIdx += 1
                tmpNam = tmpNam + namTmp[index]
        newNam = tmpNam[::-1]   # reverse the string chars

    if extTmpl == '.':   # always keep existing extension
        newExt = oldExt
    elif extTmpl == '':   # always remove extension
        newExt = ''
    elif (not insMode) or (insMode and extTmp != ''): # set new ext, working from left to right
        padIdx = 0
        for index in range(lenExt):
            if index == 0:   # special case, ext always starts with a dot char
                if not insMode: padIdx += 1
                tmpExt = '.'
                continue
            oldChar = ''
            char = extTmp[index]
            if char == delete: continue # do nothing (non-insert mode)
            elif (not insMode) and (char == pad):  continue    # do nothing (non-insert mode)
            elif char == pad:  # insert mode
                padIdx += 1
                oldChar = oldExt[padIdx]
                if oldChar != pad: tmpExt = tmpExt + oldChar
            elif char == seq:  # sequence code
                seqIdx += 1
                if seqIdx == seqWidth: tmpExt = tmpExt + sequenceStr(seqWidth)  # add sequence nr
            elif char == keep:  # non-insert mode
                if oldExt[index] != pad: tmpExt = tmpExt + oldExt[index]
            else: tmpExt = tmpExt + extTmp[index]   # use template char (either mode)
        newExt = tmpExt
    return (newNam, newExt)

def renameFileD(fileName, template = '.', insMode = False, fileDate = date.today(),
    delete = DELETE, keep = KEEP, pad = PAD, seq = SEQ, year = YEAR, mon = MON, day = DAY):
    '''date aware version of renameFile()
determine new file name and extensions elements by applying template to original file name
default template keeps original file name
return (name, extension) tuple
You should call insertCheck() first to verify template validity'''

    # first modify template by processing date marker characters
    template = subDateCmpnts1(template, fileDate, year, mon, day)
    if template is None: return None
    # then call renameFile() using modified template
    return renameFile(fileName, template, insMode, delete, keep, pad, seq)

## initialise

## testing code
if __name__ == '__main__':
    # add tests here
    (name, extn) = templCmpnts('.')
    print('templCmpnts(".")::({}, {})'.format(name, extn))
    (name, extn) = templCmpnts('abcdef.xyz')
    print('templCmpnts("abcdef.xyz")::({}, {})'.format(name, extn))
    (name, extn) = templCmpnts('abcdef.')
    print('templCmpnts("abcdef.")::({}, {})'.format(name, extn))
    (name, extn) = templCmpnts('abcdef')
    print('templCmpnts("abcdef")::({}, {})'.format(name, extn))
    (name, extn) = templCmpnts('ab.cd.ef')
    print('templCmpnts("ab.cd.ef")::({}, {})'.format(name, extn))
    (name, extn) = templCmpnts('.xyz')
    print('templCmpnts(".xyz")::({}, {})'.format(name, extn))

    (ok, message) = insertCheck('???abc-###.%%%')
    print('insertCheck("???abc-###.%%%")::({}, {})'.format(str(ok), message))
    (ok, message) = insertCheck('???abc-###.%%%', True)
    print('insertCheck("???abc-###.%%%", True)::({}, {})'.format(ok, message))
    (ok, message) = insertCheck('???abc-###.%%%', True, keep = '+', delete = '=')
    print('insertCheck("???abc-###.%%%", True, keep = "+", delete = "=")::({}, {})'.format(ok, message))
    (ok, message) = insertCheck('???abc-###.%%%')
    (ok, message) = insertCheck('???abc-~~~.%%%')
    print('insertCheck("???abc-~~~.%%%")::({}, {})'.format(ok, message))

    (ok, nr) = sequenceWidth('???abc-###.%%%')
    print('sequenceWidth("???abc-###.%%%")::({}, {})'.format(ok, nr))
    (ok, nr) = sequenceWidth('???abc-###.%%%##')
    print('sequenceWidth("???abc-###.%%%##")::({}, {})'.format(ok, nr))
    (ok, nr) = sequenceWidth('???abc.%%%')
    print('sequenceWidth("???abc.%%%")::({}, {})'.format(ok, nr))

    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    nr = sequenceStart(50); print('sequenceStart(50)::{}'.format(nr))
    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    print('sequenceStr(4, 75)::{}'.format(sequenceStr(4, 75)))
    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    nr = sequenceStart(); print('sequenceStart()::{}'.format(nr))
    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    nr = sequenceStart(1); print('sequenceStart(1)::{}'.format(nr))
    print('sequenceStr(4)::{}'.format(sequenceStr(4)))
    sequenceStart(1)

    (name, extn) = renameFile('abcdfg.xyz')
    print('renameFile("abcdfg.xyz")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('abcdfg.xyz', '%%%###.zzz')
    print('renameFile("abcdfg.xyz", "%%%###.zzz")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('abcdfg.xyz', '%%%###.##z')
    print('renameFile("abcdfg.xyz", "%%%###.##z")::({}, {})::invalid template!'.format(name, extn))
    (name, extn) = renameFile('abcdfg.uvw.xyz', '%%%~~~~###.zzz')
    print('renameFile("abcdfg.uvw.xyz", "%%%~~~~###.zzz")::({}, {})::invalid template!'.format(name, extn))
    (name, extn) = renameFile('abcdfg.uvw.xyz', '%%%????###.zzz')
    print('renameFile("abcdfg.uvw.xyz", "%%%????###.zzz")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('abcdfg.xyz', '%%%??###.zzz')
    print('renameFile("abcdfg.xyz", "%%%??###.zzz")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('P012345678.JPG', '1404-%%%%.jpg')
    print('renameFile("P012345678.JPG", "1404-%%%%.jpg")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('P012345678.JPG', '1404-&&&&.jpg', keep ='&')
    print('renameFile("P012345678.JPG", "1404-&&&&.jpg", keep = "&")::({}, {})'.format(name, extn))
    (name, extn) = renameFile('P012345678.JPG', '1404-&&&&$$.jpg', keep ='&', delete = '$')
    print('renameFile("P012345678.JPG", "1404-&&&&$$.jpg", keep = "&", delete = "$")::({}, {})'.format(name, extn))

    print 'date.today()::' + str(date.today())
    print 'date.today()::', date.today()
    print 'subDateCmpnts1("1401-%%%%.jpg")::' + subDateCmpnts1("1401-%%%%.jpg")
    print 'subDateCmpnts1("YYMM-%%%%.jpg")::' + subDateCmpnts1("YYMM-%%%%.jpg")
    print 'subDateCmpnts1("YYYY-MMM-%%%%.jpg")::' + subDateCmpnts1("YYYY-MMM-%%%%.jpg")
    print 'subDateCmpnts1("ZZZZ-MM-DD", year = "Z")::' + subDateCmpnts1("ZZZZ-MM-DD", year = "Z")
    print 'subDateCmpnts1("XXXX-YY-ZZ", date.today(), "X", "Y", "Z")::' + subDateCmpnts1("XXXX-YY-ZZ", date.today(), "X", "Y", "Z")
    print 'subDateCmpnts1("YYYY-MM-DD", (2010, 04, 01))::' + subDateCmpnts1("YYYY-MM-DD", (2010, 04, 01))

    print 'subDateCmpnts("1401-%%%%.jpg", 2014, 04, 01)::' + subDateCmpnts("1401-%%%%.jpg", 2014, 04, 01)
    print 'subDateCmpnts("YYMM-%%%%.jpg", 2014, 04, 01)::' + subDateCmpnts("YYMM-%%%%.jpg", 2014, 04, 01)
    print 'subDateCmpnts("YYYY-MMM-%%%%.jpg", 2014, 04, 01)::' + subDateCmpnts("YYYY-MMM-%%%%.jpg", 2014, 04, 01)
    print 'subDateCmpnts("YYYY-M-D", "2014", "04", "01")::' + subDateCmpnts("YYYY-M-D", "2014", "04", "01")
    print 'subDateCmpnts("YYYY-MM-DD", "2014", "04", "01")::' + subDateCmpnts("YYYY-MM-DD", "2014", "04", "01")
    print 'subDateCmpnts("ZZZZ-MM-DD", "2014", "04", "01", year = "Z")::' + subDateCmpnts("ZZZZ-MM-DD", "2014", "04", "01", year = "Z")

    (name, extn) = renameFileD('P012345678.JPG', 'YYMM-%%%%.jpg')
    print('renameFileD("P012345678.JPG", "YYMM-%%%%.jpg")::({}, {})'.format(name, extn))
    (name, extn) = renameFileD('P012345678.JPG', 'YYMM-&&&&.jpg', keep ='&')
    print('renameFileD("P012345678.JPG", "YYMM-&&&&.jpg", keep = "&")::({}, {})'.format(name, extn))
    (name, extn) = renameFileD('P012345678.JPG', 'YYMM-&&&&$$.jpg', keep ='&', delete = '$')
    print('renameFileD("P012345678.JPG", "YYMM-&&&&$$.jpg", keep = "&", delete = "$")::({}, {})'.format(name, extn))

