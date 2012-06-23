'''
Created on Jan 16, 2012

@author: howard
'''

import urllib
import urllib2

from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher


class InstagramProfileFetcher(ProfileFetcher):

  USER_INFO = 'users/{0}'

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    if asm.access_token:
      access_token = asm.access_token
      user_info = self.USER_INFO.format('self')
    else:
      access_token = self.oauth_config['user1_access_token']
      user_info = self.USER_INFO.format(asm.service_author_id)

    args = {'access_token': access_token}

    url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                           user_info,
                           urllib.urlencode(args))

    # request the user's profile
    json_obj = json_serializer.load(urllib2.urlopen(url))

    if json_obj['meta']['code'] != 200:
      raise Exception('Instagram error response: {0}'.format(json_obj['meta']['code']))

    json_obj = json_obj.get('data', {})

    profile_json = {}

    if 'full_name' in json_obj:
      profile_json['name'] = json_obj['full_name']

    if 'profile_picture' in json_obj:
      profile_json['picture_url'] = json_obj['profile_picture']

    if 'bio' in json_obj:
      profile_json['headline'] = json_obj['bio']

    return profile_json
