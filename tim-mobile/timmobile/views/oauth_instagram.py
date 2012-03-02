import logging
import urllib2
import simplejson as json
from datetime import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from instagram import client

from mi_url.RequestWithMethod import RequestWithMethod

from timmobile.exceptions import GenericError
from timmobile.exceptions import UnexpectedAPIResponse
from timmobile import oAuthConfig
from timmobile.globals import DBSession

# ??? TODO - these need to come from somewhere else
FEATURE = 'instagram'

log = logging.getLogger(__name__)

@view_config(route_name='instagram', request_method='GET', renderer='timmobile:templates/oauth.pt', permission='author')
def get_instagram(request):

  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)
  
  # Query the API for installed features
  try:
    req = RequestWithMethod('%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authorName), 'GET')
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  except Exception, e:
    log.error(e)
    raise e

  # Check if the feature we're trying to add is listed
  # ??? TODO - need better handling of feature already existing
  if len([feature for feature in resJSON['features'] if feature['name'] == FEATURE]) == 1:
    request.session.flash('Your Instagram account is active.')
    return HTTPFound(location=request.route_path('account_details',featurename=FEATURE))
    
  return { 'feature':'Instagram',
           'url' : request.route_url('instagram'),
           'api_endpoint':request.registry.settings['mi.api.endpoint'] }

@view_config(route_name='instagram', request_method='POST', permission='author')
def post_instagram(request):
  
  config = {'client_id': oAuthConfig[FEATURE]['key'],
            'client_secret': oAuthConfig[FEATURE]['secret'],
            'redirect_uri': request.route_url('instagram_callback') }
   
  unauthenticated_api = client.InstagramAPI(**config)
  
  redirectURL = unauthenticated_api.get_authorize_url(scope=["likes","comments"])

  return HTTPFound(location=redirectURL)


@view_config(route_name='instagram_callback', request_method='GET')
def instagram_callback(request):
  
  code = request.params.get('code')

  # ??? TODO - proper handling of error case
  if not code:
    raise GenericError('missing code query argument from Instagram callback')

  # Get author's login name
  authorName = authenticated_userid(request)
  
  config = {'client_id': oAuthConfig[FEATURE]['key'],
            'client_secret': oAuthConfig[FEATURE]['secret'],
            'redirect_uri': request.route_url('instagram_callback') }

  unauthenticated_api = client.InstagramAPI(**config)

  access_token = unauthenticated_api.exchange_code_for_access_token(code)
  
  # ??? TODO - proper handling of error case
  if not access_token:
    raise GenericError('no access_token returned from Instagram when exchanging code for access_token')

  json_payload = json.dumps({'access_token':access_token})
  headers = {'Content-Type':'application/json; charset=utf-8'}
  req = RequestWithMethod('%s/v1/authors/%s/features/%s' %
                                                    (request.registry.settings['mi.api.endpoint'],authorName,FEATURE),
                                            'PUT',
                                            json_payload,
                                            headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  request.session['instagram_access_token'] = access_token
  
  request.session.flash('Your Instagram account has been successfully added.')
  return HTTPFound(location=request.route_path('newsfeed'))
