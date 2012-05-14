#!/usr/bin/env python

'''
Created on May 2, 2012

@author: howard
'''

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client, join, create_queues, send_messages)
from event_updaters.event_updater_factory import EventUpdaterFactory

DBSession = sessionmaker()


class EventUpdaterDriver(AppBase):

  def display_usage(self):
    return 'Usage: ' + self.name + '.py <<service_name>> \nExample: ' + self.name + '.py facebook'

  def _handle_event(self, msg):
    send_messages(self.client, self.send_queue, [msg])

  def _handle_message_receive(self, msg):

    def handle_event_callback(callback_msg):
      self._handle_event(callback_msg)

    body = msg['message']
    self.updater.fetch(body['tim_author_id'], body['service_author_id'], body['service_event_id'], handle_event_callback)

  def main(self):

    self.log.info("Beginning: " + self.name)

    service_name = self.args[0]
    if not service_name:
      self.log.fatal("Missing required argument: service-name")
      return

    # read the db url from the config
    db_url = self.config['db']['sqlalchemy.url']

    # initialize the db engine & session
    engine = create_engine(db_url, encoding='utf-8', echo=False)
    DBSession.configure(bind=engine)

    db_session = DBSession()

    # get the oauth application config for this collector
    oauth_config = self.config['oauth'][service_name]

    # get the broker and queue config
    broker_url = self.config['broker']['url']
    queue_config = self.config['queues']
    self.send_queue = queue_config[service_name]['event']
    receive_queue = queue_config[service_name]['update']

    self.log.info('Queue broker URL: %s' % broker_url)
    self.log.info('Receive queue: %s' % receive_queue)
    self.log.info('Send queue: %s' % self.send_queue)

    self.updater = EventUpdaterFactory.from_service_name(service_name, db_session, oauth_config, self.log)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = create_message_client(broker_url)

    create_queues(self.client, [receive_queue])

    def handle_receieve_callback(callback_msg):
      self._handle_message_receive(callback_msg)

    join(self.client, receive_queue, handle_receieve_callback)

    self.log.info("Finished: " + self.name)

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventUpdaterDriver(1).main())
