import logging
import urlparse
import urllib
import urllib2
import oauth2 as oauth
import simplejson as json
from datetime import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from mi_utils.oauth import make_request
from mi_url.RequestWithMethod import RequestWithMethod

from timweb import oAuthConfig

log = logging.getLogger(__name__)


# ??? TODO - these need to come from somewhere else
FEATURE = 'twitter'

@view_config(route_name='twitter', request_method='GET', renderer='timweb:templates/twitter.pt', permission='author')
def get_twitter(request):

  # first check if the author has already added this feature.
  
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
    request.session.flash('You have already added the Twitter feature.')
    return HTTPFound(location=request.route_path('twitter_confirmation'))
    
  return { 'feature':'Twitter', 'url' : request.route_url('twitter'), 'title':'Twitter feature'}
  
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

  # Step 2: Redirect to the provider. Since this is a CLI script we do not 
  # redirect. In a web application you would redirect the user to the URL
  # below.

  request.session['oauth_token_secret'] = request_token['oauth_token_secret']

  redirectURL = "%s?oauth_token=%s" % (oAuthConfig[FEATURE]['authorize_url'], request_token['oauth_token'])
  
  return HTTPFound(location=redirectURL)


@view_config(route_name='twitter_callback', request_method='GET')
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

  json_payload = json.dumps({'access_token':oauth_token,'access_token_secret':oauth_token_secret,'auxillary_data':{'id':userInfoJSON['id']}})
  headers = {'Content-Type':'application/json; charset=utf-8'}      
  req = RequestWithMethod('%s/v1/authors/%s/features/%s' % 
                            (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE), 
                          'PUT',
                          json_payload,
                          headers)
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())

  try:
    request.session['twitter_access_token'] = oauth_token
    request.session['twitter_access_token_secret'] = oauth_token_secret
  except Exception, e:
    print e
    
  request.session.flash('The Twitter feature has been successfully added.')
  return HTTPFound(location=request.route_path('twitter_confirmation'))


@view_config(route_name='twitter_confirmation', request_method='GET', renderer='timweb:templates/twitter_confirmation.pt')
def twitter_confirmation(request):
  
  # query the api for some feature events to display to the user
  req = urllib2.Request('%s/v1/authors/%s/features/%s/featureEvents' % 
                          (request.registry.settings['mi.api.endpoint'],authenticated_userid(request),FEATURE)) 
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  content = []
  for event in resJSON['events']:
    title = event['content']['label']
    timestamp = datetime.utcfromtimestamp(event['create_time'])
    content.append('<p>%s - %s</p>' % (timestamp.isoformat(),title))

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return{'message':message,'content':''.join(content), 'title':'Twitter feature'}
