import oauth2 as oauth

from sqlalchemy import (and_)

from tim_commons.oauth import make_request
from tim_commons.messages import create_linkedin_event
from tim_commons import json_serializer
from tim_commons import db

from mi_schema.models import ServiceEvent

from event_updater import EventUpdater

UPDATE_COMMENTS = '%speople/~/network/updates/key=%s/update-comments'
UPDATE_LIKES = '%speople/~/network/updates/key=%s/likes'


class LinkedinEventUpdater(EventUpdater):
  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(asm.access_token, asm.access_token_secret)
    client = oauth.Client(consumer, token)

    # check if this event isCommentable or isLikable
    event_json, = db.Session().query(ServiceEvent.json). \
                               filter(and_(ServiceEvent.author_service_map_id == asm.id,
                                           ServiceEvent.event_id == service_event_id)).one()

    event_obj = json_serializer.load_string(event_json)

    update_obj = None
    if event_obj.get("isCommentable", False):
      url = UPDATE_COMMENTS % (self.oauth_config['endpoint'],
                               service_event_id)

      update_obj = json_serializer.load_string(make_request(client, url, {'x-li-format': 'json'}))

    likes_obj = None
    if event_obj.get("isLikable", False):

      url = UPDATE_LIKES % (self.oauth_config['endpoint'],
                            service_event_id)

      likes_obj = json_serializer.load_string(make_request(client, url, {'x-li-format': 'json'}))

    # merge update and likes together into one object
    if update_obj or likes_obj:

      if update_obj:
        event_obj['updateComments'] = update_obj
      if likes_obj:
        event_obj['isLiked'] = likes_obj['_total'] > 0
        event_obj['numLikes'] = likes_obj['_total']
        event_obj['likes'] = likes_obj

      callback(create_linkedin_event(service_author_id, asm.author_id, event_obj))
