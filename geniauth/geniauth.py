
import requests
from BeautifulSoup import BeautifulSoup
import json
import urlparse


# We use this to force requests to use a specific ssl version
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

class RequestsSSLv3Adapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=ssl.PROTOCOL_SSLv3)


def get_geni_identity_providers():
  provider_url = 'https://portal.geni.net/Shibboleth.sso/DiscoFeed'
  s = requests.Session()
  r = s.get(provider_url)
  rawproviders = json.loads(r.text)
  providers = {}
  for rp in rawproviders:
    providers[rp['DisplayNames'][0]['value']] = rp['entityID']
  return providers

idproviders = {}

def set_idproviders():
  global idproviders
  idproviders = get_geni_identity_providers()

def get_idprovider_url(idprovider, retry=True):
  # only get the idproviders when we have a key error as 
  #  it takes a while to get them
  try: return idproviders[idprovider]
  except KeyError, e:
    if retry:
      set_idproviders()
      return get_idprovider_url(idprovider, False)
    raise e


def parse_url_query_params(url):
  return urlparse.parse_qs(urlparse.urlparse(url).query)



def authenticate_with_geni(uname, password, idprovider):
  """ Authenticate with GEE via the openid protocol. 
  We actually do two redirects here: GEE -> GENI Portal -> Open id provider 
  We could technically go straight to the GENI Portal but we area really
  related to the GEE so if somehow the GEE protocol changes we dont have to 
  change anything here. Also the gee uses a really nice library for openid 
  auth so we can piggyback on that """

  genilogin_url = 'https://portal.geni.net/secure/home.php'


  # set up sslv3 adapter for shibboleth authentication
  session = requests.Session()
  session.mount('https://', RequestsSSLv3Adapter())

  # get identity provider list so we can grab the correct url
  try: idprovider_url = get_idprovider_url(idprovider)
  except KeyError:
    # stdout shows up in the swift log.. as info though
    print 'ID Provider %s, can not be found' % (idprovider)
    return False

  resp = session.get(genilogin_url)
  returl = parse_url_query_params(resp.url)['return'][0]

  # get the geni portal page with the required login params
  retparams = parse_url_query_params(returl)
  params = {'SAMLDS': retparams['SAMLDS'][0], 'target': retparams['target'][0], 'entityID': idprovider_url}
  heads = {'Referer': resp.url}
  resp = session.get(returl, params=params, headers=heads)
  
  # actully attempt to log in with the id provider
  loginurl = resp.url
  formdata = {'j_username': uname, 'j_password': password}
  resp = session.post(resp.url, data=formdata, headers={'Referer':resp.url})

  # if the response url is still equal to the login url we have failed login
  if resp.url == loginurl:
    print 'Login attempt failed'
    return False

  # go back to the geni portal with a login token
  authform = BeautifulSoup(resp.text).find('form')
  auth_redirect_url = authform.get('action')
  auth_relay_state =  authform.find('input', attrs={'name':'RelayState'}).get('value')
  auth_token = authform.find('input', attrs={'name':'SAMLResponse'}).get('value')
  resp = session.post(auth_redirect_url, data={'RelayState':auth_relay_state, 'SAMLResponse': auth_token})

  # return if the request was successful, if so we are logged in!
  return resp.ok