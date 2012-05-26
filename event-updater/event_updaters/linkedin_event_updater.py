'''
Created on May 10, 2012

@author: howard
'''
import json
import oauth2 as oauth

from tim_commons.oauth import make_request
from tim_commons.messages import create_linkedin_event

from event_updater import EventUpdater

UPDATE_COMMENTS = '%speople/~/network/updates/key=%s/update-comments'
UPDATE_LIKES = '%speople/~/network/updates/key=%s/likes'


class LinkedinEventUpdater(EventUpdater):

  def fetch(self, tim_author_id, service_author_id, service_event_id, callback):

    super(LinkedinEventUpdater, self).fetch(tim_author_id, service_author_id, service_event_id, callback)

    asm = self.get_author_service_map(tim_author_id)

    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(asm.access_token, asm.access_token_secret)
    client = oauth.Client(consumer, token)

    url = UPDATE_COMMENTS % (self.oauth_config['endpoint'],
                             service_event_id)

    update_json = json.loads(make_request(client, url, {'x-li-format': 'json'}))

    url = UPDATE_LIKES % (self.oauth_config['endpoint'],
                          service_event_id)

    likes_json = json.loads(make_request(client, url, {'x-li-format': 'json'}))

    # merge update and likes together into one JSON

    event_json = None

    callback(create_linkedin_event(service_author_id, tim_author_id, event_json))
