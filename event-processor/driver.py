#!/usr/bin/env python

'''
Created on May 2, 2012

@author: howard
'''
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client, join, create_queues)
from event_processors.event_processor_factory import EventProcessorFactory

DBSession = sessionmaker()


class EventProcessorDriver(AppBase):

  def display_usage(self):
    return 'Usage: ' + self.name + '.py <<service_name>> \nExample: ' + self.name + '.py facebook'

  def _handle_message_receive(self, msg):
    body = msg['message']
    self.processor.process(body['tim_author_id'], body['service_author_id'], body['service_event_json'])

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

    # get the broker and queue config
    broker_url = self.config['broker']['url']
    receive_queue = self.config['queues'][service_name]['event']

    self.log.info('Queue broker URL: %s' % broker_url)
    self.log.info('Receive queue: %s' % receive_queue)

    self.processor = EventProcessorFactory.from_service_name(service_name, db_session, self.log)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = create_message_client(broker_url)

    create_queues(self.client, [receive_queue])

    def handle_receieve_callback(callback_msg):
      self._handle_message_receive(callback_msg)

    join(self.client, receive_queue, handle_receieve_callback)

    self.log.info("Finished: " + self.name)

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventProcessorDriver(1).main())
