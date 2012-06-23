'''
Created on Jan 16, 2012

@author: howard
'''

import urllib
import urllib2

from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher


class FacebookProfileFetcher(ProfileFetcher):

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    if asm.access_token:
      access_token = asm.access_token
      user_id = 'me'
    else:
      access_token = self.oauth_config['user1_access_token']
      user_id = asm.service_author_id

    args = {'access_token': access_token}

    url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                              user_id,
                              urllib.urlencode(args))

    # request the user's profile
    json_obj = json_serializer.load(urllib2.urlopen(url))

    profile_json = {}

    if 'first_name' in json_obj:
      profile_json['first_name'] = json_obj['first_name']

    if 'last_name' in json_obj:
      profile_json['last_name'] = json_obj['last_name']

    if 'name' in json_obj:
      profile_json['name'] = json_obj['name']

    if 'link' in json_obj:
      profile_json['public_profile_url'] = json_obj['link']

    url = '{0}{1}/picture?{2}'.format(self.oauth_config['endpoint'],
                              user_id,
                              urllib.urlencode(args))

    # request the user's profile
    picuture_json = urllib2.urlopen(url).geturl()

    profile_json['picture_url'] = picuture_json

    return profile_json
