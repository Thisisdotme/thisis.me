'''
Created on May 4, 2012

@author: howard
'''
import json
import urllib
import oauth2 as oauth
from datetime import datetime
from time import mktime
import copy

from tim_commons.oauth import make_request
from tim_commons.messages import create_linkedin_event

from event_interpreter.linkedin_event_interpreter import LinkedinEventInterpreter
from event_collector import EventCollector

UPDATE_RESOURCE = 'people/~/network/updates'


class LinkedinEventCollector(EventCollector):

  PAGE_SIZE = 200

  SUPPORTED_TYPES = ['SHAR', 'JOBP', 'CONN', 'NCON', 'ANSW', 'MSFC', 'PREC', 'SVPR', 'STAT']
  IGNORED_TYPES = ['PROF', 'PICU', 'APPM']

  def fetch(self, service_author_id, callback):

    super(LinkedinEventCollector, self).fetch(service_author_id, callback)

    state = self.fetch_begin(service_author_id)

    self.fetch_log_info(state)

    asm = state['asm']

    service_author_id = asm.service_author_id

    min_age = datetime.utcnow() - self.LOOKBACK_WINDOW

    # setup what we need for oauth
    consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
    token = oauth.Token(key=asm.access_token, secret=asm.access_token_secret)
    client = oauth.Client(consumer, token)

    args = {'scope': 'self',
            'count': self.PAGE_SIZE}

    # optimization to request only those since we've last updated
    if asm.most_recent_event_timestamp:
      args['after'] = int(mktime((asm.most_recent_event_timestamp - self.LAST_UPDATE_OVERLAP).timetuple())) * 1000
    else:
      # limit to only one year of data
      args['after'] = int(mktime((datetime.utcnow() - self.LOOKBACK_WINDOW).timetuple())) * 1000

    args['after'] = 0

    offset = 0
    args['start'] = offset

    url = '%s%s?%s' % (self.oauth_config['endpoint'], UPDATE_RESOURCE, urllib.urlencode(args, True))

    total_count = 0
    while url:

      # request the user's updates
      content = make_request(client, url, {'x-li-format': 'json'})

      raw_json = json.loads(content)

      if raw_json.get('_total', 0) == 0:
        url = None
        break

      for post in raw_json.get('values', []):

#        print json.dumps(post, sort_keys=True, indent=2)

        update_type = post['updateType']

        if update_type in self.SUPPORTED_TYPES:

          if update_type == 'CONN' and post['updateContent']['person']['id'] == service_author_id:

            # the response can contain multiple connections that the member has made.  We'll
            # separate them into individual responses
            postClone = copy.deepcopy(post)

            for connection in post['updateContent']['person']['connections']['values']:

              postClone['updateContent']['person']['connections'] = {"_total": 1, "values": [copy.deepcopy(connection)]}

              interpreter = LinkedinEventInterpreter(postClone)

              if interpreter.get_time() < min_age:
                url = None
                break

              if self.screen_event(interpreter, state):
                callback(create_linkedin_event(service_author_id, asm.author_id, postClone))

          elif (update_type == 'PREC' or update_type == 'SVPR') and post['updateContent']['person']['id'] == service_author_id:

            interpreter = LinkedinEventInterpreter(post)

            if interpreter.get_time() < min_age:
              url = None
              break

            if self.screen_event(interpreter, state):
              callback(create_linkedin_event(service_author_id, asm.author_id, post))

          elif update_type == 'SHAR':

            interpreter = LinkedinEventInterpreter(post)

            if interpreter.get_time() < min_age:
              url = None
              break

            if self.screen_event(interpreter, state):
              callback(create_linkedin_event(service_author_id, asm.author_id, post))

          elif update_type == 'MSFC' and post['updateContent']['companyPersonUpdate']['person']['id'] == service_author_id:

            interpreter = LinkedinEventInterpreter(post)

            if interpreter.get_time() < min_age:
              url = None
              break

            if self.screen_event(interpreter, state):
              callback(create_linkedin_event(service_author_id, asm.author_id, post))

          elif update_type == 'JOBP' and post['updateContent']['job']['jobPoster']['id'] == service_author_id:

            interpreter = LinkedinEventInterpreter(post)

            if interpreter.get_time() < min_age:
              url = None
              break

            if self.screen_event(interpreter, state):
              callback(create_linkedin_event(service_author_id, asm.author_id, post))

          elif update_type == 'JGRP' and post['updateContent']['person']['id'] == service_author_id:

            # the response can contain multiple groups that the member has joined.  We'll
            # separate them into individual responses
            postClone = copy.deepcopy(post)

            for group in post['updateContent']['person']['memberGroups']['values']:

              postClone['updateContent']['person']['memberGroups'] = {"_total": 1, "values": [copy.deepcopy(group)]}

              interpreter = LinkedinEventInterpreter(postClone)

              if interpreter.get_time() < min_age:
                url = None
                break

              if self.screen_event(interpreter, state):
                callback(create_linkedin_event(service_author_id, asm.author_id, postClone))

          elif update_type == 'STAT' and post['updateContent']['person']['id'] == service_author_id:

            interpreter = LinkedinEventInterpreter(post)

            if interpreter.get_time() < min_age:
              url = None
              break

            if self.screen_event(interpreter, state):
              callback(create_linkedin_event(service_author_id, asm.author_id, post))

        else:
          if not update_type in self.IGNORED_TYPES:
            self.log.warning('???? skipping linkedIn event: %s' % update_type)

        # if the url is None stop
        if not url:
          break

      # if the url is None stop
      if not url:
        break

      total_count = total_count + raw_json['_count'] if '_count' in raw_json else raw_json['_total']
      if raw_json['_total'] == total_count:
        url = None
        break

      offset = offset + self.PAGE_SIZE
      args['start'] = offset
      url = '%s%s?%s' % (self.oauth_config['endpoint'], UPDATE_RESOURCE, urllib.urlencode(args, True))

    print total_count

    # terminate the fetch
    self.fetch_end(state)
