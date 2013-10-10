""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

from fabric.api import *
import hosts

swiftrepos = hosts.proxies


def add_gfs_user(adminuser, adminkey, user, group, key):

	for repo, addr in swiftrepos.iteritems():
		print repo, addr
