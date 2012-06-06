import urllib
import oauth2 as oauth
from datetime import datetime

from tim_commons.oauth import make_request
from tim_commons.messages import create_twitter_event
from tim_commons import json_serializer

from event_interpreter.twitter_event_interpreter import TwitterEventInterpreter
from event_collector import EventCollector


USER_INFO = 'account/verify_credentials.json'
USER_TIMELINE = 'statuses/user_timeline.json'


class TwitterEventCollector(EventCollector):

  def fetch(self, service_author_id, callback):

    super(TwitterEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(asm.access_token, asm.access_token_secret)

    client = oauth.Client(consumer, token)

    args = {'include_rts': 1,
            'include_entities': 1,
            'trim_user': 1,
            'count': 100}

    if asm.most_recent_event_id:
      args['since_id'] = asm.most_recent_event_id

    # API endpoint for getting user timeline
    url = '%s%s?%s' % (self.oauth_config['endpoint'],
                       USER_TIMELINE,
                       urllib.urlencode(args))

    min_age = datetime.utcnow() - self.LOOKBACK_WINDOW
    last_id = None
    while True:

      content = make_request(client, url)

      raw_json = json_serializer.load_string(content)

      # check if nothing returned and terminate loop if so
      if len(raw_json) == 0:
        break

      for post in raw_json:

        # process the item
        #print json.dumps(post, sort_keys=True, indent=2)

        interpreter = TwitterEventInterpreter(post, asm, self.oauth_config)
        last_id = interpreter.get_id()

        # terminate fetching any more events if we've gone beyond the lookback window
        if interpreter.get_create_time() < min_age:
          url = None
          break

        if self.screen_event(interpreter, state):
          callback(create_twitter_event(service_author_id, asm.author_id, post))

      if not url:
        break

      # setup for the next page (if any)
      args['max_id'] = long(last_id) - 1
      url = '%s%s?%s' % (self.oauth_config['endpoint'],
                         USER_TIMELINE,
                         urllib.urlencode(args))

    # terminate the fetch
    self.fetch_end(state)
