
import sys
sys.path.append('..')
sys.path.append('.')

import gfs



fs = gfs.GFS('savant', 'savant', 'savant')

f = fs.open('/local/paul.txt', True)

#fs = gfs.SwiftFS('http://grack01.uvic.trans-cloud.net:8080/auth/v1.0', 'savant', 'savant', 'savant')
#print fs.stat_container('savant')

#print fs.stat()

#print fs.list('/local/')
#print fs.stat()
#fs.upload('gfs.py', '/local/')

#fs.open('hello.txt', True)
#fs.move('hi.txt', 'hello.txt', True)

#fs.copy('hello.txt', 'helo.txt', True)

#f = fs.open('hello.txt', True)
#f.todisk('hello.txt')

#if not f:
#    sys.exit()

#print f.readlines()


#sleep(100)
f.write('hi paul!!\n')
#print f.getvalue()
f.seek(0)
print f.readlines()
f.close()

#fs = gfs.GFS('savant', 'savant', 'savant')
#fs.remove('/local/helo.txt')
# f = fs.open('helo.txt')
# print f.readlines()
# f.close()

#fs.move( 'ello.txt', 'helo.txt')
