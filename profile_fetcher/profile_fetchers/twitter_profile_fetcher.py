'''
Created on Jan 16, 2012

@author: howard
'''

import oauth2 as oauth
import urllib
import urllib2

from tim_commons.oauth import make_request
from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher

USER_INFO = 'users/show.json'


class TwitterProfileFetcher(ProfileFetcher):

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    args = {'user_id': asm.service_author_id,
            'include_entities': True}

    # Create our OAuth consumer instance
    if asm.access_token:
      consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
      token = oauth.Token(key=asm.access_token, secret=asm.access_token_secret)
      client = oauth.Client(consumer, token)

    url = '%s%s?%s' % (self.oauth_config['endpoint'],
                       USER_INFO,
                       urllib.urlencode(args))

    # request the user's profile
    json_obj = json_serializer.load_string(make_request(client, url)) if asm.access_token \
               else json_serializer.load(urllib2.urlopen(url))

    profile_json = {}

    if 'name' in json_obj:
      profile_json['name'] = json_obj['name']

    if 'location' in json_obj:
      profile_json['location'] = json_obj['location']

    if 'profile_image_url' in json_obj:
      profile_json['picture_url'] = json_obj['profile_image_url']

    if 'description' in json_obj:
      profile_json['headline'] = json_obj['description']

    profile_json['public_profile_url'] = 'https://twitter.com/#!/%s' % json_obj['screen_name']

    return profile_json
