import urllib
import urllib2
from datetime import datetime
import calendar
import logging

from tim_commons.messages import create_facebook_event, CURRENT_STATE, create_event_link
from tim_commons import json_serializer

from event_interpreter.facebook_event_interpreter import FacebookEventInterpreter
from event_collector import EventCollector
import data_access.service


class FacebookEventCollector(EventCollector):

  FEED_COLLECTION = 'me/posts'
  ALBUMS_COLLECTION = 'me/albums'
  PHOTOS_COLLECTION = '/photos'
  CHECKIN_COLLECTION = 'me/checkins'

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
    posts_url = unicode('{0}{1}?{2}').format(self.oauth_config['endpoint'],
                                             self.FEED_COLLECTION,
                                             urllib.urlencode(args))

    total_accepted = 0
    while posts_url and total_accepted < self.MAX_EVENTS:

      logging.debug('requesting: "%s"', posts_url)
      posts_obj = json_serializer.load(urllib2.urlopen(posts_url))

      # process the item

      # TODO loop termination on various constraints is not exact

      # for element in the feed
      for post in posts_obj['data']:

        # currently only interested in 'status' posts from the user
        if post['from']['id'] == service_author_id:

          post_type = post.get('type', None)

          # if this is a status update and there is an action or the
          # user is tagged in the story keep it

          # TODO: check for user in story_tags is experimental

          if post_type == 'status':

            tagged = False
            if 'story_tags' in post:
              for story_tag in post['story_tags'].itervalues():
                for entity in story_tag:
                  if int(entity['id']) == int(service_author_id):
                    tagged = True
                    break
                if tagged:
                  break

            if not post.get('actions') and not tagged:
              continue

          # skip photo and checkin posts.  they will get picked-up by their respective
          # processing below
          if post_type == 'photo' or post_type == 'checkin':
            continue

          interpreter = FacebookEventInterpreter(post, asm, self.oauth_config)
          if self.screen_event(interpreter, state):
            total_accepted = total_accepted + 1
            callback(create_facebook_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), post))

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      next_url = posts_obj['paging']['next'] if 'paging' in posts_obj and 'next' in posts_obj['paging'] else None
      posts_url = next_url if next_url and next_url != posts_url else None

    # while posts

    # collect photos for all time if this is the first update; otherwise
    # only collect photos since the last update.  Setting since to None
    # and remove the 'since' property from the query args will collect
    # all photos
    if not asm.most_recent_event_timestamp:
      since = None
      del args['since']

    albums_url = unicode('{0}{1}?{2}').format(self.oauth_config['endpoint'],
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

        if since == None or created_time >= since or updated_time >= since:

          # set the type to 'album so it will match what you get when it's directly
          # queried; also makes it easier for the event process to identify it
          album['type'] = 'album'

          interpreter = FacebookEventInterpreter(post, asm, self.oauth_config)

          # send event message
          callback(create_facebook_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), album))

        # if

        album_id = album['id']

        # check for any new photos in the album
        photos_url = unicode('{0}{1}{2}?{3}').format(self.oauth_config['endpoint'],
                                                     album_id,
                                                     self.PHOTOS_COLLECTION,
                                                     urllib.urlencode(args))
        while photos_url:

          photos_obj = json_serializer.load(urllib2.urlopen(photos_url))

          for photo in photos_obj.get('data', []):

            photo['type'] = 'photo'

            interpreter = FacebookEventInterpreter(post, asm, self.oauth_config)

            # event message
            callback(create_facebook_event(
                  asm.author_id,
                  CURRENT_STATE,
                  service_author_id,
                  interpreter.get_id(),
                  photo,
                  [create_event_link(data_access.service.name_to_id('facebook'), album_id)]))

          # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
          next_url = photos_obj['paging']['next'] if 'paging' in photos_obj and 'next' in photos_obj['paging'] else None
          photos_url = next_url if next_url and next_url != photos_url else None

        # while photos

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      next_url = albums_obj['paging']['next'] if 'paging' in albums_obj and 'next' in albums_obj['paging'] else None
      albums_url = next_url if next_url and next_url != albums_url else None

    # while albums

    # fetch all new checkins
    checkins_url = unicode('{0}{1}?{2}').format(self.oauth_config['endpoint'],
                                                self.CHECKIN_COLLECTION,
                                                urllib.urlencode(args))

    total_accepted = 0
    while checkins_url and total_accepted < self.MAX_EVENTS:

      checkins_obj = json_serializer.load(urllib2.urlopen(checkins_url))

      # process the item

      # TODO loop termination on various constraints is not exact

      # for element in the feed
      for checkin_obj in checkins_obj['data']:

        # filter checkins not directly from this user
        if checkin_obj['from']['id'] == service_author_id:

          # set the type to checkin.  When querying for checkins the
          # type property is missing
          checkin_obj['type'] = 'checkin'

          interpreter = FacebookEventInterpreter(post, asm, self.oauth_config)

          if self.screen_event(interpreter, state):
            total_accepted = total_accepted + 1
            callback(create_facebook_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), post))

      # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
      next_url = checkins_obj['paging']['next'] if 'paging' in checkins_obj and 'next' in checkins_obj['paging'] else None
      checkins_url = next_url if next_url and next_url != posts_url else None

    # while checkins

    # terminate the fetch
    self.fetch_end(state)
