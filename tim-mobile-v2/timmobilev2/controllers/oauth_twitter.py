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

from timmobilev2 import tim_config
from urllib2 import HTTPError

log = logging.getLogger(__name__)


# ??? TODO - these need to go somewhere else
SERVICE = 'twitter'


@view_config(route_name='twitter', request_method='GET', renderer='timmobile:templates/oauth.pt')
def get_twitter(request):

  return {'feature': 'Twitter',
          'url': request.route_url(SERVICE),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='twitter', request_method='POST')
def post_twitter(request):

  consumer_key = tim_config['oauth'][SERVICE]['key']
  consumer_secret = tim_config['oauth'][SERVICE]['secret']

  consumer = oauth.Consumer(consumer_key, consumer_secret)
  client = oauth.Client(consumer)

  # Step 1: Get a request token. This is a temporary token that is used for
  # having the user authorize an access token and to sign the request to obtain
  # said access token.
  callback = request.route_url('twitter_callback')
  resp, content = client.request(tim_config['oauth'][SERVICE]['request_token_url'], "POST", body=urllib.urlencode({'oauth_callback': callback}))
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

  redirectURL = "{0}?oauth_token={1}".format(tim_config['oauth'][SERVICE]['authorize_url'], request_token['oauth_token'])

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
  consumer_key = tim_config['oauth'][SERVICE]['key']
  consumer_secret = tim_config['oauth'][SERVICE]['secret']
  consumer = oauth.Consumer(consumer_key, consumer_secret)
  token = oauth.Token(oauth_token, oauth_token_secret)
  client = oauth.Client(consumer, token)

  token.set_verifier(oauth_verifier)

  resp, content = client.request(tim_config['oauth'][SERVICE]['access_token_url'], "POST")
  access_token = dict(urlparse.parse_qsl(content))

  # these are the real deal and need to be stored securely in the DB
  oauth_token = access_token['oauth_token']
  oauth_token_secret = access_token['oauth_token_secret']

  token = oauth.Token(oauth_token, oauth_token_secret)
  client = oauth.Client(consumer, token)

  userInfoJSON = json.loads(make_request(client, 'https://api.twitter.com/1/account/verify_credentials.json').decode('utf-8'))

  json_payload = json.dumps({'access_token': oauth_token, 'access_token_secret': oauth_token_secret, 'service_author_id': userInfoJSON['id']})
  headers = {'Content-Type': 'application/json; charset=utf-8'}
  req = RequestWithMethod('%s/v1/authors/%s/services/%s' %
                            (tim_config['api']['endpoint'], authenticated_userid(request), SERVICE),
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
