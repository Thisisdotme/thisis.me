import urllib
import urllib2

from tim_commons.messages import create_googleplus_event
from tim_commons import json_serializer
from event_interpreter.googleplus_event_interpreter import GoogleplusStatusEventInterpreter
from event_collector import EventCollector


class GoogleplusEventCollector(EventCollector):

  USER_ACTIVITY = 'people/me/activities/public'

  PAGE_SIZE = 100

  def fetch(self, service_author_id, callback):

    super(GoogleplusEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    # TODO - there needs to be a global caching mechanism for this (i.e. memcached, etc.).
    #        Because of the distributed nature of this two successive updates for the
    #        same author don't share any state and can't leverage the refresh token.
    #        The refresh token should have a configured TTL

    # we need to exchange the refresh token for an access token
    query_args = urllib.urlencode([('client_id', self.oauth_config['key']),
                                   ('client_secret', self.oauth_config['secret']),
                                   ('refresh_token', asm.access_token),
                                   ('grant_type', 'refresh_token')])
    raw_obj = json_serializer.load(urllib2.urlopen(self.oauth_config['oauth_exchange_url'],
                                                   query_args))

    access_token = raw_obj['access_token']

    args = {'access_token': access_token,
            'maxResults': self.PAGE_SIZE}

    # setup the url for fetching a page of posts
    url = '%s%s?%s' % (self.oauth_config['endpoint'], self.USER_ACTIVITY, urllib.urlencode(args))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      raw_obj = json_serializer.load(urllib2.urlopen(url))

      # for element in the feed
      for post in raw_obj.get('items', []):

        if post['kind'] == 'plus#activity':

          if self.screen_event(GoogleplusStatusEventInterpreter(post, asm, self.oauth_config),
                               state):
            total_accepted = total_accepted + 1
            callback(create_googleplus_event(service_author_id, asm.author_id, post))

        # if
      # for

      # setup for the next page (if any)
      next_page = raw_obj.get('next_pageToken')
      if next_page:
        args['pageToken'] = next_page
        url = '%s%s?%s' % (self.oauth_config['endpoint'],
                           self.USER_ACTIVITY,
                           urllib.urlencode(args))
      else:
        url = None

    # terminate the fetch
    self.fetch_end(state)
