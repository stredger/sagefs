import sys
sys.path.append('..')
sys.path.append('.')

import gfs

testuser = 'savant'
testgroup = 'savant'
testkey = 'savant'

for host in gfs.swiftrepos.values():

    print "\n===== Testng host %s =====" % (host) 
    auth_url = gfs.get_authv1_url(host)
    fs = gfs.SwiftFS(auth_url, testgroup, testuser, testkey)
    print "Authenticated"

    fname = 'hello.txt'
    f = fs.open(fname, True)
    print "Opened file %s" % (fname)

    fstr = "what up suckas!"
    f.write(fstr, False)
    f.close()
    print "Wrote: '%s' to file and closed it" % (fstr)

    f = fs.open(fname)
    fdata = f.read()
    f.close()
    print "Re-opened %s, and read contents: '%s'" % (fname, fdata)
