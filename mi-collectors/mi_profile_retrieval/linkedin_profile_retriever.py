'''
Created on Jan 16, 2012

@author: howard
'''

import oauth2 as oauth
import json

from tim_commons.oauth import make_request

from profile_retriever import ProfileRetriever

class LinkedInProfileRetriever(ProfileRetriever):
  
  '''
  classdocs
  '''
  service_name = 'linkedin'
  
  def get_author_profile(self,afm,db_session,oauth_config):
    
    # Create our OAuth consumer instance
    consumer = oauth.Consumer(oauth_config['key'], oauth_config['secret'])
    token = oauth.Token(key=afm.access_token,secret=afm.access_token_secret)
    client = oauth.Client(consumer, token)

    # request the user's profile
    response = make_request(client,'http://api.linkedin.com/v1/people/~:(first-name,last-name,headline,public-profile-url,picture-url,location:(name),industry,summary,specialties,associations,honors,interests,positions:(title,summary,company))',{'x-li-format':'json'})
    respJSON = json.loads(response)

#    print json.dumps(respJSON, sort_keys=True, indent=2)
    
    profileJSON = {}
    
    firstName = lastName = ''

    if respJSON.has_key('firstName'): 
      firstName = profileJSON['first_name'] = respJSON['firstName']
      
    if respJSON.has_key('lastName'): 
      lastName = profileJSON['last_name'] = respJSON['lastName']

    # if we have a non-empty string add it to the json
    name = ('%s %s' % (firstName,lastName)).strip()
    if len(name) > 0:
      profileJSON['name'] = name

    if respJSON.has_key('industry'): 
      profileJSON['industry'] = respJSON['industry']

    if respJSON.has_key('headline'): 
      profileJSON['headline'] = respJSON['headline']
      
    if respJSON.has_key('pictureUrl'):
      profileJSON['picture_url'] = respJSON['pictureUrl']

    if respJSON.has_key('location') and respJSON['location'].has_key('name'):
      profileJSON['location'] = respJSON['location']['name']

    if respJSON.has_key('summary'): 
      profileJSON['summary'] = respJSON['summary']

    if respJSON.has_key('specialties'): 
      profileJSON['specialties'] = respJSON['specialties']

    if respJSON.has_key('publicProfileUrl'): 
      profileJSON['public_profile_url'] = respJSON['publicProfileUrl']

    if respJSON.has_key('positions') and respJSON['positions'].has_key('values'):
      positions = []
      for position in respJSON['positions']['values']:
        
        positionJSON = {}
        
        if position.has_key('company'):
          
          if position['company'].has_key('name'):
            positionJSON['company'] = position['company']['name']

          if position['company'].has_key('industry'):
            positionJSON['industry'] = position['company']['industry']

        if position.has_key('summary'):
          positionJSON['summary'] = position['summary']

        if position.has_key('title'):
          positionJSON['title'] = position['title']
          
        positions.append(positionJSON)
  
      profileJSON['positions'] = positions
    
    return profileJSON
  
#    # request the user's network status
#    response = make_request(client,'http://api.linkedin.com/v1/people/~/network/network-stats',{'x-li-format':'json'})
#    respJSON = json.loads(response)
#    firstdegree = respJSON['values'][0]
#    seconddegree = respJSON['values'][1]
#    print json.dumps(respJSON, sort_keys=True, indent=2)
