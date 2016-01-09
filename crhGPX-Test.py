# crhGPX-Test.py -- gpx utilities tests
# Copyright (c) 2015 CR Hailey
# v1.00 crh 17-jun-15 -- initial release

#!/usr/local/bin/python

#import re
#from math import floor, sqrt, pi, sin, cos, tan, atan2 as arctan2
#import datetime
#import time
#import numpy as np
#from StringIO import StringIO
import argparse

import crhGPX
from crhMap import *
from crhDebug import *
from crhString import *
import crhTimer


progName = 'crhGPX-Test'
inputF = 'crhGPX-Test.gpx'

# process arguments
parser = argparse.ArgumentParser(description="process map route gpx (GPS Exchange Format xml) data")
parser.add_argument('-i', '--input', action="store", dest="infile",
                    help='input filename with extension (eg: crhGPX-Test.gpx)')
args = parser.parse_args()
if args.infile:
    inputF = args.infile

# process data
print ''
gpxData = crhGPX.gpx(inputF)
ok = gpxData.validData()

if ok:
#    print gpxData.genXML(bsv = False).getvalue()
    print gpxData.genXML(bsv = True, track = True).getvalue()
    print gpxData.genBSV().getvalue()
    print gpxData.genStats().getvalue()
else:
    statusErrMsg('error', 'main', 'unable to process gpx file: {}'.format(inputF))

## tidy up

errTMsg('{} ending normally ({:06.2f}sec)'.format(getProgName(), crhTimer.timer.stop()))
