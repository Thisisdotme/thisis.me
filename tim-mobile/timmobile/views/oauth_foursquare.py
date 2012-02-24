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

log = logging.getLogger(__name__)


class FoursquareView(object):
  '''
  classdocs
  '''
  
  '''
  class variables
  '''
  featureName = 'foursquare'
  
  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request

  def verify_access_token(self,access_token):

    validToken = True
  
    # We have a token, validate that it's valid
    log.info('Verifying foursquare token: %s', access_token)
  
    return validToken

  def get_access_info(self):

    # the presumption is that the feature already exists.  If it doesn't then this function
    # should not have been called
    req = urllib2.Request('%s/v1/authors/%s/features/%s' % 
                                (self.request.registry.settings['mi.api.endpoint'],authenticated_userid(self.request),self.featureName)) 
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
    
    # ??? TODO - enhance the error handling
    accessToken = resJSON['access_token']
    if not accessToken:
      raise UnexpectedAPIResponse('missing access_token for %s for author %s' % (self.featureName,authenticated_userid(self.request)))
  
    if not self.verify_access_token(accessToken):
      accessToken = None
  
    return accessToken, resJSON['auxillary_data']['id']
  
  @view_config(route_name='foursquare', request_method='GET', renderer='timmobile:templates/oauth.pt', permission='author')
  def get(self):

    # first check if the author has already added this feature.
    
    # Get author's login name
    authorName = authenticated_userid(self.request)
  
    userId = accessToken = None
  
    if 'foursquare_access_token' in self.request.session:
  
      accessToken = self.request.session['foursquare_access_token']
      userId = self.request.session['foursquare_user_id']
      if not self.verify_access_token(accessToken):
        accessToken = None
        del self.request.session['foursquare_access_token']
        del self.request.session['foursquare_user_id']
       
    else:
  
      # Query the API for installed features
      try:
        req = urllib2.Request('%s/v1/authors/%s/features' % (self.request.registry.settings['mi.api.endpoint'],authorName))
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
      if len([feature for feature in resJSON['features'] if feature['name'] == self.featureName]) == 1:
        accessToken, userId = self.get_access_info()      
    
        self.request.session['foursquare_access_token'] = accessToken
        self.request.session['foursquare_user_id'] = userId
  
    # redirect to add confirmation page if we don't have a valid access token
    if not accessToken:
      return {'feature':'Foursquare',
              'url' : self.request.route_url('foursquare'),
              'api_endpoint':self.request.registry.settings['mi.api.endpoint']}
    else:
  
      self.request.session.flash('Your Foursquare account is active.')
      return HTTPFound(location=self.request.route_path('account_details',featurename=self.featureName))


  @view_config(route_name='foursquare', request_method='POST', permission='author')
  def post(self):
  
    api_key = oAuthConfig[self.featureName]['key']
    queryArgs = urllib.urlencode([('client_id',api_key),
                                  ('response_type','code'),
                                  ('redirect_uri',self.request.route_url('foursquare_callback'))])
    
    url = oAuthConfig[self.featureName]['oauth_url'] % queryArgs
  
    log.info('Redirecting user to Foursquare to get authorization code')
  
    return HTTPFound(location=url)
  
  
  @view_config(route_name='foursquare_callback', request_method='GET')
  def callback(self):
    
    log.debug('foursquare_callback')
  
    authorName = authenticated_userid(self.request)
  
    accessToken = UserId = None
    userId = None
  
    code = self.request.params.get('code')
    if code:
    
      print 'code => %s' % code
      
      # let's get the acces_token
      api_key = oAuthConfig[self.featureName]['key']
      api_secret = oAuthConfig[self.featureName]['secret']
  
      queryArgs = urllib.urlencode([('client_id',api_key),
                                    ('client_secret',api_secret),
                                    ('grant_type','authorization_code'),
                                    ('redirect_uri',self.request.route_url('foursquare_callback')),
                                    ('code',code)])
      
      url = oAuthConfig[self.featureName]['access_token_url'] % queryArgs
  
      try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        resJSON = json.loads(res.read())        
  
        accessToken = resJSON['access_token']
  
      except urllib2.URLError, e:
        log.error(e.reason)
        raise e
      
      # now let's get some information about the user -- namely their id
      req = urllib2.Request(oAuthConfig[self.featureName]['url'] % ('users/self',accessToken))
      res = urllib2.urlopen(req)
      meJSON = json.loads(res.read())
  
      if meJSON['meta']['code'] == 200:
        userId = meJSON['response']['user']['id']
      
    else:
      error = self.request.params.get('error')
      raise GenericError('Error authenticating user with Foursquare: %s' % error)
    
    json_payload = json.dumps({'access_token':accessToken,'auxillary_data':{'id':userId}})
    headers = {'Content-Type':'application/json; charset=utf-8'}      
    req = RequestWithMethod('%s/v1/authors/%s/features/%s' % 
                                    (self.request.registry.settings['mi.api.endpoint'],authorName,self.featureName), 
                            'PUT',
                            json_payload,
                            headers)
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  
    log.info("Added Foursquare feature for author %s" % authorName)
      
    self.request.session['foursquare_access_token'] = accessToken
    self.request.session['foursquare_user_id'] = userId
    
    self.request.session.flash('Your Foursquare account has been successfully added.')
    return HTTPFound(location=self.request.route_path('account_details',featurename=self.featureName))
    