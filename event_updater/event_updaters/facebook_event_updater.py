import urllib2
import urllib

from tim_commons.messages import create_facebook_event, CURRENT_STATE
from tim_commons import json_serializer

from event_interpreter.facebook_event_interpreter import FacebookEventInterpreter

from event_updater import EventUpdater


class FacebookEventUpdater(EventUpdater):
  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    args = {'access_token': asm.access_token}

    # fetch latest version of event
    path = '%s%s?%s' % (self.oauth_config['endpoint'], service_event_id, urllib.urlencode(args))

    json_obj = json_serializer.load(urllib2.urlopen(path))

    interpreter = FacebookEventInterpreter(json_obj, asm, self.oauth_config)

    callback(create_facebook_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), json_obj))
