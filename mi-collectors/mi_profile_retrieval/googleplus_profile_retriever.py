'''
Created on Jan 16, 2012

@author: howard
'''

import urllib
import urllib2
import json
import re

from profile_retriever import ProfileRetriever

class GooglePlusProfileRetriever(ProfileRetriever):
  
  '''
  classdocs
  '''
  feature_name = 'linkedin'
  
  def get_author_profile(self,afm,db_session,oauth_config):
    
    # we need to exchange the refresh token for an access token 
    apiKey = oauth_config['key']
    apiSecret = oauth_config['secret']
    queryArgs = urllib.urlencode([('client_id',apiKey),
                                  ('client_secret',apiSecret),
                                  ('refresh_token',afm.access_token),
                                  ('grant_type','refresh_token')])
    req = urllib2.Request(oauth_config['oauth_exchange_url'],queryArgs) 
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())

    accessToken = resJSON['access_token']

    # get a little info from the plus people api
    req = urllib2.Request('https://www.googleapis.com/plus/v1/people/me?access_token=%s' % accessToken)
    res = urllib2.urlopen(req)
    respJSON = json.loads(res.read())

#    print json.dumps(respJSON, sort_keys=True, indent=2)
    
    profileJSON = {}
    
    if respJSON.has_key('name'):

      firstName = lastName = ''

      if respJSON['name'].has_key('givenName'): 
        profileJSON['first_name'] = respJSON['name']['givenName']
        firstName = profileJSON['first_name']
  
      if respJSON['name'].has_key('familyName'): 
        profileJSON['last_name'] = respJSON['name']['familyName']
        lastName = profileJSON['last_name']
        
      profileJSON['name'] = ('%s %s' % (firstName,lastName)).strip()

    if respJSON.has_key('aboutMe'): 
      profileJSON['summary'] = re.sub(r'<[^>]*?>', '', respJSON['aboutMe']) 

    if respJSON.has_key('image') and respJSON['image'].has_key('url'):
      profileJSON['picture_url'] = respJSON['image']['url']

    if respJSON.has_key('url'): 
      profileJSON['public_profile_url'] = respJSON['url']

    return profileJSON
