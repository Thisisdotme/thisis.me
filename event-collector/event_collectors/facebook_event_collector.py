'''
Created on May 4, 2012

@author: howard
'''
import json
import urllib
import urllib2
from time import mktime

from event_collector import EventCollector
from tim_commons.messages import create_facebook_event


class FacebookEventCollector(EventCollector):

  SERVICE_NAME = "facebook"

  def create_event_message(self, tim_author_id, service_author_id, jsonEventDict):
    return create_facebook_event(service_author_id, tim_author_id, jsonEventDict)

  def fetch(self, tim_author_id, service_author_id, oauth_access_token, oauth_access_secret, callback):

    super(FacebookEventCollector, self).fetch(service_author_id, callback)

    asm = self.get_author_service_map_for_fetch(service_author_id)

    try:

      args = {'access_token': oauth_access_token}

      # fetch all the pages /me/feed
      path = self.oauth_config['endpoint'] % 'me/picture?%s' % urllib.urlencode(args)
      req = urllib2.Request(path)
      res = urllib2.urlopen(req)

      # optimization to request only those since we've last updated
      if asm.last_update_time:
        since = int(mktime(asm.last_update_time.timetuple()))
        args['since'] = since

      # fetch all the pages /me/feed
      path = self.oauth_config['endpoint'] % 'me/feed?%s' % urllib.urlencode(args)

      total_accepted = 0
      while path and total_accepted < 200:

        try:
          req = urllib2.Request(path)
          res = urllib2.urlopen(req)
          rawJSON = json.loads(res.read())
        except Exception, e:
          self.log.error('error parsing /me/feed')
          self.log.error(e)

          # abort for this author but continue on
          path = None
          continue

        # process the item
        #print json.dumps(rawJSON, sort_keys=True, indent=2)

        # loop termination on various constraints is not exact

        # for element in the feed
        for post in rawJSON['data']:

          # currently only interested in 'status' posts from the user
#          if post['type'] == 'status' and post['from']['id'] == fbUserId:
          if post['from']['id'] == service_author_id:

#            # check if I'm in the story tags anywhere.
#            found = False
#            if post.get('type') == 'status' and post.has_key('story_tags'):
#              storyTags = post['story_tags']
#              for tagKey in storyTags:
#                tag = storyTags.get(tagKey)
#                for tagItem in tag:
#                  if tagItem['id'] == fbUserId:
#                    found = True
#
#            if found:
#              continue

            # if this is a status update and there are no actions then skip it
            if post.get('type') == 'status' and post.get('actions') is None:
              continue

            callback(tim_author_id, service_author_id, post)

          # if
        # for

        # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
        nextPath = rawJSON['paging']['next'] if 'paging' in rawJSON and 'next' in rawJSON['paging'] else None
        path = nextPath if nextPath and nextPath != path else None

    except Exception, e:
      self.log.error("****ERROR****")
      self.log.error(e)
      raise
