""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

swift = None
mongo = None

class SageHost():
  def __init__(self, host, port):
    self.host = host
    self.port = port


class SwiftHost(SageHost):
  def __init__(self, host, user, group, key, port=8080):
    SageHost.__init__(self, host, port)
    self.user = user
    self.group = group
    self.key = key

  def get_authv1_url(self):
    """ Given a host will generate the auth url required by swift """
    return 'http://%s:%s/auth/v1.0' % (self.host, self.port)


class MongoHost(SageHost):
  def __init__(self, host, database, collection, port=27017):
    SageHost.__init__(self, host, port)
    self.database = database
    self.collection = collection


def update_swift_host(host, user=None, group=None, key=None):
  if user: host.user = user
  if group: host.group = group
  if key: host.key = key

def update_all_swift_hosts(user=None, group=None, key=None):
  for host in swift.values():
    update_swift_host(host, user, group, key)




# a dictionary of all the swift proxies in sage
swift = {
  # 'vic':SwiftHost('142.104.17.135', 'admin', 'system', 'sagefs'),
  'tor':SwiftHost('142.150.208.220', 'admin', 'system', 'sagefs'),
  'carl':SwiftHost('134.117.57.138', 'admin', 'system', 'sagefs'),
  'local':SwiftHost('localhost', 'admin', 'system', 'sagefs'),
  # 'local':SwiftHost('localhost', 8080, 'stredger', 'GENI+Project+Office', None)
}

# mongo instances
mongo = {
  # 'local':MongoHost('localhost', 27017, 'Sage', 'fsdata')
  # 'mongo':MongoHost('localhost', 27017, 'Sage', 'fsdata') # cant funkin make this work with non localhost
}
