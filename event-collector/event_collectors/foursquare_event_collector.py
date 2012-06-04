'''
Created on May 4, 2012

@author: howard
'''
import json
import urllib
import urllib2
from datetime import datetime
from time import mktime

from tim_commons.messages import create_foursquare_event
from event_interpreter.foursquare_event_interpreter import FoursquareEventInterpreter
from event_collector import EventCollector

USER_CHECKINS = 'users/self/checkins'
USER_SELF = 'users/self'

LIMIT = 200


class FoursquareEventCollector(EventCollector):

  def fetch(self, service_author_id, callback):

    super(FoursquareEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    args = {'oauth_token': asm.access_token,
            'v': 20120130}

    args['limit'] = LIMIT
    args['offset'] = 0

    # get only events since last update or past year depending on if this
    # is the first collection of not
    if asm.most_recent_event_timestamp:
      after_time = int(mktime((asm.most_recent_event_timestamp - self.LAST_UPDATE_OVERLAP).timetuple()))
    else:
      after_time = int(mktime((datetime.utcnow() - self.LOOKBACK_WINDOW).timetuple()))

    args['afterTimestamp'] = after_time

    url = '%s%s?%s' % (self.oauth_config['endpoint'], USER_CHECKINS, urllib.urlencode(args))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      raw_json = json.load(urllib2.urlopen(url))

      # check for error
      if raw_json['meta']['code'] != 200:
        raise Exception('Foursquare error response: %s' % raw_json['meta']['code'])

      # terminate if the response has no more events/checkins
      if len(raw_json['response']['checkins']['items']) == 0:
        break

      # for each element in the feed
      for post in raw_json['response']['checkins']['items']:

        interpreter = FoursquareEventInterpreter(post, asm, self.oauth_config)

        if self.screen_event(interpreter, state):
          total_accepted = total_accepted + 1
          callback(create_foursquare_event(service_author_id, asm.author_id, post))

      # for

      if not url:
        break

      # setup next request
      args['offset'] = args['offset'] + LIMIT
      url = '%s%s?%s' % (self.oauth_config['endpoint'], USER_CHECKINS, urllib.urlencode(args))

    # terminate the fetch
    self.fetch_end(state)
