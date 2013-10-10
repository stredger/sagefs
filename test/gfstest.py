""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

""" 
A Test for various GFS functionality
"""

import sys
sys.path += ['..', '.']
import os
import gfs


fs = gfs.GFS('savant', 'savant', 'savant')

testloc = 'uvic'
testfile = 'hello.txt'

print "======== Testing stat() ========"
print fs.stat() # will test connections to all repos!
print fs.stat('/%s/' % (testloc))
print fs.stat('/%s/%s' % (testloc, testfile))

print "======== Testing list() ========"
print fs.list()
print fs.list('/%s/' % (testloc))
print fs.list('/%s/%s' % (testloc, testfile))

print "======== Testing open() & upload() ========"
newtestloc = 'savi'
teststr = 'sup mang'
f = fs.open('/%s/%s' % (testloc, testfile), True)
f.write(teststr)
f.todisk(testfile)
f.close()
fs.upload(testfile, '/%s/%s' % (newtestloc, testfile))
print "uploaded file to /%s/%s" % (newtestloc, testfile)
os.remove(testfile)

print "======== Testing copy() ========"
newtestfile = 'hi.txt'
fs.copy('/%s/%s' % (newtestloc, testfile), '/%s/%s' % (testloc, newtestfile))
fs.copy('/%s/%s' % (newtestloc, testfile), '/%s/%s' % (testloc, newtestfile), True)
print "copied file /%s/%s to /%s/%s" % (newtestloc, testfile, testloc, newtestfile)

print "======== Testing move() & remove() ========"
fs.move('/%s/%s' % (newtestloc, testfile), '/%s/%s' % (testloc, testfile), True)
fs.move('/%s/%s' % (testloc, newtestfile), '/%s/%s' % (testloc, testfile), True)
print "moved /%s/%s to /%s/%s" % (newtestloc, testfile, testloc, newtestfile)
print "also moved /%s/%s to /%s/%s" % (testloc, newtestfile, testloc, testfile)

fs.remove('/%s/%s' % (testloc, testfile))
print "removed /%s/%s" % (testloc, testfile)
