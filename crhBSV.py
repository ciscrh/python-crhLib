# crhBSV.py -- bsv file processing utilities (tier 3)
# Copyright (c) 2013-2015 CR Hailey
# v1.00 crh 30-may-13 -- initial release
# v2.01 crh 30-jan-15 -- add bsv class implementation
# v2.12 crh 10-mar-15 -- incorporate class variables & methods & add more instance methods

# most bsv coding can be handled using just class methods & variables
# instance methods & variables are used to deal with unusual cases
# class variables & methods are given an initial upper case letter
# instance variables & methods are given an initial lower case letter
# all former module functions have been removed, use bsv class methods instead

#!/usr/local/bin/python

from crhDebug import *

# renamed from v1.x, now treated as constants
_SEPCHAR = '|'
_SEPESCSEQ = '!!!!'
_NEWLINESEQ = r'\r\n'   # new in v2


## bar separated value class (new in v2)

class bsv(object):
    '''a class for processing bar separated value records'''

    # class variables, most of which should be considered as read-only.
    # you should create & use an instance if you need to change any of these basic values
    # formerly defined as module variables so possible backwards compatibility issues (unlikely)
    _SepChar = _SEPCHAR   # character separating the fields in a record line
    _SepEscSeq = _SEPESCSEQ   # sequence of characters used to escape embedded sep chars
    _NewLineSeq = _NEWLINESEQ # sequence of characters used to escape embedded new lines

    # class methods are provided to modify the field name list
    _FieldNameList = []

    # allows module testing if set True :-)
    _TestMode = False

    ## class methods for basic management of _FieldNameList

    @classmethod
    def FieldNameList(cls, line = None):
        '''converts bsv line of text to list of field names & update the corresponding class variable
        return the updated fieldNameList, or just
        return the existing fieldNameList if bsv line argument not supplied'''

        if line is not None:
            cls._FieldNameList =  cls.Line2List(line)
        return cls._FieldNameList

    @classmethod
    def ReorderFieldNames(cls, names):
        ''' the names list values must be a subset of the class variable fieldNameList
        return reordered field name list, does not modify fieldNameList'''

        if len(cls._FieldNameList) != len(names):
            statusErrMsg('warn', 'crhBSV.ReorderFieldNames', 'mismatched list length')
        newList = []
        for i in range(len(names)):
            if names[i] in cls._FieldNameList:
                newList.append(names[i])
            else:
                if (__name__ == '__main__') or bsv._TestMode:
                    statusErrMsg('error', "ReorderFieldNames()", names[i] + " not in fieldNameList")
                    return None
                else:
                    statusErrMsg('fatal', "ReorderFieldNames()", names[i] + " not in fieldNameList")
                    sys.exit(1)
        return newList

    ## class methods without equivalent instance methods (ie, suitable for both class & instances)

    @classmethod
    def ListMsg(cls, lst, suppress = False, stdErr = True):
        '''print list to stderr/stdout, possibly,
        default to stderr'''

        if not suppress:
            _stdErrMsg('[', stdErr, False, False)
            j = len(lst) - 1
            for i in range(len(lst)):
                _stdErrMsg(lst[i], stdErr, False, False)
                if i < j:
                    _stdErrMsg(', ', stdErr, False, False)
            _stdErrMsg(']', stdErr)

    @classmethod
    def DictMsg1(cls, dct, suppress = False, stdErr = True):
        '''print unordered dictionary to stderr/stdout, possibly,
        default to stderr'''

        if suppress: return None
        if dct == None:
            _stdErrMsg('None', stdErr, False, False)
            return
        _stdErrMsg('{', stdErr, False, False)
        j = len(dct) - 1
        i = 0
        for k in dct:
            _stdErrMsg(k + ': ' + str(dct[k]), stdErr, False, False)
            if i < j:
                _stdErrMsg(', ', stdErr, False, False)
                i += 1
        _stdErrMsg('}', stdErr)

    ## instance methods for basic management

    def __init__(self, sepChar = _SEPCHAR, sepEscSeq = _SEPESCSEQ, newLineSeq = _NEWLINESEQ):
        '''initialise object'''
 
        # initially set to the default values if not given as arguments
        self._sepChar = sepChar
        self._sepEscSeq = sepEscSeq
        self._newLineSeq = newLineSeq

        # no initial value, these allow bsv records to be created, stored & retrieved as lists, etc
        self._fieldNameList = []
        self._fieldNameTuple = tuple()
        self._recordTupleList = []

    def sepChar(self, sepChar = None):
        '''sets the instance field separator character
        returns the old value, acts as a get method if None value supplied'''

        oldSepChar = self._sepChar
        if not sepChar is None:
            self._sepChar = sepChar
        return oldSepChar

    def sepEscSeq(self, sepEscSeq = None):
        '''sets the instance field separator character escape code
        returns the old value, acts as a get method if None value supplied'''

        oldSepEscSeq = self._sepEscSeq
        if not sepEscSeq is None:
            self._sepEscSeq = sepEscSeq
        return oldSepEscSeq

    def newLineSeq(self, newLineSeq = None):
        '''sets the instance field new line character sequence
        returns the old value, acts as a get method if None value supplied'''

        oldNewLineSeq = self._newLineSeq
        if not newLineSeq is None:
            self._newLineSeq = newLineSeq
        return oldNewLineSeq

    def fieldNameList(self, line = None):
        '''converts bsv line of text to list & tuple of field names
        & save them as instance variables
        returns the old value, acts as a get method if None value supplied'''

        oldFieldNameList = self._fieldNameList
        if not line is None:
            self._fieldNameList =  self.line2List(line)
            self._fieldNameTuple = tuple(self._fieldNameList)
        return oldFieldNameList

    def fieldNameTuple(self, line = None):
        '''converts bsv line of text to tuple & list of field names
        & save them as instance variables
        returns the old value, acts as a get method if None value supplied'''

        oldFieldNameTuple = self._fieldNameTuple
        if not line is None:
            self.fieldNameList(line)
        return oldFieldNameTuple

    def reorderFieldNameList(self, names):
        '''return reordered field name list, does not modify _fieldNameList'''

        if len(self._fieldNameList) != len(names):
            statusErrMsg('warn', 'crhBSV.reorderFieldNameList', 'mismatched list length')
        newList = []
        for i in range(len(names)):
            if names[i] in self._fieldNameList:
                newList.append(names[i])
            else:
                if (__name__ == '__main__') or bsv._TestMode:
                    statusErrMsg('error', 'crhBSV.reorderFieldNameList', names[i] + ' not in _fieldNameList')
                    return None
                else:
                    statusErrMsg('fatal', 'crhBSV.reorderFieldNameList', names[i] + ' not in _fieldNameList')
                    sys.exit(1)
        return newList

    ## instance records tuple list management

    def addRecordLine(self, line):
        '''convert bsv line to tuple & add to instance records list
        return new tuple if successful, None otherwise'''

        tmpTuple = self.line2Tuple(line)
        if len(tmpTuple) != len(self._fieldNameTuple):
            statusErrMsg('error', 'crhBSV.addRecordLine', 'bsv line fields/name fields length mismatch')
            return None
        else:
            self._recordTupleList.append(tmpTuple)
            return tmpTuple

    def addRecordList(self, lst):
        '''add list to tuple list
        return new tuple if successful, None otherwise'''

        tmpTuple = tuple(lst)
        if len(tmpTuple) != len(self._fieldNameTuple):
            statusErrMsg('error', 'crhBSV.addRecordList', 'list/name fields length mismatch')
            return None
        else:
            self._recordTupleList.append(tmpTuple)
            return tmpTuple

    def addRecordDict(self, dct):
        '''add dictionary to tuple list
        return new tuple if successful, None otherwise'''

        tmpList = []
        nameError = False
        if len(dct) != len(self._fieldNameTuple):
            statusErrMsg('error', 'crhBSV.addRecordDict', 'dictionary/name fields length mismatch')
            return None
        for name in self._fieldNameTuple:
            if name in dct:
                tmpList.append(dct[name])
            else:
                statusErrMsg('error', 'crhBSV.addRecordDict', 'invalid field name ({})'.format(name))
                nameError = True
        if nameError:
            return None
        else:
            return self.addRecordList(tmpList)

    def recordTupleList(self):
        '''return instance records tuple list'''

        return self._recordTupleList

    # some instance generators, all acting on the instance variable _recordTupleList

    def bsvGen(self):
        '''bsv line generator function
        iterates over the instance record tuple list
        yields single record bsv line'''

        for t in self._recordTupleList:
            yield self.tuple2Line(t)

    def tupleGen(self):
        '''tuple generator function
        iterates over the instance record tuple list
        yields single record tuple'''

        for t in self._recordTupleList:
            yield t

    def listGen(self):
        '''list generator function
        iterates over the instance record tuple list
        yields single record list'''

        for t in self._recordTupleList:
            yield list(t)

    def dictGen(self):
        '''dictionary generator function
        iterates over the instance record tuple list
        yields single record dictionary'''

        for t in self._recordTupleList:
            yield self.line2Dict(self.tuple2Line(t))

    ## general methods not directly involving the instance record tuple list
    ## & typically giving functionality previously provided by module methods
    ## note that both instance & class versions of these methods are defined

    def line2List(self, line):
        '''converts bsv line of text to list of fields'''

        bsvRecord =  line.split(self._sepChar)
        for i in range(len(bsvRecord)):
            bsvRecord[i] = bsvRecord[i].replace(self._sepEscSeq, self._sepChar)
        return bsvRecord

    @classmethod
    def Line2List(cls, line):
        '''converts bsv line of text to list of fields'''

        bsvRecord =  line.split(cls._SepChar)
        for i in range(len(bsvRecord)):
            bsvRecord[i] = bsvRecord[i].replace(cls._SepEscSeq, cls._SepChar)
        return bsvRecord

    def listML(self, line):
        '''converts bsv line of text to list of list of fields
        first converts fields with new line escape sequences to list of lines
        otherwise each field list contains just one element'''

        bsvRecord =  line.split(self._sepChar)
        for i in range(len(bsvRecord)):
            bsvRecord[i] = bsvRecord[i].replace(self._sepEscSeq, self._sepChar)
            bsvRecord[i] = self.fieldList(bsvRecord[i])
        return bsvRecord

    @classmethod
    def ListML(cls, line):
        '''converts bsv line of text to list of list of fields
        first converts fields with new line escape sequences to list of lines
        otherwise each field list contains just one element'''

        bsvRecord =  line.split(cls._SepChar)
        for i in range(len(bsvRecord)):
            bsvRecord[i] = bsvRecord[i].replace(cls._SepEscSeq, cls._SepChar)
            bsvRecord[i] = cls.FieldList(bsvRecord[i])
        return bsvRecord

    def line2Tuple(self, line):
        '''converts bsv line of text to tuple of fields'''

        return tuple(self.line2List(line))

    @classmethod
    def Line2Tuple(cls, line):
        '''converts bsv line of text to tuple of fields'''

        return tuple(cls.Line2List(line))

    def tupleML(self, line):
        '''converts bsv line of text to tuple of tuple of fields
        first converts fields with new line escape sequences to list of lines
        otherwise each field tuple contains just one element'''

        bsvRecordList =  self.listML(line)
        for i in range(len(bsvRecordList)):
            bsvRecordList[i] = tuple(bsvRecordList[i])
        return tuple(bsvRecordList)

    @classmethod
    def TupleML(cls, line):
        '''converts bsv line of text to tuple of tuple of fields
        first converts fields with new line escape sequences to list of lines
        otherwise each field tuple contains just one element'''

        bsvRecordList =  cls.ListML(line)
        for i in range(len(bsvRecordList)):
            bsvRecordList[i] = tuple(bsvRecordList[i])
        return tuple(bsvRecordList)

    def line2Dict(self, line):
        '''converts bsv line of text to dictionary of fields'''

        if self._fieldNameTuple:
            tmpList =  self.line2List(line)
            tmpDict = dict()
            for i in range(len(tmpList)):
                tmpDict[self._fieldNameTuple[i]] = tmpList[i]
            return tmpDict
        else:   # no field name tuple defined: abort program
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.line2Dict', '_fieldNameTuple not defined')
                return None
            else:
                statusErrMsg('fatal', 'crhBSV.line2Dict', '_fieldNameTuple not defined')
                sys.exit(1)

    @classmethod
    def Line2Dict(cls, line):
        '''converts bsv line of text to dictionary of fields'''

        if cls._FieldNameList:
            tmpList =  cls.Line2List(line)
            tmpDict = dict()
            for i in range(len(tmpList)):
                tmpDict[cls._FieldNameList[i]] = tmpList[i]
            return tmpDict
        else:   # no field name tuple defined: abort program
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.Line2Dict', 'FieldNameList not defined')
                return None
            else:
                statusErrMsg('fatal', 'crhBSV.Line2Dict', 'FieldNameList not defined')
                sys.exit(1)

    def list2Line(self, lst):
        '''converts list to bsv line of text'''

        for i in range(len(lst)):
            lst[i] = str(lst[i]).replace(self._sepChar, self._sepEscSeq)
        return self._sepChar.join(lst)

    @classmethod
    def List2Line(cls, lst):
        '''converts list to bsv line of text'''

        for i in range(len(lst)):
            lst[i] = str(lst[i]).replace(cls._SepChar, cls._SepEscSeq)
        return cls._SepChar.join(lst)

    def tuple2Line(self, tpl):
        '''converts tuple to bsv line of text'''

        return self.list2Line(list(tpl))

    @classmethod
    def Tuple2Line(cls, tpl):
        '''converts tuple to bsv line of text'''

        return cls.List2Line(list(tpl))

    def dict2Line(self, dct):
        '''converts dictionary to bsv line of text'''

        if self._fieldNameTuple:
            tmpLine = ''
            j = len(self._fieldNameTuple) - 1
            for i in range(len(self._fieldNameTuple)):
                try:
                    tmpLine += dct[self._fieldNameTuple[i]].replace(self._sepChar, self._sepEscSeq)
                except KeyError as e:
                    if (__name__ == '__main__') or bsv._TestMode:
                        statusErrMsg('error', 'crhBSV.dict2Line', 
                            'missing dictionary key: {}'.format(str(e)))
                    else:
                        statusErrMsg('fatal', 'crhBSV.dict2Line', 
                            'missing dictionary key: {}'.format(str(e)))
                        sys.exit(1)
                if i < j:
                    tmpLine += self._sepChar
            return tmpLine
        else:   # no field name list defined, abort program
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.dict2Line', '_fieldNameTuple not defined')
                return None
            else:
                statusErrMsg('fatal', 'crhBSV.dict2Line', '_fieldNameTuple not defined')
                sys.exit(1)

    @classmethod
    def Dict2Line(cls, dct):
        '''converts dictionary to bsv line of text'''

        if cls._FieldNameList:
            tmpLine = ''
            j = len(cls._FieldNameList) - 1
            for i in range(len(cls._FieldNameList)):
                try:
                    tmpLine += dct[cls._FieldNameList[i]].replace(cls._SepChar, cls._SepEscSeq)
                except KeyError as e:
                    if (__name__ == '__main__') or bsv._TestMode:
                        statusErrMsg('error', 'crhBSV.Dict2Line', 
                            'missing dictionary key: {}'.format(str(e)))
                    else:
                        statusErrMsg('fatal', 'error', 'crhBSV.Dict2Line', 
                            'missing dictionary key: {}'.format(str(e)))
                        sys.exit(1)
                if i < j:
                    tmpLine += cls._SepChar
            return tmpLine
        else:   # no field name list defined, abort program
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.Dict2Line', 'fieldNameList not defined')
                return None
            else:
                statusErrMsg('fatal', 'crhBSV.Dict2Line', 'fieldNameList not defined')
                sys.exit(1)

    def printRecord(self, record, sparse = False, pad = 10):
        '''print basic ordered formatted dictionary record as key: value lines
        pad should be equal or greater than the length of the longest possible field name'''

        if not self._fieldNameTuple:
            statusErrMsg('fatal', 'crhBSV.printRecord', '_fieldNameTuple not defined')
            sys.exit(1)
        for i in range(len(self._fieldNameTuple)):
            k = self._fieldNameTuple[i]
            v = record[k]
            if v or (not sparse):
                msg(k.ljust(pad) + ': ', lf = False)
                # replace escape sequence with newline
                msg(v.replace(self._newLineSeq, '\n' + ' ' * (pad + 2)))
        msg('---------------------------')

    @classmethod
    def PrintRecord(cls, record, sparse = False, pad = 10):
        '''print basic ordered formatted dictionary record as key: value lines
        pad should be equal or greater than the length of the longest possible field name'''

        if not cls._FieldNameList:
            statusErrMsg('fatal', 'crhBSV.PrintRecord', '_FieldNameList not defined')
            sys.exit(1)
        for i in range(len(cls._FieldNameList)):
            k = cls._FieldNameList[i]
            v = record[k]
            if v or (not sparse):
                msg(k.ljust(pad) + ': ', lf = False)
                # replace escape sequence with newline
                msg(v.replace(cls._NewLineSeq, '\n' + ' ' * (pad + 2)))
        msg('---------------------------')

    def dictMsg(self, dct, suppress = False, stdErr = True):
        '''print ordered dictionary to stderr/stdout, possibly,
        default to stderr'''
        if len(self._fieldNameList) == 0:
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.dictMsg', 
                    'instance field name list not set')
            else:
                statusErrMsg('fatal', 'crhBSV.dictMsg', 
                    'instance field name list not set')
                sys.exit(1)
        if not suppress:
            if dct == None:
                _stdErrMsg('None', stdErr)
                return
            _stdErrMsg('{', stdErr, False, False)
            j = len(self._fieldNameList) - 1
            for i in range(len(self._fieldNameList)):
                try:
                    k = self._fieldNameList[i]
                    _stdErrMsg(k + ': ' + str(dct[k]), stdErr, False, False)
                except KeyError as e:
                    _stdErrMsg('', stdErr)
                    if (__name__ == '__main__') or bsv._TestMode:
                        statusErrMsg('error', 'crhBSV.dictMsg', 
                            'missing dictionary key: {}'.format(str(e)))
                    else:
                        statusErrMsg('fatal', 'crhBSV.dictMsg', 
                            'missing dictionary key: {}'.format(str(e)))
                        sys.exit(1)
                if i < j:
                    _stdErrMsg(', ', stdErr, False, False)
            _stdErrMsg('}', stdErr)

    @classmethod
    def DictMsg(cls, dct, suppress = False, stdErr = True):
        '''print ordered dictionary to stderr/stdout, possibly,
        default to stderr'''
        if len(bsv._FieldNameList) == 0:
            if (__name__ == '__main__') or bsv._TestMode:
                statusErrMsg('error', 'crhBSV.DictMsg', 
                    'class field name list not set')
            else:
                statusErrMsg('fatal', 'crhBSV.DictMsg', 
                    'class field name list not set')
                sys.exit(1)
        if not suppress:
            if dct == None:
                _stdErrMsg('None', stdErr)
                return
            _stdErrMsg('{', stdErr, False, False)
            j = len(bsv._FieldNameList) - 1
            for i in range(len(bsv._FieldNameList)):
                try:
                    k = bsv._FieldNameList[i]
                    _stdErrMsg(k + ': ' + str(dct[k]), stdErr, False, False)
                except KeyError as e:
                    _stdErrMsg('', stdErr)
                    if (__name__ == '__main__') or bsv._TestMode:
                        statusErrMsg('error', 'crhBSV.DictMsg', 
                            'missing dictionary key: {}'.format(str(e)))
                    else:
                        statusErrMsg('fatal', 'crhBSV.DictMsg', 
                            'missing dictionary key: {}'.format(str(e)))
                        sys.exit(1)
                if i < j:
                    _stdErrMsg(', ', stdErr, False, False)
            _stdErrMsg('}', stdErr)

    def fieldList(self, field):
        '''generate multi-value list from field, using new line escape sequences'''

        fieldList = field.split(self._newLineSeq)
        return fieldList

    @classmethod
    def FieldList(cls, field):
        '''generate multi-value list from field, using new line escape sequences'''

        fieldList = field.split(cls._NewLineSeq)
        return fieldList

## end of class bsv

## helper functions for use within module

def _stdErrMsg(message, stdErr = True, suppress = False, lf = True):
    '''use crhDebug errMsg()/msg() as required,
    default to errMsg()'''

    if stdErr:
        errMsg(message, suppress, lf)
    else:
        msg(message, suppress, lf)

def _bsvTestMode(mode = True):
    '''allow development testing by replacing fatal errors with errors'''

    global bsv
    bsv._TestMode = mode

## initialise

## testing code
# (comprehensive testing now handled by crhBSV-test.py)

if __name__ == '__main__':
    # add test stuff here
    pass
