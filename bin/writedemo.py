
import random
import string
import datetime
#import hosts
import sagetool
import time

ENDC = '\033[0m'
OKGREEN = '\033[92m'
OKBLUE = '\033[94m'

def colourize(path):
    if '2' in path: return OKGREEN + path + ENDC
    return OKBLUE + path + ENDC

def write_to_sage(path):
	t = str(datetime.datetime.now())
	path = sagetool.write(path, t, True, True)
	dat = sagetool.read(path)
	return 'Wrote %s to %s at %s' % (dat, colourize(path), str(datetime.datetime.now()))

def gen_random_filename(n=6):
	return '%s.txt' % (''.join(random.choice(string.lowercase) for i in range(n)))

def randomwrites():
	try:
		print write_to_sage(gen_random_filename())
	except Exception, e:
		print str(e)
            
def write_forever():
	sagetool.connect_to_sage()
	print 'Writing forever: ctrl-c to exit'
	try: 
		while True:
			randomwrites()
			#time.sleep(50) # assume 10 secs to do all requests
	except KeyboardInterrupt:
		print '\nBye!'

if __name__ == "__main__":

	write_forever()
