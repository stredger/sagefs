""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

class SageHost():
  def __init__(self, host, port):
    self.host = host
    self.port = port


class SwiftHost(SageHost):
  def __init__(self, host, port, user, group, key):
    SageHost.__init__(self, host, port)
    self.user = user
    self.group = group
    self.key = key

  def get_authv1_url(self):
    """ Given a host will generate the auth url required by swift """
    return 'http://%s:%s/auth/v1.0' % (self.host, self.port)


class MongoHost(SageHost):
  def __init__(self, host, port, database, collection):
    SageHost.__init__(self, host, port)
    self.database = database
    self.collection = collection




# a dictionary of all the swift proxies in sage
swift = {
  # 'savi':SwiftHost('142.104.64.68', 8080, 'savant', 'savant', 'savant'),
  'swift':SwiftHost('a.microbe.vikelab.emulab.net', 8080, 'savant', 'savant', 'savant'),
}

# mongo instances
mongo = {
  # 'local':MongoHost('localhost', 27017, 'Sage', 'fsdata')
  'mongo':MongoHost('a.microbe.vikelab.emulab.net', 27017, 'Sage', 'fsdata')
}
