import urllib2
import urllib

from tim_commons.messages import create_instagram_event
from tim_commons import json_serializer
from event_updater import EventUpdater


class InstagramEventUpdater(EventUpdater):

  MEDIA_INFO = 'media/'

  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    args = {'access_token': asm.access_token}

    # fetch latest version of event
    url = '%s%s%s?%s' % (self.oauth_config['endpoint'], self.MEDIA_INFO, service_event_id, urllib.urlencode(args))

    raw_obj = json_serializer.load(urllib2.urlopen(url))

    callback(create_instagram_event(service_author_id, asm.author_id, raw_obj['data']))
