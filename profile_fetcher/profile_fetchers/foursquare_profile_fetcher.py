'''
Created on Jan 16, 2012

@author: howard
'''

import urllib
import urllib2

from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher


class FoursquareProfileFetcher(ProfileFetcher):

  USER_INFO = 'users/{0}'

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    if asm.access_token:
      access_token = asm.access_token
      user_info = self.USER_INFO.format('self')
    else:
      access_token = self.oauth_config['user1_access_token']
      user_info = self.USER_INFO.format(asm.service_author_id)

    args = {'oauth_token': access_token,
            'v': 20120130}

    url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                              user_info,
                              urllib.urlencode(args))

    # request the user's profile
    json_obj = json_serializer.load(urllib2.urlopen(url))

    # check for error
    if json_obj['meta']['code'] != 200:
      raise Exception('Foursquare error response: {0}'.format(json_obj['meta']['code']))

    json_obj = json_obj['response']['user']

    profile_json = {}

    firstName = profile_json['first_name'] = json_obj.get('firstName', '')

    lastName = profile_json['last_name'] = json_obj.get('lastName', '')

    # if we have a non-empty string add it to the json
    name = '{0} {1}'.format(firstName, lastName).strip()
    if len(name) > 0:
      profile_json['name'] = name

    if 'photo' in json_obj:
      profile_json['picture_url'] = json_obj['photo']

    if 'bio' in json_obj:
      profile_json['headline'] = json_obj['bio']

    return profile_json
