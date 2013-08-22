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
    cexists = fs.container_exists(testgroup)
    fexists = fs.file_exists(fname)
    print "Container %s exists? %s\nFile %s exists? %s" % (testgroup, cexists, fname, fexists)

    f = fs.open(fname, True)
    print "Opened file %s with create flag" % (fname)

    fexists = fs.file_exists(fname)
    print "Now file %s exists? %s" % (fname, fexists)
    
    fstr = "what up suckas!"
    f.write(fstr, False)
    f.close()
    print "Wrote: '%s' to file and closed it" % (fstr)

    f = fs.open(fname)
    fdata = f.read()
    f.close()
    print "Re-opened %s, and read contents: '%s'" % (fname, fdata)

    fstat = fs.stat(fname)
    fsstat = fs.stat()
    print "Stats for filesystem: %s\nStats for file %s: %s" % (fsstat, fname, fstat)

    copyname = 'hello2.txt'
    fs.copy(fname, copyname)
    if not fs.file_exists(copyname):
        print "Copy failed"
        sys.exit()
    print "Copied % to %s" % (fname, copyname)

    listing = fs.list()
    print "Lised fs: %s" % (listing)

    try: fs.move(copyname, fname)
    except GFSFileExistsException: pass
    fs.move(copyname, fname, True)
    if fs.file_exists(copyname):
        print "Move failed"
        sys.exit()

    fs.remove(fname)
    if fs.file_exists(fname):
        print "Remove failed"
        sys.exit()
    print "Removed file %s" % (fname)
