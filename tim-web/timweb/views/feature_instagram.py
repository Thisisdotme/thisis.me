import logging
import urllib2
import json
from datetime import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from instagram import client

from mi_url.RequestWithMethod import RequestWithMethod

from timweb.exceptions import GenericError
from timweb.exceptions import UnexpectedAPIResponse
from timweb import oAuthConfig

# ??? TODO - these need to come from somewhere else
FEATURE = 'instagram'

log = logging.getLogger(__name__)

@view_config(route_name='instagram', request_method='GET', renderer='timweb:templates/instagram.pt', permission='author')
def get_instagram(request):

  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)
  
  # Query the API for installed features
  try:
    req = RequestWithMethod('http://%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authorName), 'GET')
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  except Exception, e:
    log.error(e)
    raise e

  # Check if the feature we're trying to add is listed
  # ??? TODO - need better handling of feature already existing
  if len([feature for feature in resJSON['features'] if feature['name'] == FEATURE]) == 1:
    request.session.flash('You have already added the Instagram feature.')
    return HTTPFound(location=request.route_path('instagram_confirmation'))
    
  return { 'feature':'Instagram', 'url' : request.route_url('instagram'), 'title':'Instagram Feature' }

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
  req = RequestWithMethod('http://%s/v1/authors/%s/features/%s' % 
                                                    (request.registry.settings['mi.api.endpoint'],authorName,FEATURE), 
                                            'PUT',
                                            json_payload,
                                            headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  request.session['instagram_access_token'] = access_token
  
  request.session.flash('The Instagram feature has been successfully added.')
  return HTTPFound(location=request.route_path('instagram_confirmation'))


@view_config(route_name='instagram_confirmation', request_method='GET', renderer='timweb:templates/instagram_confirmation.pt')
def instagram_confirmation(request):
  
  # query the api for some feature events to display to the user
  req = urllib2.Request('http://%s/v1/authors/%s/features/%s/featureEvents' % 
                          (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE)) 
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  photos = []
  for event in resJSON['events']:
    image = event['content']['auxillary_data']['images']['thumbnail']['url']
    title = event['content'].get('label','')
    timestamp = datetime.utcfromtimestamp(event['create_time'])
    photos.append('<p>%s, created: %s<br/><img src="%s"/></p>' % (title,timestamp.isoformat(),image))

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return{'content':''.join(photos),'message':message, 'title':'Instagram Feature'}
  
