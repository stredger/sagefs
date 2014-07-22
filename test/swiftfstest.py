''' 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
'''

''' Test for various SwiftFS functionality, at all repos! '''

import sys
sys.path += ['..', '.']
import sagefs

fs = sagefs.SageFS()

for name,host in sagefs.hosts.swift.items():

    print '\n===== Testing host %s =====' % (name) 
    auth_url = host.get_authv1_url()
    fs = sagefs.SwiftFS(auth_url, host.group, host.user, host.key)
    print 'Authenticated'

    fname = 'hello.txt'
    cexists = fs.container_exists(host.user)
    fexists = fs.file_exists(fname)
    print 'Container %s exists? %s\nFile %s exists? %s' % (host.user, cexists, fname, fexists)

    f = fs.open(fname, True)
    print 'Opened file %s with create flag' % (fname)

    fexists = fs.file_exists(fname)
    print 'Now file %s exists? %s' % (fname, fexists)
    
    fstr = 'what up suckas!'
    f.write(fstr, False)
    f.close()
    print 'Wrote: "%s" to file and closed it' % (fstr)

    f = fs.open(fname)
    fdata = f.read()
    f.close()
    print 'Re-opened %s, and read contents: "%s"' % (fname, fdata)

    fstat = fs.stat(fname)
    fsstat = fs.stat()
    print 'Stats for filesystem: %s\nStats for file %s: %s' % (fsstat, fname, fstat)

    copyname = 'hello2.txt'
    fs.copy(fname, copyname, True)

    if not fs.file_exists(copyname):
        print 'Copy failed'
        sys.exit()
    print 'Copied %s to %s' % (fname, copyname)

    listing = fs.list()
    print 'Listed fs: %s' % (listing)

    try: fs.move(copyname, fname)
    except sagefs.SageFSFileExistsException: pass
    fs.move(copyname, fname, True)
    if fs.file_exists(copyname):
        print 'Move failed'
        sys.exit()

    fs.remove(fname)
    if fs.file_exists(fname):
        print 'Remove failed'
        sys.exit()
    print 'Removed file %s' % (fname)
