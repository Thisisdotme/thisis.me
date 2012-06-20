import urllib
import oauth2 as oauth

from tim_commons.oauth import make_request
from tim_commons.messages import create_twitter_event
from tim_commons import json_serializer

from event_updater import EventUpdater

TWEET_STATUS = '%sstatuses/show.json?%s'


class TwitterEventUpdater(EventUpdater):
  def fetch(self, service_id, service_author_id, service_event_id, callback):
    asm = self.get_author_service_map(service_author_id)

    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(asm.access_token, asm.access_token_secret)

    client = oauth.Client(consumer, token)

    url = TWEET_STATUS % (self.oauth_config['endpoint'],
                         urllib.urlencode({'id': service_event_id,
                                           'include_entities': '1',
                                           'trim_user': '1'}))

    event_json = json_serializer.load_string(make_request(client, url))

    callback(create_twitter_event(service_author_id, asm.author_id, event_json))
