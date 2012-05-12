'''
Created on May 10, 2012

@author: howard
'''
import json
import urllib2
import urllib

from tim_commons.messages import create_facebook_event
from event_updater import EventUpdater


class FacebookEventUpdater(EventUpdater):

  def fetch(self, tim_author_id, service_author_id, service_event_id, callback):

    super(FacebookEventUpdater, self).fetch(tim_author_id, service_author_id, service_event_id, callback)

    asm = self.get_author_service_map(tim_author_id)

    args = {'access_token': asm.access_token}

    # fetch latest version of event
    path = self.oauth_config['endpoint'] % '%s?%s' % (service_event_id, urllib.urlencode(args))

    event_json = json.load(urllib2.urlopen(path))

    callback(create_facebook_event(service_author_id, tim_author_id, event_json))
