import urllib
import urllib2
from datetime import datetime
import calendar

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
      since = calendar.timegm((datetime.utcnow() -
                               self.NEW_LOOKBACK_WINDOW).utctimetuple())
    args['since'] = since

    # fetch all new posts
    posts_url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                                    self.FEED_COLLECTION,
                                    urllib.urlencode(args))

    total_accepted = 0
    while posts_url and total_accepted < self.MAX_EVENTS:

      posts_obj = json_serializer.load(urllib2.urlopen(posts_url))

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
      next_url = posts_obj['paging']['next'] if 'paging' in posts_obj and 'next' in posts_obj['paging'] else None
      posts_url = next_url if next_url and next_url != posts_url else None

    # while posts

    # collect photos for all time.  If this is the first update then
    photo_since = since if asm.most_recent_event_timestamp else None

    albums_url = '{0}{1}?{2}'.format(self.oauth_config['endpoint'],
                                     self.ALBUMS_COLLECTION,
                                     urllib.urlencode({'access_token': asm.access_token}))

    while albums_url:

      albums_obj = json_serializer.load(urllib2.urlopen(albums_url))

      for album in albums_obj.get('data', []):

        # skip photos posted to friend's walls
        if album['type'] == 'friends_walls':
          continue

        created_time = calendar.timegm(datetime.strptime(album['created_time'], "%Y-%m-%dT%H:%M:%S+0000").utctimetuple())
        updated_time = calendar.timegm(datetime.strptime(album['updated_time'], "%Y-%m-%dT%H:%M:%S+0000").utctimetuple())

        if photo_since == None or created_time >= photo_since or updated_time >= photo_since:

          # set the type to 'album so it will match what you get when it's directly
          # queried; also makes it easier for the event process to identify it
          album['type'] = 'album'

          # send event message
          callback(create_facebook_event(service_author_id, asm.author_id, album))

        # if

        # check for any new photos in the album
        photos_url = '{0}{1}{2}?{3}'.format(self.oauth_config['endpoint'],
                                            album['id'],
                                            self.PHOTOS_COLLECTION,
                                            urllib.urlencode(args))
        while photos_url:

          photos_obj = json_serializer.load(urllib2.urlopen(photos_url))

          for photo in photos_obj.get('data', []):

            photo['type'] = 'photo'

            # event message
            callback(create_facebook_event(service_author_id, asm.author_id, photo))

          # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
          next_url = photos_obj['paging']['next'] if 'paging' in photos_obj and 'next' in photos_obj['paging'] else None
          photos_url = next_url if next_url and next_url != photos_url else None

        # while photos

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      next_url = albums_obj['paging']['next'] if 'paging' in albums_obj and 'next' in albums_obj['paging'] else None
      albums_url = next_url if next_url and next_url != albums_url else None

    # while albums

    # terminate the fetch
    self.fetch_end(state)
