import logging
import urllib
import urllib2
from urlparse import parse_qs
from datetime import datetime
import json
 
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from tim_commons.request_with_method import RequestWithMethod

from timweb.exceptions import UnexpectedAPIResponse, GenericError
from timweb import oauth_config

log = logging.getLogger(__name__)

FEATURE = 'facebook'


def verify_facebook_access_token(facebook_access_token):

  validToken = True

  # We have a token, validate that it's valid
  log.info('Verifying facebook token')

  return validToken


def get_facebook_info(request):

  # the presumption is that the feature already exists.  If it doesn't then this function
  # should not have been called
  req = urllib2.Request('http://%s/v1/authors/%s/features/%s' % 
                              (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE)) 
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  # ??? TODO - enhance the error handling
  accessToken = resJSON['access_token']
  if not accessToken:
    raise UnexpectedAPIResponse('missing access_token for %s for author %s' % (FEATURE,authenticated_userid(request)))

  if not verify_facebook_access_token(accessToken):
    accessToken = None

  facebookUserId = resJSON['auxillary_data']['id']

  return accessToken, facebookUserId

  
@view_config(route_name='facebook', request_method='GET', renderer='timweb:templates/facebook.pt', permission='author')
def get_facebook(request):
  
  # first check if the author has already added this feature.
  
  # Get author's login name
  authorName = authenticated_userid(request)

  facebookUserId = facebookAccessToken = None

  if 'facebook_access_token' in request.session:

    facebookAccessToken = request.session['facebook_access_token']
    facebookUserId = request.session['facebook_user_id']
    if not verify_facebook_access_token(facebookAccessToken):
      facebookAccessToken = None
      del request.session['facebook_access_token']
      del request.session['facebook_user_id']
     
  else:

    # Query the API for installed features
    try:
      req = urllib2.Request('http://%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authorName))
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
      facebookAccessToken, facebookUserId = get_facebook_info(request)      
  
      request.session['facebook_access_token'] = facebookAccessToken
      request.session['facebook_user_id'] = facebookUserId

  # redirect to add confirmation page if we don't have a valid access token
  if not facebookAccessToken:
    return {'feature':'Facebook', 'url' : request.route_url('facebook'), 'title':'Facebook Feature'}
  else:

    request.session.flash('You have already added the Facebook feature.')
    return HTTPFound(location=request.route_path('facebook_confirmation'))

@view_config(route_name='facebook', request_method='POST', permission='author')
def post_facebook(request):

  api_key = oauth_config[FEATURE]['key']
  queryArgs = urllib.urlencode([('client_id',api_key),
                                ('redirect_uri',request.route_url('facebook_callback')),
                                ('scope','offline_access,read_stream,user_photos,user_checkins,user_events,user_groups,user_videos,user_about_me,user_education_history,user_status')])
  
  url = oauth_config[FEATURE]['oauth_url'] % queryArgs

  log.info('Redirecting user to Facebook to get authorization code')

  return HTTPFound(location=url)


@view_config(route_name='facebook_callback', request_method='GET', renderer='timweb:templates/confirmation.pt')
def facebook_callback(request):
  
  print 'facebook_callback'

  authorName = authenticated_userid(request)

  fbAccessToken = None
  fbUserId = None

  code = request.params.get('code')
  if code:
  
    print 'code => %s' % code
    
    # let's get the acces_token
    api_key = oauth_config[FEATURE]['key']
    api_secret = oauth_config[FEATURE]['secret']

    queryArgs = urllib.urlencode([('client_id',api_key),
                                  ('redirect_uri',request.route_url('facebook_callback')),
                                  ('client_secret',api_secret),
                                  ('code',code)])
    
    url = oauth_config[FEATURE]['access_token_url'] % queryArgs

    try:
      req = urllib2.Request(url)
      res = urllib2.urlopen(req)
      fbDict = parse_qs(res.read())

      fbAccessToken = fbDict['access_token'][0]

    except urllib2.URLError, e:
      log.error(e.reason)
      raise e
    
    # now let's get some information about the user -- namely their id
    req = urllib2.Request(oauth_config[FEATURE]['url'] % ('me',fbAccessToken))
    res = urllib2.urlopen(req)
    meJSON = json.loads(res.read())

    fbUserId = meJSON['id']
    
  else:
    error_reason = request.params.get('error_reason')
    error = request.params.get('error')
    error_description = request.params.get('error_description')
    msg = '%s - %s - %s' % (error_reason, error, error_description)
    log.error(msg)
    raise GenericError(msg)
  
  json_payload = json.dumps({'access_token':fbAccessToken,'auxillary_data':{'id':fbUserId}})
  headers = {'Content-Type':'application/json; charset=utf-8'}      
  req = RequestWithMethod('http://%s/v1/authors/%s/features/%s' % 
                                  (request.registry.settings['mi.api.endpoint'],authorName,FEATURE), 
                          'PUT',
                          json_payload,
                          headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  log.info("Added Facebook feature for author %s" % authorName)
    
  request.session['facebook_access_token'] = fbAccessToken
  request.session['facebook_user_id'] = fbUserId
  
  request.session.flash('The Facebook feature has been successfully added.')
  return HTTPFound(location=request.route_path('facebook_confirmation'))
    

@view_config(route_name='facebook_confirmation', request_method='GET', renderer='timweb:templates/facebook_confirmation.pt')
def facebook_confirmation(request):

  posts = []
    
  try:

    # query the api for some feature events to display to the user
    req = urllib2.Request('http://%s/v1/authors/%s/features/%s/featureEvents' % 
                            (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE)) 
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
    
    for event in resJSON['events']:
      title = event['content']['label'] if event['content']['label'] else ''
      timestamp = datetime.utcfromtimestamp(event['create_time'])
      posts.append('<p>%s (Created: %s)</p>' % (title,timestamp.isoformat()))
#
#    # /me/posts
#    req = urllib2.Request(oauth_config[FEATURE]['url'] % ('me/posts',access_token))
#    res = urllib2.urlopen(req)
#    postsJSON = json.loads(res.read())
#
#    print 'posts'
#    for post in postsJSON['data']:
#      if post['from']['id'] == fbUserId:
#        if hasattr(post,'story'):
#          posts.append('<p>%s</p>' % post['story'])          
#
#    # /me/events
#    req = urllib2.Request(oauth_config[FEATURE]['url'] % ('me/events',access_token))
#    res = urllib2.urlopen(req)
#    postsJSON = json.loads(res.read())
#
#    print 'events'
#    for post in postsJSON['data']:
#      if 'name' in post:
#        posts.append('<p>%s</p>' % post['name'])          

  except Exception, e:
    print "ERROR:"
    print e

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return{'message':message,'content':''.join(posts), 'title':'Facebook Feature'}
  
