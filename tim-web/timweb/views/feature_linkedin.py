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

from tim_commons.request_with_method import RequestWithMethod
from tim_commons.oauth import make_request

from timweb.exceptions import UnexpectedAPIResponse
from timweb import oauth_config

log = logging.getLogger(__name__)


# ??? TODO - these need to come from somewhere else
FEATURE = 'linkedin'

@view_config(route_name='linkedin', request_method='GET', renderer='timweb:templates/linkedin.pt', permission='author')
def get_linkedin(request):

  # first check if the author has already added this feature.
  
  # Query the API for installed features
  try:
    req = urllib2.Request('http://%s/v1/authors/%s/features' % (request.registry.settings['mi.api.endpoint'],authenticated_userid(request)))
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
    return HTTPFound(location=request.route_path('linkedin_confirmation'))
    
  return { 'feature':'LinkedIn', 'url' : request.route_url('linkedin'), 'title':'LinkedIn feature'}
  
@view_config(route_name='linkedin', request_method='POST', permission='author')
def post_linkedin(request):

  consumer_key = oauth_config[FEATURE]['key']
  consumer_secret = oauth_config[FEATURE]['secret']
  consumer = oauth.Consumer(consumer_key, consumer_secret)
  client = oauth.Client(consumer)
  
  # Step 1: Get a request token. This is a temporary token that is used for 
  # having the user authorize an access token and to sign the request to obtain 
  # said access token.

  callback = request.route_url('linkedin_callback')
  resp, content = client.request(oauth_config[FEATURE]['request_token_url'], "POST", body=urllib.urlencode({'oauth_callback':callback}))
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

  redirectURL = "%s?oauth_token=%s" % (oauth_config[FEATURE]['authorize_url'], request_token['oauth_token'])
  
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
  consumer = oauth.Consumer(oauth_config[FEATURE]['key'], oauth_config[FEATURE]['secret'])
  
  token = oauth.Token(oauth_token,oauth_token_secret)
  token.set_verifier(oauth_verifier)

  client = oauth.Client(consumer, token)
  
  resp, content = client.request(oauth_config[FEATURE]['access_token_url'], "POST")
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

  json_payload = json.dumps({'access_token':accessToken,'access_token_secret':accessTokenSecret,'auxillary_data':{'id':linkedinId}})
  headers = {'Content-Type':'application/json; charset=utf-8'}      
  req = RequestWithMethod('http://%s/v1/authors/%s/features/%s' % 
                            (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE), 
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
    
  request.session.flash('The LinkedIn feature has been successfully added.')
  return HTTPFound(location=request.route_path('linkedin_confirmation'))


@view_config(route_name='linkedin_confirmation', request_method='GET', renderer='timweb:templates/linkedin_confirmation.pt')
def linkedin_confirmation(request):
  
  # check if the linkedin access token is already in the session store.  If not we'll need to retrieve
  # from the API
  access_token = request.session.get('linkedin_access_token')

  if not access_token:

    req = urllib2.Request('http://%s/v1/authors/%s/features/%s' % 
                              (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE))
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())

    # ??? TODO - enhance the error handling
    access_token = resJSON['access_token']
    if not access_token:
      raise UnexpectedAPIResponse('missing access_token for Instagram for author %s' % authenticated_userid(request))

    access_token_secret = resJSON['access_token_secret']
    if not access_token_secret:
      raise UnexpectedAPIResponse('missing access_token_secret for Instagram for author %s' % authenticated_userid(request))

    request.session['linkedin_access_token'] = access_token
    request.session['linkedin_access_token_secret'] = access_token_secret
      
  accessToken = request.session['linkedin_access_token']
  accessTokenSecret = request.session['linkedin_access_token_secret']

  # Create our OAuth consumer instance
  consumer = oauth.Consumer(oauth_config[FEATURE]['key'], oauth_config[FEATURE]['secret'])
  token = oauth.Token(key=accessToken,secret=accessTokenSecret)
  client = oauth.Client(consumer, token)

  # request the user's profile
  response = make_request(client,'http://api.linkedin.com/v1/people/~:(id,first-name,last-name,headline,public-profile-url)',{'x-li-format':'json'})
  respJSON = json.loads(response)
  firstname = respJSON['firstName']
  lastname = respJSON['lastName']
  headline = respJSON['headline']
  profileURL = respJSON['publicProfileUrl']
  print json.dumps(respJSON, sort_keys=True, indent=2)

  # request the user's network status
  response = make_request(client,'http://api.linkedin.com/v1/people/~/network/network-stats',{'x-li-format':'json'})
  respJSON = json.loads(response)
  firstdegree = respJSON['values'][0]
  seconddegree = respJSON['values'][1]
#  print json.dumps(respJSON, sort_keys=True, indent=2)

  # request the user's connections
  response = make_request(client,'http://api.linkedin.com/v1/people/~/connections',{'x-li-format':'json'})
  respJSON = json.loads(response)
  connections = []
  for connection in respJSON['values']:
    if connection['id'] == 'private':
      continue
    image = '<img src="%s"/>' % connection['pictureUrl'] if 'pictureUrl' in connection else ''
    connections.append('<li>%s %s %s</li>' % (connection['firstName'], connection['lastName'], image))
#  print json.dumps(respJSON, sort_keys=True, indent=2)

  # query the api for some feature events to display to the user
  req = urllib2.Request('http://%s/v1/authors/%s/features/%s/featureEvents' % 
                          (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE)) 
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  updates = []
  for event in resJSON['events']:
    title = event['content']['label'] if event['content']['label'] else ''
    timestamp = datetime.utcfromtimestamp(event['create_time'])
    updates.append('<p>%s (Created: %s)</p>' % (title,timestamp.isoformat()))

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return{'message':message, 'title':'LinkedIn feature',
         'firstname':firstname,'lastname':lastname,'headline':headline,'profileURL':profileURL,
         'firstdegree':firstdegree,'seconddegree':seconddegree,
         'updates': ''.join(updates),
         'connections': ''.join(connections)}
