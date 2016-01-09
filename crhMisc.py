# crhMisc.py -- miscellaneous utilities (tier 1)
# Copyright (c) 2013-2015 CR Hailey
# v1.01 crh 30-may-13 -- initial release
# v1.10 crh 14-jul-15 -- FilterSequence added

#!/usr/local/bin/python

## essential variables

## define classes

# class provides switch (aka case) statement functionality
class Switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        '''
        Return the match method once, then stop
        '''
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        '''
        Indicate whether or not to enter a case suite
        '''
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
            
# class filters out proportion of sequence items
class FilterSequence(object):
    '''
    return proportion of sequence items
    '''
    def __init__(self, factor):
        '''
        factor is integer in the range 0..10
        0 (or negative) always returns None
        n  (0>n<10) returns n item(s) in 10
        10 (or bigger) always returns the item
        '''
        if isinstance(factor, int):
            if factor < 0:
                self._factor = 0
            elif factor > 10:
                self._factor = 10
            else:
                self._factor = factor
        else:
            raise TypeError('crhMisc.FilterSequence() -- __init__() requires integer argument')        
        self._seqNr  = 0

    def retain(self):
        '''
        return True or False, as appropriate
        always returns True the first time called
        True proportion will be correct at least after every 10 calls
        '''
        self._seqNr += 1
        seqNr = self._seqNr % 10
        factor = self._factor
        if factor == 0:
            return False
        elif seqNr == 1 or factor == 10:
            return True
        elif seqNr == 0:
            return factor > 6
        elif seqNr == 2:
            return factor > 7
        elif seqNr == 3:
            return factor in [5, 6, 7, 9]
        elif seqNr == 4:
            return factor not in [1, 2, 5]
        elif seqNr == 5:
            return factor in [5, 8]
        elif seqNr == 6:
            return factor not in [1, 3, 5]
        elif seqNr == 7:
            return factor in [5, 7, 8, 9]
        elif seqNr == 8:
            return factor in [3, 6, 7, 9]
        else: return factor not in [1, 2, 3, 7]    # seqNr == 9

## examples

#c = 'z'
#for case in switch(c):
#    if case('a'): pass # only necessary if the rest of the suite is empty
#    if case('b'): pass
#    # ...
#    if case('y'): pass
#    if case('z'):
#        print "c is lowercase!"
#        break
#    if case('A'): pass
#    # ...
#    if case('Z'):
#        print "c is uppercase!"
#        break
#    if case(): # default
#        print "I dunno what c was!"

## initialise

## testing code

if __name__ == '__main__':
    # add test stuff here
    pass
    for factor in range(-1, 12):
        retainLst = list()
        print 'factor: {}'.format(factor)
        total = 0
        filter = FilterSequence(factor)
        for i in range(1, 21):
            if filter.retain():
                retainLst.append(i)
                total += 1
        print retainLst
        print 'total: {}\n'.format(total)
