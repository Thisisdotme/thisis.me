import urllib2
import urllib

from tim_commons.messages import create_instagram_event, CURRENT_STATE
from tim_commons import json_serializer

from event_interpreter.instagram_event_interpreter import InstagramEventInterpreter

from event_updater import EventUpdater


class InstagramEventUpdater(EventUpdater):

  MEDIA_INFO = 'media/'

  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    if asm.access_token:
      access_token = asm.access_token
    else:
      access_token = self.oauth_config['user1_access_token']

    args = {'access_token': access_token}

    # fetch latest version of event
    url = '{0}{1}{2}?{3}'.format(self.oauth_config['endpoint'], self.MEDIA_INFO, service_event_id, urllib.urlencode(args))

    raw_obj = json_serializer.load(urllib2.urlopen(url))

    post = raw_obj['data']

    interpreter = InstagramEventInterpreter(post, asm, self.oauth_config)

    callback(create_instagram_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), post))