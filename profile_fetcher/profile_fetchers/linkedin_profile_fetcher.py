'''
Created on Jan 16, 2012

@author: howard
'''

import oauth2 as oauth
import urllib

from tim_commons.oauth import make_request
from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher


class LinkedinProfileFetcher(ProfileFetcher):

  PROFILE_INFO = 'people/~:(first-name,last-name,headline,public-profile-url,picture-url,location:(name),industry,summary,specialties,associations,honors,interests,positions:(title,summary,company))'
  PUBLIC_PROFILE_INFO = 'people/url={0}:(first-name,last-name,headline,public-profile-url,picture-url,location:(name),industry,summary,specialties,associations,honors,interests,positions:(title,summary,company))'
#  PUBLIC_PROFILE_INFO = 'people/url={0}:public'

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    # setup what we need for oauth
    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    if asm.access_token:
      token = oauth.Token(key=asm.access_token, secret=asm.access_token_secret)
    else:
      token = oauth.Token(self.oauth_config['user1_access_token'], self.oauth_config['user1_access_token_secret'])
    client = oauth.Client(consumer, token)

    profile_url_stem = self.PROFILE_INFO if asm.access_token \
                       else self.PUBLIC_PROFILE_INFO.format(urllib.quote(asm.service_author_id, ''))

    url = '%s%s' % (self.oauth_config['endpoint'], profile_url_stem)

    # request the user's profile
    json_obj = json_serializer.load_string(make_request(client, url, {'x-li-format': 'json'}))

    profile_json = {}

    firstName = lastName = ''

    if 'firstName' in json_obj:
      firstName = profile_json['first_name'] = json_obj['firstName']

    if 'lastName' in json_obj:
      lastName = profile_json['last_name'] = json_obj['lastName']

    # if we have a non-empty string add it to the json
    name = ('%s %s' % (firstName, lastName)).strip()
    if len(name) > 0:
      profile_json['name'] = name

    if 'industry' in json_obj:
      profile_json['industry'] = json_obj['industry']

    if 'headline' in json_obj:
      profile_json['headline'] = json_obj['headline']

    if 'pictureUrl' in json_obj:
      profile_json['picture_url'] = json_obj['pictureUrl']

    if 'location' in json_obj and 'name' in json_obj['location']:
      profile_json['location'] = json_obj['location']['name']

    if 'summary' in json_obj:
      profile_json['summary'] = json_obj['summary']

    if 'specialties' in json_obj:
      profile_json['specialties'] = json_obj['specialties']

    if 'publicProfileUrl' in json_obj:
      profile_json['public_profile_url'] = json_obj['publicProfileUrl']

    if 'positions' in json_obj and 'values' in json_obj['positions']:
      positions = []
      for position in json_obj['positions']['values']:

        position_json = {}

        if 'company' in position:

          if 'name' in position['company']:
            position_json['company'] = position['company']['name']

          if 'industry' in position['company']:
            position_json['industry'] = position['company']['industry']

        if 'summary' in position:
          position_json['summary'] = position['summary']

        if 'title' in position:
          position_json['title'] = position['title']

        positions.append(position_json)

      profile_json['positions'] = positions

    return profile_json

#    # request the user's network status
#    response = make_request(client,'http://api.linkedin.com/v1/people/~/network/network-stats',{'x-li-format':'json'})
#    json_obj = json.loads(response)
#    firstdegree = json_obj['values'][0]
#    seconddegree = json_obj['values'][1]
#    print json.dumps(json_obj, sort_keys=True, indent=2)
