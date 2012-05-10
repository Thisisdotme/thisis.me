'''
Created on May 4, 2012

@author: howard
'''
import json
import urllib
import oauth2 as oauth

from tim_commons.oauth import make_request
from tim_commons.messages import create_twitter_event

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

    user_id = int(asm.service_author_id)

    # API endpoing for querying user info
    url = '%s%s' % (self.oauth_config['endpoint'], USER_INFO)
    user_info_json = json.loads(make_request(client, url))

    twitter_user_id = user_info_json['id']

    if twitter_user_id != user_id:
      raise Exception("Bad state - mis-matched twitter user ids")

    # API endpoint for getting user timeline
    page = 1
    url = '%s%s?%s' % (self.oauth_config['endpoint'],
                       USER_TIMELINE,
                       urllib.urlencode({'include_rts': '1', 'include_entities': '1', 'count': '200', 'page': page}))

    total_accepted = 0
    while url and total_accepted < self.MAX_EVENTS:

      content = make_request(client, url)

      raw_json = json.loads(content)

      # check if nothing returned and terminate loop if so
      if len(raw_json) == 0:
        url = None
        continue

      for post in raw_json:

        # process the item
        #print json.dumps(post, sort_keys=True, indent=2)

        if self.screen_event(TwitterEventInterpreter(post), state):
          total_accepted = total_accepted + 1
          callback(create_twitter_event(service_author_id, asm.author_id, post))

      # setup for the next page (if any)
      page = page + 1
      url = '%s%s?%s' % (self.oauth_config['endpoint'],
                         USER_TIMELINE,
                         urllib.urlencode({'include_rts': '1', 'include_entities': '1', 'count': '200', 'page': page}))

    # terminate the fetch
    self.fetch_end(state)
