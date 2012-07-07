import logging
import datetime
import urllib2
import json
 
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from errors import UnexpectedAPIResponse

import flickrapi

from tim_commons.request_with_method import RequestWithMethod

log = logging.getLogger(__name__)

api_key = 'c407ceb64f7714f1120809ec7c246b86'
api_secret = '2c41d2f4e5378314'

FEATURE = 'flickr'

def verify_flickr_access_token(flickr_access_token):

  validToken = True

  # We have a token, validate that it's valid
  log.info('Verifying flickr token')

  f = flickrapi.FlickrAPI(api_key,api_secret,token=flickr_access_token,store_token=False)

  try:
    f.auth_checkToken()
  except flickrapi.FlickrError:
    validToken = False

  return validToken

def get_flickr_access_token(request):

  req = urllib2.Request('http://%s/v1/authors/%s/features/%s' % 
                              (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE))
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  # ??? TODO - enhance the error handling
  access_token = resJSON['access_token']
  if not access_token:
    raise UnexpectedAPIResponse('missing access_token for Instagram for author %s' % authenticated_userid(request))

  if not verify_flickr_access_token(access_token):
    access_token = None

  return access_token

  
@view_config(route_name='flickr', request_method='GET', renderer='timweb:templates/flickr.pt', permission='author')
def get_flickr(request):
  
  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)

  flickr_access_token = None

  if 'flickr_access_token' in request.session:
    flickr_access_token = request.session['flickr_access_token']
    if not verify_flickr_access_token(flickr_access_token):
      flickr_access_token = None
      del request.session['flickr_access_token']
     
  else:
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
      flickr_access_token = get_flickr_access_token(request)      
  
  if not flickr_access_token:
    return {'feature':'Flickr', 'url' : request.route_url('flickr')}
  else:

    request.session['flickr_access_token'] = flickr_access_token
    
    request.session.flash('You have already added the Flickr feature.')
    return HTTPFound(location=request.route_path('flickr_confirmation'))

@view_config(route_name='flickr', request_method='POST', permission='author')
def post_flickr(request):
  
  f = flickrapi.FlickrAPI(api_key,api_secret,token=None,store_token=False)
  
  # No valid token, so redirect to Flickr
  authorName = authenticated_userid(request)
  log.info('get_flickr - adding feature for author: %s' % authorName)
  log.info('Redirecting user to Flickr to get frob')
  url = f.web_login_url(perms='read')
  return HTTPFound(location=url)


@view_config(route_name='flickr_callback', request_method='GET', renderer='timweb:templates/confirmation.pt')
def flickr_callback(request):
  
  print 'flickr_callback'

  authorName = authenticated_userid(request)

  frob = request.params.get('frob')
  
  f = flickrapi.FlickrAPI(api_key,api_secret,token=None,store_token=False)

  flickr_access_token = f.get_token(frob)

  json_payload = json.dumps({'access_token':flickr_access_token})
  headers = {'Content-Type':'application/json; charset=utf-8'}      
  req = RequestWithMethod('http://%s/v1/authors/%s/features/%s' % 
                                  (request.registry.settings['mi.api.endpoint'],authorName,FEATURE), 
                          'PUT',
                          json_payload,
                          headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  log.info("Added Flickr feature for author %s" % authorName)
    
  request.session['flickr_access_token'] = flickr_access_token
  
  request.session.flash('The Flickr feature has been successfully added.')
  return HTTPFound(location=request.route_path('flickr_confirmation'))
    

@view_config(route_name='flickr_confirmation', request_method='GET', renderer='timweb:templates/flickr_confirmation.pt')
def flickr_confirmation(request):

  photos = []
    
  try:

    access_token = request.session['flickr_access_token']

    flickr = flickrapi.FlickrAPI(api_key,api_secret,token=access_token,store_token=False,format='json')

    today = datetime.date.today()
    min_date = today - datetime.timedelta(14)   # within the past 14 days

    response = flickr.photos_recentlyUpdated(min_date=min_date,nojsoncallback=1)
    responseObj = json.loads(response)
    
    list = responseObj['photos']['photo']
    
    for photo in list:

      id = photo['id']
      photoSizes = json.loads(flickr.photos_getSizes(photo_id=id,nojsoncallback=1))

      thumbnails = [thumbnail for thumbnail in photoSizes['sizes']['size'] if thumbnail['label'] == 'Small']
                    
      url = thumbnails[0]['source']
      print thumbnails[0]['url']

      photos.append('<img src="%s"/><br>' % url)
    
  except Exception, e:
    print "ERROR:"
    print e

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return{'message':message,'content':''.join(photos)}
  
