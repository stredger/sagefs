''' 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
'''

''' Test for various SwiftFile functionality '''

import sys
sys.path += ['..', '.']
import os
import sagefs

from testcommon import *

name,host = sagefs.hosts.swift.items()[0]
print 'testing on %s' % (name)
fs = sagefs.SwiftFS(host.get_authv1_url(), host.group, host.user, host.key)


print '======== Testing in mem file ========'

fname = 'hello.txt'
try: fs.remove(fname)
except sagefs.SageFSFileNotFoundException: pass


testname = 'open mem'
f = fs.open(fname, True, True)
if not f:
  testfailed(testname)
  print 'Failed to open %s in mem' % (fname)
  sys.exit()
testpassed(testname)
print 'Opened %s in mem' % (fname)


testname = 'writelist mem'
writelist = ['hello', 'man']
f.writelines(writelist)
f.seek(0)
contents = f.read()
f.seek(0)
if not contents == ''.join(writelist):
  testfailed(testname)
  print 'write failed, contents: "%s" do not match what was written "%s"' % (contents, ''.join(writelist))
else:
  testpassed(testname)
  print 'wrote %s to %s, and read %s' % (writelist, fname, contents)


writestr = 'yea yea yea'
f.write(writestr)
f.seek(0)
contents = f.read()
f.seek(0)
if not contents == writestr:
  testfailed(testname)
  print 'write failed, contents: "%s" do not match what was written "%s"' % (contents, writestr)
else:
  testpassed(testname)
  print 'wrote %s to %s, and read %s' % (writestr, fname, contents)


testname = 'todisk mem'
f.todisk(fname)
f.close()
print 'Put %s to local disk' % (fname)
f = open(fname)
contents = f.read()
if not contents == writestr:
  testfailed(testname)
  print 'todisk read/write failed, contents: "%s" do not match what was written "%s"' % (contents, writestr)
else:
  testpassed(testname)
  print 'Read file %s, from disk. %s' % (fname, contents)
f.close()
os.remove(fname)



print '\n======== Testing on disk file ========'

fname = 'hello.txt'

try: fs.remove(fname)
except sagefs.SageFSFileNotFoundException: pass


testname = 'open disk'
f = fs.open(fname, True, False)
if not f:
  testfailed(testname)  
  print 'Failed to open on disk file'
  sys.exit()
testpassed(testname)
print 'Opened %s in mem' % (fname)


testname = 'writelines disk'
writelist = ['hello', 'man']
f.writelines(writelist)
f.seek(0)
contents = f.read()
f.seek(0)
if not contents == ''.join(writelist):
  testfailed(testname)
  print 'write failed, contents: "%s" do not match what was written "%s"' % (contents, ''.join(writelist))
else: 
  testpassed(testname)
  print 'wrote %s to %s, and read %s' % (writelist, fname, contents)


testname = 'write disk'
f.seek(0)
writestr = 'yea yea yea'
f.write(writestr)
f.seek(0)
contents = f.read()
f.seek(0)
if not contents == writestr:
  testfailed(testname)
  print 'write failed, contents: "%s" do not match what was written "%s"' % (contents, writestr)
else: 
  testpassed(testname)
  print 'wrote %s to %s, and read %s' % (writestr, fname, contents)


testname = 'todisk disk'
f.todisk(fname)
f.close()
print 'Put %s to disk' % (fname)

f = open(fname)
contents = f.read()
if not contents == writestr:
  testfailed(testname)
  print 'todisk read/write failed, contents: "%s" do not match what was written "%s"' % (contents, writestr)
else:
  testpassed(testname)
  print 'Read file %s, from disk. %s' % (fname, contents)
f.close()
os.remove(fname)

fs.remove(fname)