import urllib2
import urllib

from tim_commons.messages import create_foursquare_event
from tim_commons import json_serializer
from event_updater import EventUpdater

CHECKIN_RESOURCE = 'checkins/'


class FoursquareEventUpdater(EventUpdater):
  def fetch(self, service_id, service_author_id, service_event_id, callback):
    asm = self.get_author_service_map(service_author_id)

    args = {'oauth_token': asm.access_token,
            'v': 20120130}

    url = '%s%s%s?%s' % (self.oauth_config['endpoint'],
                         CHECKIN_RESOURCE,
                         service_event_id,
                         urllib.urlencode(args))

    event_json = json_serializer.load(urllib2.urlopen(url))

    # check for error
    if event_json['meta']['code'] != 200:
      raise Exception('Foursquare error response: %s' % event_json['meta']['code'])

    '''
      TODO: there should be a generalized mechanism for pruning unwanted properties from
            the json

      With Foursquare we're going to eliminate the user property (we know all about the user) and
      it doesn't appear in the checkin definition returned by "users/self/checkins" apparently
      by design as foursquare designates this event as optional and the user context is clearly
      defined by the call

      The following two properties don't appear in the "users/self/checkins" resource so each new
      foursquare event will immediately update.  If the user executes another checkin within
      60 minutes its possible the collector will get the event again because of the 60 minute
      overlap cause this event to "flap".  It's minor but noteworthy.

      del checkin_json['score']
      del checkin_json['venue']['specials']
    '''

    checkin_json = event_json['response']['checkin']

    if 'user' in checkin_json:
      del checkin_json['user']

    callback(create_foursquare_event(service_author_id, asm.author_id, checkin_json))
