import urllib2
import urllib

from tim_commons.messages import create_googleplus_event
from tim_commons import json_serializer
from event_updater import EventUpdater


class GoogleplusEventUpdater(EventUpdater):

  ACTIVITY_INFO = 'activities/'

  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    # we need to exchange the refresh token for an access token
    query_args = urllib.urlencode([('client_id', self.oauth_config['key']),
                                   ('client_secret', self.oauth_config['secret']),
                                   ('refresh_token', asm.access_token),
                                   ('grant_type', 'refresh_token')])
    raw_obj = json_serializer.load(urllib2.urlopen(self.oauth_config['oauth_exchange_url'], query_args))

    access_token = raw_obj['access_token']

    args = {'access_token': access_token}

    # fetch latest version of event
    url = '%s%s%s?%s' % (self.oauth_config['endpoint'], self.ACTIVITY_INFO, service_event_id, urllib.urlencode(args))

    raw_obj = json_serializer.load(urllib2.urlopen(url))

    callback(create_googleplus_event(service_author_id, asm.author_id, raw_obj))
