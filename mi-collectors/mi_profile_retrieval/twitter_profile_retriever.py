'''
Created on Jan 16, 2012

@author: howard
'''

import oauth2 as oauth
import json

from mi_utils.oauth import make_request

from profile_retriever import ProfileRetriever

class TwitterProfileRetriever(ProfileRetriever):
  
  '''
  classdocs
  '''
  feature_name = 'twitter'
  
  def get_author_profile(self,afm,db_session,oauth_config):
    
    # Create our OAuth consumer instance
    consumer = oauth.Consumer(oauth_config['key'], oauth_config['secret'])
    token = oauth.Token(key=afm.access_token,secret=afm.access_token_secret)
    client = oauth.Client(consumer, token)

    # request the user's profile
    content = make_request(client,'https://api.twitter.com/1/account/verify_credentials.json')
    str_content = content.decode('utf-8')

    respJSON = json.loads(str_content)

#    print json.dumps(respJSON, sort_keys=True, indent=2)
    
    profileJSON = {}

    if respJSON.has_key('name'):
      profileJSON['name'] = respJSON['name']

    if respJSON.has_key('location'):
      profileJSON['location'] = respJSON['location']

    if respJSON.has_key('profile_image_url'):
      profileJSON['picture_url'] = respJSON['profile_image_url']

    if respJSON.has_key('description'): 
      profileJSON['headline'] = respJSON['description']
      
    profileJSON['public_profile_url'] = 'https://twitter.com/#!/%s' % respJSON['screen_name']

    return profileJSON
  