import json
import urllib
import urllib2
from time import mktime

from tim_commons.messages import create_instagram_event
from event_interpreter.instagram_event_interpreter import InstagramEventInterpreter
from event_collector import EventCollector


class InstagramEventCollector(EventCollector):

  USER_MEDIA = 'users/self/media/recent'

  PAGE_SIZE = 200

  def fetch(self, service_author_id, callback):

    super(InstagramEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    args = {'access_token': asm.access_token,
            'count': self.PAGE_SIZE}

    # optimization to request only those since we've last updated
    if asm.last_update_time:
      args['min_timestamp'] = int(mktime(asm.last_update_time.timetuple()))

    # setup the url for fetching a page of posts
    url = '%s%s?%s' % (self.oauth_config['endpoint'], self.USER_MEDIA, urllib.urlencode(args))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      raw_obj = json.load(urllib2.urlopen(url))

      # for element in the feed
      for post in raw_obj.get('data', []):

        if self.screen_event(InstagramEventInterpreter(post, asm, self.oauth_config), state):
          total_accepted = total_accepted + 1
          callback(create_instagram_event(service_author_id, asm.author_id, post))

        # if
      # for

      # setup for the next page (if any)
      url = raw_obj['pagination']['next_url'] if 'pagination' in raw_obj and 'next_url' in raw_obj['pagination'] else None

    # terminate the fetch
    self.fetch_end(state)
