import json
import urllib
import urllib2
from datetime import datetime
from time import mktime

from tim_commons.messages import create_facebook_event
from event_interpreter.facebook_event_interpreter import FacebookStatusEventInterpreter
from event_collector import EventCollector


class FacebookEventCollector(EventCollector):

  FEED_COLLECTION = 'me/posts'
  ALBUMS_COLLECTION = 'me/albums'

  def fetch(self, service_author_id, callback):

    super(FacebookEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    args = {'access_token': asm.access_token}

    # get only events since last update or past year depending on if this
    # is the first collection of not
    if asm.most_recent_event_timestamp:
      since = int(mktime((asm.most_recent_event_timestamp - self.LAST_UPDATE_OVERLAP).timetuple()))
    else:
      since = int(mktime((datetime.utcnow() - self.LOOKBACK_WINDOW).timetuple()))
    args['since'] = since

    # fetch all new posts
    path = '%s%s?%s' % (self.oauth_config['endpoint'], self.FEED_COLLECTION, urllib.urlencode(args))

    total_accepted = 0
    while path and total_accepted < self.MAX_EVENTS:

      raw_json = json.load(urllib2.urlopen(path))

      # process the item
      #print json.dumps(raw_json, sort_keys=True, indent=2)

      # TODO loop termination on various constraints is not exact

      # for element in the feed
      for post in raw_json['data']:

        # currently only interested in 'status' posts from the user
        if post['from']['id'] == service_author_id:

          # if this is a status update and there are no actions then skip it
          if post.get('type') == 'status' and post.get('actions') is None:
            continue

          if self.screen_event(FacebookStatusEventInterpreter(post, asm, self.oauth_config), state):
            total_accepted = total_accepted + 1
            callback(create_facebook_event(service_author_id, asm.author_id, post))

        # if
      # for

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      nextPath = raw_json['paging']['next'] if 'paging' in raw_json and 'next' in raw_json['paging'] else None
      path = nextPath if nextPath and nextPath != path else None

    # fetch all new photo albums
    path = '%s%s?%s' % (self.oauth_config['endpoint'], self.ALBUMS_COLLECTION, urllib.urlencode(args))
    total_accepted = 0
    while path and total_accepted < self.MAX_EVENTS:

      raw_json = json.load(urllib2.urlopen(path))

    # terminate the fetch
    self.fetch_end(state)
