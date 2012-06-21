import urllib
import urllib2
from datetime import datetime
import calendar

from tim_commons.messages import create_instagram_event, CURRENT_STATE
from tim_commons import json_serializer

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

    # get only events since last update or past year depending on if this
    # is the first collection of not
    if asm.most_recent_event_timestamp:
      min_timestamp = calendar.timegm((asm.most_recent_event_timestamp -
                                       self.MOST_RECENT_OVERLAP).utctimetuple())
    else:
      min_timestamp = calendar.timegm((datetime.utcnow() -
                                       self.NEW_LOOKBACK_WINDOW).utctimetuple())
    args['min_timestamp'] = min_timestamp

    # setup the url for fetching a page of posts
    url = '%s%s?%s' % (self.oauth_config['endpoint'], self.USER_MEDIA, urllib.urlencode(args))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      raw_obj = json_serializer.load(urllib2.urlopen(url))

      # for element in the feed
      for post in raw_obj.get('data', []):

        interpreter = InstagramEventInterpreter(post, asm, self.oauth_config)

        if self.screen_event(interpreter, state):
          total_accepted = total_accepted + 1
          callback(create_instagram_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), post))

        # if
      # for

      # setup for the next page (if any)
      url = raw_obj['pagination']['next_url'] if 'pagination' in raw_obj and 'next_url' in raw_obj['pagination'] else None

    # terminate the fetch
    self.fetch_end(state)
