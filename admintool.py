""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

from fabric.api import *
import hosts
import sys

machines = [m.host for m in hosts.swift.values()]
env.roledefs = {
	'machines':machines
}
env.key_filename = '~/.ssh/st_rsa'


def add_sagefs_user(adminkey, user, group, key):
	run('swauth-add-user -A http://%s:8080/auth -K %s -a %s %s %s'
		% (env.host_string, adminkey, group, user, key))
		

def check_user(user, group, key, fromlocal=False):
	if fromlocal: cmd = local
	else: cmd = run

	cmd('swift -A http://%s:8080/auth/v1.0 -U %s:%s -K %s stat' 
		% (env.host_string, group, user, key))


if __name__ == "__main__":
	#if len(sys.argv) > 6:

	execute(add_sagefs_user, 'stepheniscool', 'sagefs', 'stredger', 'thebestpass', hosts=machines)
	execute(check_user, 'sagefs', 'stredger', 'thebestpass', hosts=machines)
