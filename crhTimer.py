# crhTimer.py -- stopwatch timer (tier 3), replaces the Timer previously provided by crhDate
# note (1) that on windows systems it measures wall clock time & (I think) on linux, process time!!!
# on python v3 you can use perf_counter() & process_time() to measure either as required
# note (2) calling these methods consumes significant milliseconds
# so frequent calls will adversely effect the time consumed by the script at millisecond precision!
# Copyright (c) 2015 CR Hailey
# v1.00 crh 03-jun-15 -- initial release

#!/usr/local/bin/python
#

from time import clock
from crhGV import gv    # object holding global variables shared across modules & scripts 
import crhDebug

## timer class

class Timer(object):
    '''object implementing simple timer'''
    
    def __init__(self, start = False, seconds = True, millisec = True):
        '''constructor, timer not started by default'''
    
        self._reset(seconds, millisec)
        if start:   # make use of seconds & milliseconds params
            self.start(seconds, millisec)
        
    def _reset(self, seconds = True, millisec = True):
        '''reset attributes to initial state'''
        
        self._elapsed =  0.0
        self._seconds = True    # output in elapsed seconds
        self._millisec = True   # seconds precision of 3dp
        self._func = clock      # process for measuring elapsed time
        self._startTime = None
        self._started = False
        self._paused = False

    def start(self, seconds = True, millisec = True):
        '''start timer, output seconds & milliseconds by default
        resumes timer after previous stop() call
        starts new timer session after previous reset() call
        returns elapsed time (non zero if resuming timer)'''
        
        if self._started:   # previously started
            if (not self._paused):
                raise RuntimeError('Timer.start() -- timer already started')
            else:   # previously paused
                self._paused = False
                self._startTime = self._func() - self._elapsed
                self._seconds = seconds
                self._millisec = millisec
                return self._elapsed
        else:   # previously reset or not started
            self._startTime = self._func()
            self._started = True
        self._seconds = seconds
        self._millisec = millisec
        return self._elapsed
        
    def stop(self):
        '''stop (suspends) timer & return elapsed time
        timer can be resumed later if required by calling start()
        elapsed time retained & can be retrieved by calling elapsed()'''
        
        if not (self._started or self._paused):
            raise RuntimeError('Timer.stop() -- timer not started')
        if not self._paused:
            self._elapsed = self._func() - self._startTime
#        self._started = True
        self._paused = True
        return self._output()
        
    def elapsed(self):
        '''return elapsed time, updating elapsed time if timer running'''
        
        if not (self._started or self._paused):
            raise RuntimeError('Timer.elapsed() -- timer not started')
        if self._paused:
            return self._output()
        self._elapsed = self._func() - self._startTime
        return self._output()
        
    def reset(self):
        '''reset timer, returning elapsed time if available
        subsequent call to elapsed() will trigger exception unless
        preceded by calling start()'''
        
        if self._started:
            if self._paused:
                elapsed = self._elapsed
            else:
                elapsed = self._func() - self._startTime
        else:
            elapsed = None
        self._reset()
        return elapsed
    
    def _output(self):
        '''output suitably processed time'''
        
        elapsed = self._elapsed
        if self._seconds:   # default -- output seconds
            if (elapsed >= 86400.0):   # limit elapsed time to 86399.xxx secs (ie, <1 day)
                raise RuntimeError('Timer._output() -- elapsed time ({} seconds) outside acceptable range'.format(int(self._elapsed)))
            if self._millisec:  # default -- output to milliseconds precision
                return round(elapsed, 3)
            else:   # output to nearest second
                return int(round(elapsed, 0))
        else:   # output tuple (hr, min, sec [,ms])
            hr = int(elapsed//3600)
            mn = int((elapsed%3600)//60)
            sec = int(elapsed%60)
            if self._millisec:  # default -- include milliseconds field in tuple
                return (hr, mn, sec, int((round(elapsed, 3) - int(elapsed))*1000))
            else:
                return (hr, mn, sec)

## initialise

timer = Timer(True) # start Timer instance by default when importing this module

## testing code

if __name__ == '__main__':
    from time import sleep
    
    timer1 = Timer(True, False)
    print 'timer (elapsed 0.0)   = {:6.3f}'.format(timer.elapsed())
    print 'timer1 (elapsed 0.0)  = {}'.format(timer1.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.1)   = {:6.3f}'.format(timer.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.2)   = {:6.3f}'.format(timer.elapsed())
    print 'timer1 (elapsed 0.2)  = {}'.format(timer1.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.3)   = {:6.3f}'.format(timer.elapsed())
    print 'timer stopped         = {:6.3f}'.format(timer.stop())
    sleep(0.1)
    print 'timer (elapsed 0.4)   = {:6.3f}'.format(timer.elapsed())
    print 'timer1 (elapsed 0.4)  = {}'.format(timer1.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.5)   = {:6.3f}'.format(timer.elapsed())
    print 'timer started         = {:6.3f}'.format(timer.start())
    sleep(0.1)
    print 'timer (elapsed 0.6)   = {:6.3f}'.format(timer.elapsed())
    print 'timer1 (elapsed 0.6)  = {}'.format(timer1.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.7)   = {:6.3f}'.format(timer.elapsed())
    print 'timer stopped         = {:6.3f}'.format(timer.stop())
    sleep(0.1)
    print 'timer (elapsed 0.8)   = {:6.3f}'.format(timer.elapsed())
    timer.reset()
    print 'timer reset & started = {:6.3f}'.format(timer.start())
    print 'timer1 (elapsed 0.8)  = {}'.format(timer1.elapsed())
    sleep(0.1)
    print 'timer (elapsed 0.9)   = {:6.3f}'.format(timer.elapsed())
    sleep(0.1)
    print 'timer (elapsed 1.0)   = {:6.3f}'.format(timer.elapsed())
    print 'timer stopped         = {:6.3f}'.format(timer.stop())
    sleep(0.1)
    print 'timer1 (elapsed 1.1)  = {}'.format(timer1.elapsed())
    print 'timer (elapsed 1.1)   = {:6.3f}'.format(timer.elapsed())
    print 'timer reset           = {:6.3f}'.format(timer.reset())
    sleep(0.1)
    print 'call to timer.elapsed() now should trigger exception...'
    try:
        print 'timer (elapsed 1.2)   = {:6.3f}'.format(timer.elapsed())
    except RuntimeError, e:
        print e

