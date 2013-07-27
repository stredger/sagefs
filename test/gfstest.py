
import sys
sys.path.append('..')

import gfs

fs = gfs.SwiftFS('http://localhost:8080/auth/v1.0', 'savant', 'savant', 'savant')

f = fs.open('hello.txt')


print f.readlines()
f.write('helklo ando')
#print f.getvalue()
#f.seek(0)
#print f.readlines()
#f.close()

f = fs.open('hello.txt')
print f.readlines()

#print fs.localfiles
