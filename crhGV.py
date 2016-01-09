# crhGV.py -- pseudo global variables (tier 1)
# Copyright (c) 2013-2015 CR Hailey
# implemented as a simple class to overcome some problems if not object based
# provides means to add, modify, retrieve & delete pseudo global variables
# v1.01 crh 23-apr-13 -- initial release

#!/usr/local/bin/python
#

from sys import stderr

def _errMsg(message):
    """print message to stderr"""
    
    stderr.write(message + gv.getVar('strTermChar'))
#    sys.stderr.flush()

class GlobalVars(object):
    """object to store & retrieve variables"""
    
    def __init__(self):
        """constructor"""
        
        self._varDict = {}
        
    def isVar(self, varName):
        """checks if varibale exists"""
    
        if varName in self._varDict:
            return True
        else:
            return False
        
    # add pseudo gv methods
    def _addVar(self, varName, varValue):
        """add variable, not called directly"""
    
        pass
        if self.isVar(varName):
            return False
        else:
            self._varDict[varName] = varValue
            return True
            
    def addStr(self, strName, strValue = ''):
        """add string variable"""
    
        if isinstance(strValue, str):
            return self._addVar(strName, strValue)
        else:
            raise TypeError('value of type str required for addStr({})'.format(strName))
    
    def addInt(self, intName, intValue = 0):
        """add integer variable"""
    
        if isinstance(intValue, int):
            return self._addVar(intName, intValue)
        else:
            raise TypeError('value of type int required for addInt({})'.format(intName))
    
    def addFlt(self, fltName, fltValue = 0.0):
        """add float variable"""
    
        if isinstance(fltValue, float):
            return self._addVar(fltName, fltValue)
        else:
            raise TypeError('value of type float required for addFlt({})'.format(fltName))
    
    def addBool(self, boolName, boolValue = True):
        """add boolean variable"""
    
        if isinstance(boolValue, bool):
            return self._addVar(boolName, boolValue)
        else:
            raise TypeError('value of type bool required for addBool({})'.format(boolName))
    
    # set pseudo gv methods
    def _setVar(self, varName, varValue = None):
        """assign value to variable, not called directly"""
    
        if self.isVar(varName):
            self._varDict[varName] = varValue
            return True
        else:
            return False

    def setStr(self, strName, strValue = ''):
        """assign value to string variable"""
    
        if isinstance(strValue, str):
            return self._setVar(strName, strValue)
        else:
            raise TypeError('value of type str required for setStr({})'.format(strName))

    def setInt(self, intName, intValue = 0):
        """assign value to integer variable"""
    
        if isinstance(intValue, int):
            return self._setVar(intName, intValue)
        else:
            raise TypeError('value of type int required for setInt({})'.format(intName))

    def setFlt(self, fltName, fltValue = 0.0):
        """assign value to float variable"""
    
        if isinstance(fltValue, float):
            return self._setVar(fltName, fltValue)
        else:
            raise TypeError('value of type float required for setFlt({})'.format(fltName))

    def setBool(self, boolName, boolValue = True):
        """assign value to boolean variable"""
    
        if isinstance(boolValue, bool):
            return self._setVar(boolName, boolValue)
        else:
            raise TypeError('value of type bool required for setBool({})'.format(boolName))

    # retrieve pseudo gv method
    def getVar(self, varName):
        """return value of a variable"""
    
        if self.isVar(varName):
            return self._varDict[varName]
        else:
            return None

    # delete pseudo gv method
    def delVar(self, varName):
        """remove variable, return its last value"""
    
        if self.isVar(varName):
            val = self._varDict[varName]
            del self._varDict[varName]
            return True
        else:
            return False
            
## set up some crh module/script standard global variables

# assumes module only imported once per script run. 
gv = GlobalVars()
gv.addStr('progName', '_') # script program name, set by crhDebug initially
gv.addBool('debug', False) # debug mode [default: False]
gv.addBool('flush', False) # output immediate flush mode [default: False]
gv.addStr('strTermChar', "\n")  # EOL character used by msg print functions

## testing code

if __name__ == '__main__':
#    print gv._varDict  # do not leave enabled on production code (uses print)
    gv.addStr('testStr', '123')
    _errMsg("testStr: {} ['123']".format(gv.getVar('testStr')))
    gv.setStr('testStr', '321')
    _errMsg("testStr: {} ['321']".format(gv.getVar('testStr')))
#    gv.addStr('testStr', 123)   # raise exception test
    gv.addInt('testInt', 123)
    _errMsg("testInt: {:d} [123]".format(gv.getVar('testInt')))
    gv.setInt('testInt', 321)
    _errMsg("testInt: {:d} [321]".format(gv.getVar('testInt')))
    gv.addFlt('testFlt', 123.)
    _errMsg("testFlt: {:f} [123.]".format(gv.getVar('testFlt')))
    gv.setFlt('testFlt', 321.)
    _errMsg("testFlt: {:.4f} [321.]".format(gv.getVar('testFlt')))
    gv.addBool('testBool', True)
    _errMsg("testBool: {:d} [True]".format(gv.getVar('testBool')))
    gv.setBool('testBool', False)
    _errMsg("testBool: {:d} [False]".format(gv.getVar('testBool')))
