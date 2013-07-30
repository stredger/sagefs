
import sys
sys.path.append('..')
sys.path.append('.')

import gfs



#fs = gfs.GFS('savant', 'savant', 'savant')

#f = fs.open('/local/helo.txt', True)

fs = gfs.SwiftFS('http://localhost:8080/auth/v1.0', 'savant', 'savant', 'savant')


# print fs.list()
print fs.stat('h.txt')

f = fs.open('helo.txt', True)

# if not f:
#     sys.exit()

print f.readlines()


#sleep(100)
f.write('Dirty Marry\n')
# #print f.getvalue()
#f.seek(0)
#print f.readlines()
f.close()


#fs.remove('/local/helo.txt')
# f = fs.open('helo.txt')
# print f.readlines()
# f.close()
# print fs.localfiles

#fs.move( 'ello.txt', 'helo.txt')
