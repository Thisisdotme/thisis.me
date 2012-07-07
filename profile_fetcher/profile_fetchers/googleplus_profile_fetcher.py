'''
Created on Jan 16, 2012

@author: howard
'''

import logging
import urllib
import urllib2
import re

from tim_commons import json_serializer

from profile_fetcher import ProfileFetcher


class GoogleplusProfileFetcher(ProfileFetcher):

  USER_INFO = 'people/me'

  def get_author_profile(self, service_author_id, asm):

    asm = self.fetch_begin(service_author_id, asm)

    # we need to exchange the refresh token for an access token
    query_args = urllib.urlencode([('client_id', self.oauth_config['key']),
                                   ('client_secret', self.oauth_config['secret']),
                                   ('refresh_token', asm.access_token),
                                   ('grant_type', 'refresh_token')])

    try:
      raw_obj = json_serializer.load(urllib2.urlopen(self.oauth_config['oauth_exchange_url'],
                                                     query_args))
    except urllib2.URLError, e:
      logging.error('ERROR REASON: {0}, {1}'.format(e.code, e.read()))
      raise

    access_token = raw_obj['access_token']

    args = {'access_token': access_token}

    # setup the url for fetching profile
    url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'], self.USER_INFO, urllib.urlencode(args))

    # request the profile info
    json_obj = json_serializer.load(urllib2.urlopen(url))

    profile_json = {}

    if 'name' in json_obj:

      firstName = lastName = ''

      if 'givenName' in json_obj['name']:
        profile_json['first_name'] = json_obj['name']['givenName']
        firstName = profile_json['first_name']

      if 'familyName' in json_obj['name']:
        profile_json['last_name'] = json_obj['name']['familyName']
        lastName = profile_json['last_name']

      profile_json['name'] = ('%s %s' % (firstName, lastName)).strip()

    if 'aboutMe' in json_obj:
      profile_json['summary'] = re.sub(r'<[^>]*?>', '', json_obj['aboutMe'])

    if 'image' in json_obj and 'url' in json_obj['image']:
      profile_json['picture_url'] = json_obj['image']['url']

    if 'url' in json_obj:
      profile_json['public_profile_url'] = json_obj['url']

    return profile_json
