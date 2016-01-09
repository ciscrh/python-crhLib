# crhFile.py -- file utilities (tier 3)
# Copyright (c) 2013-2015 CR Hailey
# v0.92 crh 25-apr-13 -- under development
# v1.01 crh 29-mar-14 -- initial release
# v1.13 crh 21-jun-14 -- file lists & generators updated/added

#!/usr/local/bin/python

import io
import re
import os
import glob
import fnmatch
import collections
import sys
from crhGV import *
from crhDebug import *
from crhString import *

## essential variables
rcBackslash = re.compile(r'\\')
rcForwardslash = re.compile(r'/')
walkedDir = collections.namedtuple('walkedDir', 'path subdirs files depth')
fileLineGenOK = True    # set False if fileLineGen() raises exception when initialising

## define functions
def dos2UnixPath(path):
    '''
    converts DOS path separators (backslash) to Unix (/)
    '''
    return rcBackslash.sub('/', path)

def unix2DosPath(path):
    '''
    converts Unix path separators (/) to DOS (backslash)
    '''
    return rcForwardslash.sub(r'\\', path)

def osPath(path):
    '''
    correct path for actual os
    '''
    if gv.getVar('os') == 'nt':
        return unix2DosPath(path)
    elif gv.getVar('os') == 'posix':
        return dos2Unix(path)
    else:
        return path

def getFileList(fileGlob, directory = '', fullPath = True):
    '''
    return list of files (excluding path) using glob
    '''
    fileList = []
    if directory != '':
        if os.path.isdir(directory):
            fileList = glob.glob(os.path.join(directory, fileGlob))
        else:   # invalid directory given as parameter
            fileList = None
    else:
        fileList = glob.glob(fileGlob)
    if (fileList is not None) and (not fullPath):   # extract base filename
        for i in range(len(fileList)):
            fileList[i] = os.path.split(fileList[i])[1]
    return fileList

def getFileListR(fileGlob, baseDir = '.', dirGlob = None, depth = None):
    '''
    return list of files (full path) using file & directory pattern matching in recursive search,
    possibly limiting search depth (recursing as deep as necessary by default)
    '''
    fileList = []
    for dirInfo in filterWalkIter(baseDir, fileGlob, dirGlob, depth):
        dirPath = os.path.abspath(dirInfo.path)
        for fname in dirInfo.files:
            fileList.append(os.path.join(dirPath, fname))
    return fileList

def getFileIter(fileGlob, baseDir = '.', dirGlob = None, depth = None):
    '''
    generator version of getFileListR(), yields full path file name
    '''
    for dirInfo in filterWalkIter(baseDir, fileGlob, dirGlob, depth):
        dirPath = os.path.abspath(dirInfo.path)
        for fname in dirInfo.files:
            yield os.path.join(dirPath, fname)

# based on ActiveState code snippet by Nick Coghlan (exists as part of packaged version WalkDir on PyPi)
def filterWalkIter(baseDir, fileGlob=None, dirGlob=None, depth=None, onError=None):
    '''
    generator filterWalkIter is similar to os.walk, but offers the following additional features:
        - yields a named tuple of (path, subdirs, files, depth)
        - allows a recursion depth limit to be specified
        - allows independent glob-style filters for filenames and subdirectories
        - emits a message to stderr and skips the directory if a symlink loop is encountered when following links
       Selective walks are always top down, as the directory listings must be altered to provide
       the above features.
       If not None, depth must be at least 0. A depth of zero can be useful to get separate
       filtered subdirectory and file listings for a given directory.
       onError is passed to os.walk to handle os.listdir errors
    '''
    if depth is not None and depth < 0:
        mesg = 'Depth limit must be None or greater than 0 ({!r} provided)'
        raise ValueError(mesg.format(depth))
    def onLoop(path):
        mesg = 'Symlink {!r} refers to a parent directory, skipping\n'
        sys.stderr.write(mesg.format(path))
        sys.stderr.flush()
    sep = os.sep
    initialDepth = baseDir.count(sep)
    for path, walkSubdirs, files in os.walk(baseDir, topdown=True,
                                             onerror=onError):
        # Filter files, if requested
        if fileGlob is not None:
            files = fnmatch.filter(files, fileGlob)
        # We hide the underlying generator's subdirectory list, since we
        # clear it internally when we reach the depth limit (if any)
        if dirGlob is None:
            subdirs = walkSubdirs[:]
        else:
            subdirs = fnmatch.filter(walkSubdirs, dirGlob)
        # Report depth
        currentDepth = path.count(sep) - initialDepth
        yield walkedDir(path, subdirs, files, currentDepth)
        # Filter directories and implement depth limiting
        if depth is not None and currentDepth >= depth:
            walkSubdirs[:] = []
        else:
            walkSubdirs[:] = subdirs

def splitFileCmpnt(fullname):
    '''
    return fullname components tuple
    '''
    (drive, fullpath) = os.path.splitdrive(os.path.abspath(osPath(fullname)))
    (path, filename) = os.path.split(fullpath)
    (name, ext) = os.path.splitext(filename)
    return (drive, path, name, ext)

def accessFile(filename, fileMode = ''):
    '''
    check path/file access
    '''
    try:
        if fileMode == '':
            message = trueFalse(os.access(filename, os.F_OK), 
                ': exists', ': does not exist')
            statusMsg('info', 'crhFile', filename + message)
            message = trueFalse(os.access(filename, os.R_OK), 
                ': readable', ': not readable')
            statusMsg('info', 'crhFile', filename + message)
            message = trueFalse(os.access(filename, os.W_OK), 
                ': writeable', ': not writeable')
            statusMsg('info', 'crhFile', filename + message)
            message = trueFalse(os.access(filename, os.X_OK), 
                ': executable', ': not executable')
            statusMsg('info', 'crhFile', filename + message)
            return True
        elif fileMode == "fOK" or fileMode == os.F_OK:
            return os.access(filename, os.F_OK)
        elif fileMode == "rOK" or fileMode == os.R_OK:
            return os.access(filename, os.R_OK)
        elif fileMode == "wOK" or fileMode == os.W_OK:
            return os.access(filename, os.W_OK)
        elif fileMode == "xOK" or fileMode == os.X_OK:
            return os.access(filename, os.X_OK)
        else:
            return os.access(filename, fileMode)
    except IOError as e:
        statusErrMsg('error', 'crhFile.accessFile', 'file access error: {}'.format(str(e)))
        return False

def openFile(filename, fileMode, fileBuffer = 1):
    '''
    open file with exception handling
    '''
    # note that binary mode (eg: rb, wb) must be explicitly invoked in Windows
    try:
        fh = open(filename, fileMode, fileBuffer)
        return fh
    except IOError as ie:
        statusErrMsg('error', 'crhFile.openFile', 'exception: IOError')
        if ie.filename:
            errMsg('filename : {}'.format(ie.filename))
        errMsg('file mode: {}'.format(fileMode))
        if ie.message:
            errMsg('message  : {}'.format(ie.message))
        if ie.strerror:
            errMsg('strerror : {}'.format(ie.strerror))
    except ValueError as ve:
        statusErrMsg('error', 'crhFile.openFile', 'exception: ValueError')
        errMsg('filename : {}'.format(filename))
        errMsg('file mode: {}'.format(fileMode))
        if ve.message:
            errMsg('message  : {}'.format(ve.message))
    return None

def fileLineGen(filename, fileMode = 'rU', fileBuffer = 1):
    '''
    text file line generator with exception handling
    opens, reads, strips newline char and automatically closes file on completion,
    using universal newline support read mode by default
    '''
    global fileLineGenOK
    fileLineGenOK = True    # reset initially
    try:
        with open(filename, fileMode, fileBuffer) as fh:
            for line in fh:
                yield line.rstrip('\n')
    
    except IOError as ie:
        fileLineGenOK = False
        statusErrMsg('error', 'crhFile.fileLineGen', 'exception: IOError')
        if ie.filename:
            errMsg('filename : {}'.format(ie.filename))
        errMsg('file mode: {}'.format(fileMode))
        if ie.message:
            errMsg('message  : {}'.format(ie.message))
        if ie.strerror:
            errMsg('strerror : {}'.format(ie.strerror))
    except ValueError as ve:
        fileLineGenOK = False
        statusErrMsg('error', 'crhFile.fileLineGen', 'exception: ValueError')
        errMsg('filename : {}'.format(filename))
        errMsg('file mode: {}'.format(fileMode))
        if ve.message:
            errMsg('message  : {}'.format(ve.message))
    return

## initialise
gv.addStr('os', os.name)
gv.addStr('platform', sys.platform)

## testing code
if __name__ == '__main__':
    # add tests here
    msg('os       : {}'.format(gv.getVar('os')))
    msg('platform : {}'.format(gv.getVar('platform')))
    msg('current directory: {}'.format(os.getcwd()))
    testStr1 = r'\first\second\third'
    testStr2 = r'/first/second/third'
    msg('dos2UnixPath({}) --> {}'.format(testStr1, dos2UnixPath(testStr1)))
    msg('unix2DosPath({}) --> {}'.format(testStr2, unix2DosPath(testStr2)))
    msg('')
    accessFile('asdfg')
    fh = openFile('asdfg', 'rt')
    msg('')
    accessFile('readme.txt')
    fh = openFile('readme.txt', 'rt')
    fh = openFile('readme.txt', 'wt')
    fh = openFile('readme.txt', 'zz')
    msg('')
    accessFile('readonly.txt')
    fh = openFile('readonly.txt', 'rt')
    fh = openFile('readonly.txt', 'wt')
    msg('')
    accessFile('blah')
    fh = openFile('blah', 'rt')
    if fh == None:
        msg('openFile() returned None, as required here')
    msg('getFileListR("setup.py", depth = 2)...')
    print getFileListR('setup.py', depth = 2)
    msg('getFileIter("setup.py", depth = 2)...')
    tmpList = []
    for file in getFileIter('setup.py', depth = 2):
        tmpList.append(file)
    print tmpList
    msg("getFileListR('crh*.py', '..\\', depth = 1)...")
    tmpList = []
    for file in getFileListR('crh*.py', '..\\', depth = 1):
        tmpList.append(file)
    print tmpList
    msg("getFileListR('crh*.py', '..\\')...")
    tmpList = []
    for file in getFileListR('crh*.py', '..\\'):
        tmpList.append(file)
    print tmpList
