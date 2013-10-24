""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

from fabric.api import *
import hosts

swiftrepos = hosts.proxies

env.roledefs = {
	'machines':swiftrepos.values()
}
env.key_filename = '~/.ssh/st_rsa'


def add_gfs_user(adminuser, adminkey, user, group, key):

	for repo, addr in swiftrepos.iteritems():
		print repo, addr



@roles('machines')
def test_hosts():
	run('echo running')


execute(test_hosts)
