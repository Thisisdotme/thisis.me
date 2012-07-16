import logging
import urlparse
import urllib
import urllib2
import oauth2 as oauth
import json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from tim_commons.oauth import make_request
from tim_commons.request_with_method import RequestWithMethod

from timmobile import oAuthConfig
from urllib2 import HTTPError
from timmobile.globals import DBSession

log = logging.getLogger(__name__)


# ??? TODO - these need to go somewhere else
FEATURE = 'twitter'

@view_config(route_name='twitter', request_method='GET', renderer='timmobile:templates/oauth.pt', permission='author')
def get_twitter(request):

  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)

  # Query the API for installed features
  try:
    req = urllib2.Request('%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authorName))
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
    request.session.flash('Your Twitter account is enabled.')
    return HTTPFound(location=request.route_path('account_details',featurename=FEATURE))
    
  return { 'feature':'Twitter',
           'url' : request.route_url('twitter'),
           'api_endpoint':request.registry.settings['mi.api.endpoint']}
  
@view_config(route_name='twitter', request_method='POST', permission='author')
def post_twitter(request):

  consumer_key = oAuthConfig[FEATURE]['key']
  consumer_secret = oAuthConfig[FEATURE]['secret']
  consumer = oauth.Consumer(consumer_key, consumer_secret)
  client = oauth.Client(consumer)
  
  # Step 1: Get a request token. This is a temporary token that is used for
  # having the user authorize an access token and to sign the request to obtain
  # said access token.

  callback = request.route_url('twitter_callback')
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


@view_config(route_name='twitter_callback', request_method='GET', permission='author')
def twitter_callback(request):
  
  # the oauth_token is request as a query arg; the auth_token_secret is in session store
  oauth_token = request.params['oauth_token']
  oauth_token_secret = request.session['oauth_token_secret']

  oauth_verifier = request.params['oauth_verifier']
  
  # Step 3: Once the consumer has redirected the user back to the oauth_callback
  # URL you can request the access token the user has approved. You use the
  # request token to sign this request. After this is done you throw away the
  # request token and use the access token returned. You should store this
  # access token somewhere safe, like a database, for future use.
  consumer_key = oAuthConfig[FEATURE]['key']
  consumer_secret = oAuthConfig[FEATURE]['secret']
  consumer = oauth.Consumer(consumer_key, consumer_secret)
  token = oauth.Token(oauth_token,oauth_token_secret)
  client = oauth.Client(consumer, token)

  token.set_verifier(oauth_verifier)

  resp, content = client.request(oAuthConfig[FEATURE]['access_token_url'], "POST")
  access_token = dict(urlparse.parse_qsl(content))

  # these are the real deal and need to be stored securely in the DB
  oauth_token = access_token['oauth_token']
  oauth_token_secret = access_token['oauth_token_secret']

  token = oauth.Token(oauth_token,oauth_token_secret)
  client = oauth.Client(consumer, token)

  userInfoJSON = json.loads(make_request(client,'https://api.twitter.com/1/account/verify_credentials.json').decode('utf-8'))

  json_payload = json.dumps({'access_token':oauth_token,'access_token_secret':oauth_token_secret,'service_author_id': userInfoJSON['id']})
  headers = {'Content-Type':'application/json; charset=utf-8'}
  req = RequestWithMethod('%s/v1/authors/%s/services/%s' %
                            (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE),
                          'PUT',
                          json_payload,
                          headers)
  try:
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  except HTTPError, e:
    # TODO: handle errors more gracefully here (caused by, e.g., API S3 bucket not existing)
    print e.read()

  try:
    request.session['twitter_access_token'] = oauth_token
    request.session['twitter_access_token_secret'] = oauth_token_secret
  except Exception, e:
    print e
    
  request.session.flash('Your Twitter account has been successfully added.')
  return HTTPFound(location=request.route_path('newsfeed'))
