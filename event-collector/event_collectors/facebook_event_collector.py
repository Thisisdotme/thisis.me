import urllib
import urllib2
import datetime
import calendar
import logging

from tim_commons.messages import create_facebook_event
from tim_commons import json_serializer
from event_interpreter.facebook_event_interpreter import FacebookEventInterpreter
from event_collector import EventCollector


class FacebookEventCollector(EventCollector):

  FEED_COLLECTION = 'me/posts'
  ALBUMS_COLLECTION = 'me/albums'
  PHOTOS_COLLECTION = '/photos'

  def fetch(self, service_author_id, callback):

    super(FacebookEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    args = {'access_token': asm.access_token}

    # get only events since last update or past year depending on if this
    # is the first collection of not
    if asm.most_recent_event_timestamp:
      since = calendar.timegm((asm.most_recent_event_timestamp -
                               self.MOST_RECENT_OVERLAP).utctimetuple())
    else:
      since = calendar.timegm((datetime.datetime.utcnow() -
                               self.NEW_LOOKBACK_WINDOW).utctimetuple())
    args['since'] = since

    # fetch all new posts
    path = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                               self.FEED_COLLECTION,
                               urllib.urlencode(args))

    total_accepted = 0
    while path and total_accepted < self.MAX_EVENTS:
      logging.debug('Requesting %s', path)
      posts_obj = json_serializer.load(urllib2.urlopen(path))

      # process the item

      # TODO loop termination on various constraints is not exact

      # for element in the feed
      for post in posts_obj['data']:

        # currently only interested in 'status' posts from the user
        if post['from']['id'] == service_author_id:

          # if this is a status update and there are no actions then skip it
          if post.get('type') == 'status' and post.get('actions') is None:
            continue

          if self.screen_event(FacebookEventInterpreter(post, asm, self.oauth_config),
                               state):
            total_accepted = total_accepted + 1
            callback(create_facebook_event(service_author_id, asm.author_id, post))

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      nextPath = posts_obj['paging']['next'] if 'paging' in posts_obj and 'next' in posts_obj['paging'] else None
      path = nextPath if nextPath and nextPath != path else None

    # terminate the fetch
    self.fetch_end(state)
