
import sys
import urllib
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


def parse_url_query_params(url):
  return urlparse.parse_qs(urlparse.urlparse(url).query)


def get_geni_auth_session(uname, password, idprovider):

  geelogin_url = 'http://gee-project.org'
  geeauth_url = 'http://gee-project.org/auth/openid'
  portallogin_url = 'https://portal.geni.net/Shibboleth.sso/Login'

  # set up sslv3 adapter for shibboleth authentication
  session = requests.Session()
  session.mount('https://', RequestsSSLv3Adapter())

  # get cookie for gee login
  resp = session.get(geelogin_url)

  # get identity provider list so we can grab the correct url
  idproviders = get_geni_identity_providers()
  try: idprovider_url = idproviders[idprovider]
  except KeyError:
    print 'ID Provider %s, can not be found' % (idprovider)
    return False

  # start the openid protocol by querying the gee auth page
  args = {'openid_identifier': 'https://portal.geni.net/server/server.php'}
  resp = session.post(geeauth_url, data=args)
  returl = parse_url_query_params(resp.url)['return'][0]

  # get the geni portal page with the required login params
  retparams = parse_url_query_params(returl)
  params = {'SAMLDS': retparams['SAMLDS'][0], 'target': retparams['target'][0], 'entityID': idprovider_url}
  heads = {'Referer': resp.url}
  resp = session.get(portallogin_url, params=params, headers=heads)
  
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

  # confirm send information back to geni portal
  confirmform = BeautifulSoup(resp.text).find('form')
  confirm_auth_url = confirmform.get('action')
  confirm_response = confirmform.find('input', attrs={'name':'save'}).get('value')
  resp = session.post(confirm_auth_url, data={'save':confirm_response}, headers={'Referer':resp.url})

  # return if the request was successful, if so we are logged in!
  return resp.ok