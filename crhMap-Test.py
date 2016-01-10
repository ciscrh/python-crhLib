# crhMap-Test.py -- mapping utilities tests
# Copyright (c) 2016 CR Hailey
# v1.00 crh 07-jan-16 -- initial release

import crhMap as cm

cm.fatalException  = False # only sensible with bespoke exception handling code
print 'crhMap.py -- mapping utilities (tier 3) tests\n'

print '(53.17709 lat, -1.71328 lon) is a crossroads outside Youlgrave (SK19266448)...'
(east, north) = cm.wgs2osgb(53.17709, -1.71329)
print '\n1.0 east, north                    >> {}, {}'.format(east, north)

print "\n2.0 wgs2osgb(53.17709, -1.71329)   >> " + str(cm.wgs2osgb(53.17709, -1.71329))
print "    >> validCoords(wgs2osgb(53.17709, -1.71329)): {}".format(str(cm.validCoords(cm.wgs2osgb(53.17709, -1.71329))))
print "2.1 wgs2osgb(100.12345, 100.12345) >> " + str(cm.wgs2osgb(100.12345, 100.12345))
print "    >> validCoords(wgs2osgb(100.12345, 100.12345)): {}".format(str(cm.validCoords(cm.wgs2osgb(100.12345, 100.12345))))

print "\n3.0 ngr2osgb('SK19266448)')        >> " + str(cm.ngr2osgb('SK19266448'))
print "3.1 ngr2osgb('SK1926064482')       >> " + str(cm.ngr2osgb('SK1926064482'))

print "\n4.0 osgb2ngr(({}, {}), 4)  >> ".format(east, north) + cm.osgb2ngr((east, north), 4)
print "4.1 osgb2ngr(({}, {}), 6)  >> ".format(east, north) + cm.osgb2ngr((east, north), 6)
print "4.2 osgb2ngr(({}, {}), 8)  >> ".format(east, north) + cm.osgb2ngr((east, north), 8)
print "4.3 osgb2ngr((419260, 364482), 10) >> " + cm.osgb2ngr((419260, 364482), 10)
print "4.4 osgb2ngr(({}, {}))     >> ".format(east, north) + cm.osgb2ngr((east, north))
print "4.5 osgb2ngr((-704174, 4227357)) will generate an exception and continue..."
try:
    cm.osgb2ngr((-704174, 4227357))
except RuntimeError as re:
    print "RuntimeError trapped: {}".format(re)

print "\n5.0 osgb2wgs(({}, {}))     >> ".format(east, north) + str(cm.osgb2wgs(east, north))
print "5.1 osgb2wgs(('{}'))           >> ".format('SK1964') + str(cm.osgb2wgs('SK1964'))
print "    >> validNGR('SK1964'): {}".format(str(cm.validNGR('SK1926064482')))
print "5.2 osgb2wgs(('{}'))         >> ".format('SK192644') + str(cm.osgb2wgs('SK192644'))
print "5.3 osgb2wgs(('{}'))       >> ".format('SK19266448') + str(cm.osgb2wgs('SK19266448'))
print "5.4 osgb2wgs(('{}'))     >> ".format('SK1926064482') + str(cm.osgb2wgs('SK1926064482'))
print "    >> validNGR('SK1926064482'): {}".format(str(cm.validNGR('SK1926064482')))

print '\n6.0 deg2dms(1.33)    >> ' + str(cm.deg2dms(1.33))
print '6.0 deg2dms(1.3333)  >> ' + str(cm.deg2dms(1.3333))
print '6.2 deg2dms(1.99)    >> ' + str(cm.deg2dms(1.99))
print '6.3 deg2dms(1.9999)  >> ' + str(cm.deg2dms(1.9999))
print '6.4 deg2dms(-1.33)   >> ' + str(cm.deg2dms(-1.33))
print '6.5 deg2dms(-1.3333) >> ' + str(cm.deg2dms(-1.3333))
print '6.6 deg2dms(-1.99)   >> ' + str(cm.deg2dms(-1.99))
print '6.7 deg2dms(-1.9999) >> ' + str(cm.deg2dms(-1.9999))
print '6.8 deg2dms(5)       >> ' + str(cm.deg2dms(5))
print '6.9 deg2dms(-5)      >> ' + str(cm.deg2dms(-5))

print '\n7.0 dms2deg(deg2dms(1.33))    >> ' + str(cm.dms2deg(cm.deg2dms(1.33)))
print '7.1 dms2deg(deg2dms(1.3333))  >> ' + str(cm.dms2deg(cm.deg2dms(1.3333)))
print '7.2 dms2deg(deg2dms(1.99))    >> ' + str(cm.dms2deg(cm.deg2dms(1.99)))
print '7.3 dms2deg(deg2dms(1.9999))  >> ' + str(cm.dms2deg(cm.deg2dms(1.9999)))
print '7.4 dms2deg(deg2dms(-1.33))   >> ' + str(cm.dms2deg(cm.deg2dms(-1.33)))
print '7.5 dms2deg(deg2dms(-1.3333)) >> ' + str(cm.dms2deg(cm.deg2dms(-1.3333)))
print '7.6 dms2deg(deg2dms(-1.99))   >> ' + str(cm.dms2deg(cm.deg2dms(-1.99)))
print '7.7 dms2deg(deg2dms(-1.9999)) >> ' + str(cm.dms2deg(cm.deg2dms(-1.9999)))
print '7.8 dms2deg(deg2dms(5))       >> ' + str(cm.dms2deg(cm.deg2dms(5)))
print '7.9 dms2deg(deg2dms(-5))      >> ' + str(cm.dms2deg(cm.deg2dms(-5)))
print "\n8.0 ngr2osgb('ZZ2755072950') will generate an exception and continue..."
try:
    cm.ngr2osgb('ZZ2755072950')
except RuntimeError as re:
    print "RuntimeError trapped: {}".format(re)
print "    >> validNGR('ZZ2755072950'): {}".format(str(cm.validNGR('ZZ2755072950')))
cm.fatalException  = True  # the default value
print "8.1 ngr2osgb('ZZ2755072950') will now generate a fatal exception and exit..."
cm.ngr2osgb('ZZ2755072950')
# the following code will not execute (script terminated!)
print "    >> validNGR('ZZ2755072950'): {}".format(str(cm.validNGR('ZZ2755072950')))
