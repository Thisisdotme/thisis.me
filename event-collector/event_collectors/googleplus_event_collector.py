import json
import urllib
import urllib2

from tim_commons.messages import create_googleplus_event
from event_interpreter.googleplus_event_interpreter import GoogleplusStatusEventInterpreter
from event_collector import EventCollector


class InstagramEventCollector(EventCollector):

  USER_ACTIVITY = 'people/me/activities/public'

  PAGE_SIZE = 200

  def fetch(self, service_author_id, callback):

    super(InstagramEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    # we need to exchange the refresh token for an access token
    queryArgs = urllib.urlencode([('client_id', self.oauth_config['key']),
                                  ('client_secret', self.oauth_config['secret']),
                                  ('refresh_token', asm.access_token),
                                  ('grant_type', 'refresh_token')])
    raw_obj = json.load(urllib2.urlopen(self.oauth_config['oauth_exchange_url'], queryArgs))

    accessToken = raw_obj['access_token']

    args = {'access_token': accessToken,
            'maxResults': self.PAGE_SIZE}

    # setup the url for fetching a page of posts
    url = '%s%s?%s' % (self.oauth_config['endpoint'], self.USER_ACTIVITY, urllib.urlencode(args))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      raw_obj = json.load(urllib2.urlopen(url))

      # for element in the feed
      for post in raw_obj.get('items', []):

        if post['kind'] == 'plus#activity':

          if self.screen_event(GoogleplusStatusEventInterpreter(post, asm, self.oauth_config), state):
            total_accepted = total_accepted + 1
            callback(create_googleplus_event(service_author_id, asm.author_id, post))

        # if
      # for

      # setup for the next page (if any)
      next_page = raw_obj.get('next_pageToken')
      if next_page:
        args['pageToken'] = next_page
        url = '%s%s?%s' % (self.oauth_config['endpoint'], self.USER_ACTIVITY, urllib.urlencode(args))
      else:
        url = None

    # terminate the fetch
    self.fetch_end(state)
