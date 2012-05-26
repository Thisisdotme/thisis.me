'''
Created on May 9, 2012

@author: howard
'''
import oauth2 as oauth
import json
from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter

from tim_commons.oauth import make_request


class LinkedinEventInterpreter(ServiceEventInterpreter):

  # TODO - not sure I want this
  def __init__(self, json, author_service_map, oauth_config):
    super(LinkedinEventInterpreter, self).__init__(json, author_service_map, oauth_config)
    self._client = None

  def get_oauth_client(self):
    # only create the client if it's requested
    if not self._client:
      consumer = oauth.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
      token = oauth.Token(key=self.author_service_map.access_token, secret=self.author_service_map.access_token_secret)
      self._client = oauth.Client(consumer, token)

    return self._client

  def get_id(self):
    return self.json['updateKey']

  def get_time(self):
    return datetime.utcfromtimestamp(int(self.json['timestamp'] / 1000))

  def get_headline(self):

    headline = None

    # share updates
    if self.json['updateType'] == 'SHAR':
      headline = self.json['updateContent']['person']['currentShare'].get('comment')

    return headline

  def get_deck(self):

    deck = None

    updateType = self.json['updateType']

    # connection updates
    if updateType == 'CONN':
      deck = self.get_connection_deck()
    # share updates
    elif updateType == 'SHAR':
      deck = self.get_share_deck()
    # company follow updates
    elif updateType == 'MSFC':
      deck = self.get_company_follow_deck()
    # recommendation updates
    elif updateType == 'PREC' or updateType == 'SVPR':
      deck = self.get_recommendation_deck()
    elif updateType == 'JOBP':
      deck = self.get_job_posting_deck()
    # joined group update
    elif updateType == 'JGRP':
      deck = self.get_join_group_deck()
    # status updates
    elif updateType == 'STAT':
      deck = self.get_status_deck()

    return deck

  # TODO: need to remedy the headline, deck, content debate
  def get_content(self):
    return self.get_deck()

  def get_photo(self):

    photo = None

    if self.json['updateType'] == 'CONN':
      self.init_connection()
      photo = self.photo

    return photo

  def get_connection_deck(self):

    self.init_connection()
    connection = self.json['updateContent']['person']['connections']['values'][0]
    content = '%s is now connected to %s %s.' % (self.json['updateContent']['person']['firstName'], connection['firstName'], connection['lastName'])
    if self.headline:
      content = '%s  %s' % (content, self.headline)
    return content

  def get_share_deck(self):

    currShare = self.json['updateContent']['person']['currentShare']

    phrase = None
    if 'content' in currShare:
      title = currShare['content'].get('title')
      description = currShare['content'].get('description')
      if title and description:
        phrase = '%s; %s' % (title, description)
      else:
        phrase = title if title else description

      shortenedUrl = currShare['content'].get('shortenedUrl')
      if shortenedUrl:
        phrase = '%s (%s)' % (phrase, shortenedUrl) if phrase else shortenedUrl

    return phrase

  def get_company_follow_deck(self):

    person = self.json['updateContent']['companyPersonUpdate']['person']
    action = self.json['updateContent']['companyPersonUpdate']['action']
    return '%s %s %s' % (person['firstName'], action['code'], self.json['updateContent']['company']['name'])

  def get_recommendation_deck(self):

    person = self.json['updateContent']['person']
    recommendation = person['recommendationsGiven']['recommendation']
    return '%s recommends %s %s %s' % (person['firstName'], recommendation['recommendationType']['code'], recommendation['recommendee']['firstName'], recommendation['recommendee']['lastName'])

  def get_job_posting_deck(self):

    job = self.json['updateContent']['job']
    person = self.json['updateContent']['job']['jobPoster']
    return '%s posted the job: %s at %s' % (person['firstName'], job['position'], job['company'])

  def get_join_group_deck(self):
    return self.json['updateContent']['person']['memberGroups']['values'][0]['name']

  def get_status_deck(self):
    return self.json['updateContent']['person']['currentStatus']

  def init_connection(self):

    connection = self.json['updateContent']['person']['connections']['values'][0]

    if connection['id'] != 'private' and self._client is None:

      url = '%speople/id=%s:(headline,summary,picture-url)' % (self.oauth_config['endpoint'], connection['id'])

      # request the user's updates
      json_str = make_request(self.get_oauth_client(), url, {'x-li-format': 'json'})
      json_obj = json.loads(json_str)

      self.headline = json_obj.get('headline')
      self.summary = json_obj.get('summary')
      self.photo = json_obj.get('pictureUrl')
