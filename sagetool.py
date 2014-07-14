
import sagefs
import sys


fs = None
def connect_to_sage():
	global fs
	fs = sagefs.SageFS()

def check_fs():
	#if fs is None:
	return
	connect_to_sage('savant', 'savant', 'savant')
		#raise sagefs.SageFSNotConnectedException(
		#	'No SageFS. Try calling connect_to_sage(...)!')	


def quick_hash(s):
	sum = 0
	for c in s: sum += ord(c)
	return sum

def choose_fs_with_hash(s):
	return fs.sites[quick_hash(s) % len(fs.sites)]

def parse_path(path):
	try:
		location, resource = fs.split_location_from_path(path)
		if location in fs.sites: return path
	except sagefs.SageFSInvalidPathException: pass
	location = choose_fs_with_hash(path)
	if path[0] is not '/': path = '%s%s' % ('/', path) 
	path = '/%s%s' % (location, path)
	return path

def read(path, create=False):
	check_fs()
	path = parse_path(path)
	try: 
		f = fs.open(path, create=create)
		print f.read()
		f.close()
	except sagefs.SageFSFileNotFoundException, e:
		print 'File Not Found'

def write(path, data, create=False, append=True):
	check_fs()
	path = parse_path(path)
	try:
		f = fs.open(path, create=create)
		if append: f.seek(0, 2) # 2 is seek end
		# dont sync on write as we will sync on close
		f.write(data, sync=False)
		f.close()
		return path
	except sagefs.SageFSFileNotFoundException, e:
		print 'File Not Found'

def usage():
	print 'sagetools.py <read|write> <path> <data if write>'


if __name__ == "__main__":
	connect_to_sage()

	try:
		cmd = sys.argv[1]
		path = sys.argv[2]
		if cmd in 'write':
			write(path, sys.argv[3], True)
		elif cmd in 'read':
			read(path, True)
	except IndexError:
		usage()
		sys.exit(-1)
