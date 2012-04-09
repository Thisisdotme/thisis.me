import logging
import urllib
import urllib2
import json
from datetime import datetime
 
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from mi_url.RequestWithMethod import RequestWithMethod

from timmobile.exceptions import UnexpectedAPIResponse, GenericError
from timmobile import oAuthConfig
from timmobile.globals import DBSession

log = logging.getLogger(__name__)

FEATURE = 'googleplus'


def verify_googlePlus_access_token(googlePlus_access_token):

  validToken = True

  # We have a token, validate that it's valid
  log.info('Verifying googlePlus token')

  return validToken


def get_googlePlus_info(request):

  # the presumption is that the feature already exists.  If it doesn't then this function
  # should not have been called
  req = urllib2.Request('%s/v1/authors/%s/features/%s' %
                          (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE))
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  refreshToken = resJSON['access_token']
  if not refreshToken:
    raise UnexpectedAPIResponse('missing access_token for %s for author %s' % (FEATURE,authenticated_userid(request)))

  userId = resJSON['auxillary_data']['id']

  # let's exchange the refresh token for an access token
  apiKey = oAuthConfig[FEATURE]['key']
  apiSecret = oAuthConfig[FEATURE]['secret']
  queryArgs = urllib.urlencode([('client_id',apiKey),
                                ('client_secret',apiSecret),
                                ('refresh_token',refreshToken),
                                ('grant_type','refresh_token')])
  req = urllib2.Request(oAuthConfig[FEATURE]['oauth_exchange_url'],queryArgs)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  accessToken = resJSON['access_token']

  if not verify_googlePlus_access_token(accessToken):
    accessToken = None

  return accessToken, userId


# GET
#
@view_config(route_name='googleplus', request_method='GET', renderer='timmobile:templates/oauth.pt', permission='author')
def get_googlePlus(request):
  
  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)

  userId = accessToken = None

  if 'googlePlus_access_token' in request.session:

    accessToken = request.session['googlePlus_access_token']
    userId = request.session['googlePlus_user_id']
    if not verify_googlePlus_access_token(accessToken):
      accessToken = None
      del request.session['googlePlus_access_token']
      del request.session['googlePlus_user_id']
     
  else:

    # Query the API for installed features
    try:
      req = urllib2.Request('%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authorName))
      res = urllib2.urlopen(req)
      resJSON = json.loads(res.read())
    except urllib2.URLError, e:
      log.error(e.reason)
      raise
    except Exception, e:
      log.error(e)
      raise
  
    # Check if the feature we're trying to add is listed
    # ??? TODO - need better handling of feature already existing
    if len([feature for feature in resJSON['features'] if feature['name'] == FEATURE]) == 1:

      accessToken, userId = get_googlePlus_info(request)
  
      request.session['googlePlus_access_token'] = accessToken
      request.session['googlePlus_user_id'] = userId

  # redirect to add confirmation page if we don't have a valid access token
  if not accessToken:
    return {'feature':'GooglePlus',
            'url' : request.route_url('googleplus'),
            'api_endpoint':request.registry.settings['mi.api.endpoint']}
  else:
    request.session.flash('You have already added the Google+ feature.')
    return HTTPFound(location=request.route_path('account_details',featurename=FEATURE))

# POST
#
@view_config(route_name='googleplus', request_method='POST', permission='author')
def post_googlePlus(request):

  print request.route_url('googleplus_callback')
  
  apiKey = oAuthConfig[FEATURE]['key']
  queryArgs = urllib.urlencode([('client_id',apiKey),
                                ('redirect_uri',request.route_url('googleplus_callback'))])
  url = oAuthConfig[FEATURE]['oauth_url'] + queryArgs

  return HTTPFound(location=url)


@view_config(route_name='googleplus_callback', request_method='GET')
def googlePlus_callback(request):
  
  authorName = authenticated_userid(request)

  code = request.params.get('code')
  if code:
  
    print 'code => %s' % code

    # let's exchange the authorization code for an access token and a refresh token
    apiKey = oAuthConfig[FEATURE]['key']
    apiSecret = oAuthConfig[FEATURE]['secret']
    queryArgs = urllib.urlencode([('code',code),
                                  ('client_id',apiKey),
                                  ('client_secret',apiSecret),
                                  ('redirect_uri',request.route_url('googleplus_callback')),
                                  ('grant_type','authorization_code')])

    req = urllib2.Request(oAuthConfig[FEATURE]['oauth_exchange_url'],queryArgs)

    try:
      res = urllib2.urlopen(req)
      resJSON = json.loads(res.read())
    except urllib2.URLError, e:
      print 'urlopen failed'

    accessToken = resJSON['access_token']
    refreshToken = resJSON['refresh_token']

  else:
    error = request.params.get('error')
    log.error('Google+ oauth failed: %s' % error)
    raise GenericError(error)

  # now let's get some information about the user -- namely their id
  req = urllib2.Request('https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s' % accessToken)
  res = urllib2.urlopen(req)
  userInfoJSON = json.loads(res.read())

  userId = userInfoJSON['id']

  # add the feature via the API
  json_payload = json.dumps({'access_token':refreshToken,'auxillary_data':{'id':userId}})
  headers = {'Content-Type':'application/json; charset=utf-8'}
  req = RequestWithMethod('%s/v1/authors/%s/features/%s' %
                            (request.registry.settings['mi.api.endpoint'],authorName,FEATURE),
                          'PUT',
                          json_payload,
                          headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  log.info("Added Google+ feature for author %s" % authorName)

  # store the access-token and user-id in the session
  request.session['googlePlus_access_token'] = accessToken
  request.session['googlePlus_user_id'] = userId

  request.session.flash('Your Google+ feature has been successfully added.')

  return HTTPFound(location=request.route_path('newsfeed'))
