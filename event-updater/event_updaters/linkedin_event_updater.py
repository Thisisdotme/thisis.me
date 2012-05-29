import oauth2 as oauth

from tim_commons.oauth import make_request
from tim_commons.messages import create_linkedin_event
from tim_commons import json_serializer

from event_updater import EventUpdater

UPDATE_COMMENTS = '%speople/~/network/updates/key=%s/update-comments'
UPDATE_LIKES = '%speople/~/network/updates/key=%s/likes'


class LinkedinEventUpdater(EventUpdater):
  def fetch(self, service_id, service_author_id, service_event_id, callback):
    asm = self.get_author_service_map(service_author_id)

    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(asm.access_token, asm.access_token_secret)
    client = oauth.Client(consumer, token)

    url = UPDATE_COMMENTS % (self.oauth_config['endpoint'],
                             service_event_id)

    # TODO: update_json =
    json_serializer.load_string(make_request(client, url, {'x-li-format': 'json'}))

    url = UPDATE_LIKES % (self.oauth_config['endpoint'],
                          service_event_id)

    # TODO: likes_json =
    json_serializer.load_string(make_request(client, url, {'x-li-format': 'json'}))

    # merge update and likes together into one JSON

    event_json = None

    callback(create_linkedin_event(service_author_id, asm.tim_author_id, event_json))
