import logging
import urlparse
import urllib
import urllib2
import oauth2 as oauth
import json
from datetime import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from mi_url.RequestWithMethod import RequestWithMethod
from mi_utils.oauth import make_request

from timmobile.exceptions import UnexpectedAPIResponse
from timmobile import oAuthConfig
from timmobile.globals import DBSession

log = logging.getLogger(__name__)


# ??? TODO - these need to come from somewhere else
FEATURE = 'linkedin'

@view_config(route_name='linkedin', request_method='GET', renderer='timmobile:templates/oauth.pt', permission='author')
def get_linkedin(request):

  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)

  # Query the API for installed features
  try:
    req = urllib2.Request('%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authenticated_userid(request)))
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  except urllib2.URLError, e:
    log.error(e)
    raise
  except Exception, e:
    log.error(e)
    raise

  # Check if the feature we're trying to add is listed
  # ??? TODO - need better handling of feature already existing
  if len([feature for feature in resJSON['features'] if feature['name'] == FEATURE]) == 1:
    request.session.flash('You have already added the LinkedIn feature.')
    return HTTPFound(location=request.route_path('account_details',featurename=FEATURE))
    
  return { 'feature':'LinkedIn',
           'url' : request.route_url('linkedin'),
           'api_endpoint':request.registry.settings['mi.api.endpoint'] }
  
@view_config(route_name='linkedin', request_method='POST', permission='author')
def post_linkedin(request):

  consumer_key = oAuthConfig[FEATURE]['key']
  consumer_secret = oAuthConfig[FEATURE]['secret']
  consumer = oauth.Consumer(consumer_key, consumer_secret)
  client = oauth.Client(consumer)
  
  # Step 1: Get a request token. This is a temporary token that is used for
  # having the user authorize an access token and to sign the request to obtain
  # said access token.

  callback = request.route_url('linkedin_callback')
  resp, content = client.request(oAuthConfig[FEATURE]['request_token_url'], "POST", body=urllib.urlencode({'oauth_callback':callback}))
  if resp['status'] != '200':
      raise Exception("Invalid response %s (%s)." % (resp['status'], content))
  
  request_token = dict(urlparse.parse_qsl(content))
  
#  print "Request Token:"
#  print "    - oauth_token             = %s" % request_token['oauth_token']
#  print "    - oauth_token_secret      = %s" % request_token['oauth_token_secret']
#  print "    - oauth_callback_confirmed = %s" % request_token['oauth_callback_confirmed']
#  print

  # Step 2: Redirect to the provider.

  request.session['oauth_token_secret'] = request_token['oauth_token_secret']

  redirectURL = "%s?oauth_token=%s" % (oAuthConfig[FEATURE]['authorize_url'], request_token['oauth_token'])
  
  return HTTPFound(location=redirectURL)


@view_config(route_name='linkedin_callback', request_method='GET')
def linkedin_callback(request):
  
  # the oauth_token is request as a query arg; the auth_token_secret is in session store
  oauth_token = request.params['oauth_token']
  oauth_token_secret = request.session['oauth_token_secret']

  oauth_verifier = request.params['oauth_verifier']
  
  # Step 3: Once the consumer has redirected the user back to the oauth_callback
  # URL you can request the access token the user has approved. You use the
  # request token to sign this request. After this is done you throw away the
  # request token and use the access token returned. You should store this
  # access token somewhere safe, like a database, for future use.
  consumer = oauth.Consumer(oAuthConfig[FEATURE]['key'], oAuthConfig[FEATURE]['secret'])
  
  token = oauth.Token(oauth_token,oauth_token_secret)
  token.set_verifier(oauth_verifier)

  client = oauth.Client(consumer, token)
  
  resp, content = client.request(oAuthConfig[FEATURE]['access_token_url'], "POST")
  access_token = dict(urlparse.parse_qsl(content))

  # these are the real deal and need to be stored securely in the DB
  accessToken = access_token['oauth_token']
  accessTokenSecret = access_token['oauth_token_secret']

  # Create our OAuth consumer instance
  token = oauth.Token(key=accessToken,secret=accessTokenSecret)
  client = oauth.Client(consumer, token)

  response = make_request(client,'http://api.linkedin.com/v1/people/~:(id)',{'x-li-format':'json'})
  respJSON = json.loads(response)
  linkedinId = respJSON['id']

  json_payload = json.dumps({'access_token': accessToken, 'access_token_secret': accessTokenSecret, 'service_author_id': linkedinId})
  headers = {'Content-Type':'application/json; charset=utf-8'}
  url = '{0}/v1/authors/{1}/services/{2}'.format(request.registry.settings['mi.api.endpoint'], authenticated_userid(request), FEATURE)
  log.info(url)
  req = RequestWithMethod(url,
                          'PUT',
                          json_payload,
                          headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  try:
    request.session['linkedin_access_token'] = accessToken
    request.session['linkedin_access_token_secret'] = accessTokenSecret
  except Exception, e:
    print e
    
  request.session.flash('Your LinkedIn feature has been successfully added.')
  return HTTPFound(location=request.route_path('newsfeed'))
