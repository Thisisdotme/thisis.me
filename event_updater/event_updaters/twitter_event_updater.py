import urllib
import urllib2
import oauth2 as oauth

from tim_commons.oauth import make_request
from tim_commons.messages import create_twitter_event, CURRENT_STATE
from tim_commons import json_serializer

from event_interpreter.twitter_event_interpreter import TwitterEventInterpreter

from event_updater import EventUpdater

TWEET_STATUS = '%sstatuses/show.json?%s'


class TwitterEventUpdater(EventUpdater):

  def fetch(self, service_id, service_author_id, service_event_id, callback):

    asm = self.get_author_service_map(service_author_id)

    # TODO - temporary until we figure out a better solution for
    # not over-driving Twitter with un-authenticated events
    if not asm.access_token:
      return

    if asm.access_token:
      consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
      token = oauth.Token(asm.access_token, asm.access_token_secret)
      client = oauth.Client(consumer, token)

    args = {'id': service_event_id,
            'include_entities': '1',
            'trim_user': '1'}

    # if not authenticated provide the user_id query arg
    if not asm.access_token:
      args['user_id'] = asm.service_author_id

    url = TWEET_STATUS % (self.oauth_config['endpoint'],
                          urllib.urlencode(args))

    # TODO - remove the try/except once figure out a better solution for not
    # exceeding Twitter's rate limits
    try:
      json_obj = json_serializer.load_string(make_request(client, url)) if asm.access_token \
                 else json_serializer.load(urllib2.urlopen(url))
    except urllib2.URLError, e:
      import logging
      logging.error('ERROR REQUEST URL: {0}'.format(url))
      logging.error('ERROR REASON: {0}, {1}'.format(e.code, e.read()))
      raise

    interpreter = TwitterEventInterpreter(json_obj, asm, self.oauth_config)

    callback(create_twitter_event(asm.author_id, CURRENT_STATE, service_author_id, interpreter.get_id(), json_obj))
