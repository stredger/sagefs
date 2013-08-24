
import sys
sys.path.append('..')
sys.path.append('.')
import os
import gfs

host = gfs.swiftrepos.values()[0]
fs = gfs.SwiftFS(gfs.get_authv1_url(host), 'savant', 'savant', 'savant')


print "======== Testing in mem file ========"

fname = 'hello.txt'
f = fs.open(fname, True, True)
if not f:
    print "Failed to open in mem file"
    sys.exit()
print "Opened in mem file %s" % (fname)

writelist = ['hello', 'man']
f.writelines(writelist)
f.seek(0)
print "wrote to %s file, and read %s" % (writelist, f.read())

writestr = 'yea yea yea'
f.write(writestr)
f.seek(0)
print "wrote to %s file, and read %s" % (writestr, f.read())

f.todisk(fname)
f.close()
print "Put %s to disk" % (fname)

f = open(fname)
print "Read file %s, from disk. %s" % (fname, f.read)
f.close()
os.remove(fname)


print "======== Testing on disk file ========"

fname = 'hello.txt'
f = fs.open(fname, True, False)
if not f:
    print "Failed to open on disk file"
    sys.exit()
print "Opened in mem file %s" % (fname)

writelist = ['hello', 'man']
f.writelines(writelist)
f.seek(0)
print "wrote %s to file, and read %s" % (writelist, f.read())

writestr = 'yea yea yea'
f.write(writestr)
f.seek(0)
print "wrote %s to file, and read %s" % (writestr, f.read())

f.todisk(fname)
f.close()
print "Put %s to disk" % (fname)

f = open(fname)
print "Read file %s, from disk. %s" % (fname, f.read())
f.close()
os.remove(fname)
