'''
Created on May 2, 2012

@author: howard
'''
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tim_commons.app_base import AppBase
from event_collectors.event_collector_factory import EventCollectorFactory
from tim_commons.message_queue import (create_message_client, join, send_messages)

DBSession = sessionmaker()


class EventCollectorDriver(AppBase):

  def display_usage(self):
    return 'Usage: ' + self.name + '.py <<service_name>> \nExample: ' + self.name + '.py facebook'

  def _handle_event(self, tim_author_id, service_author_id, jsonEventDict):

    msg = self.collector.create_event_message(tim_author_id, service_author_id, jsonEventDict)
    send_messages(self.client, self.send_queue, [msg])

  def _handle_message_receive(self, jsonDict):

    msg = jsonDict['message']

    def handle_event_callback(tim_author_id, service_author_id, jsonEventDict):
      self._handle_event(tim_author_id, service_author_id, jsonEventDict)

    self.collector.fetch(msg['service_author_id'], handle_event_callback)

  def main(self):

    self.log.info("Beginning: " + self.name)

    service_name = self.args[0]
    if not service_name:
      self.log.fatal("Missing required argument: service-name")
      return

    # read the db url from the config
    dbUrl = self.config['db_config']['sqlalchemy.url']

    # initialize the db engine & session
    engine = create_engine(dbUrl, encoding='utf-8', echo=False)
    DBSession.configure(bind=engine)

    db_session = DBSession()

    # get the oauth application config for this collector
    oauth_config = self.config['oauth'][service_name]

    # get the queue_config
    queue_config = self.config['queue_config']
    self.send_queue = queue_config[service_name]['send']

    self.log.info('Queue URL: %s' % queue_config['url'])
    self.log.info('Receive queue: %s' % queue_config[service_name]['receive'])
    self.log.info('Send queue: %s' % self.send_queue)

    self.collector = EventCollectorFactory.from_service_name(service_name, db_session, oauth_config, self.log)

    self.client = create_message_client(queue_config['url'])

    def handle_receieve_callback(jsonDict):
      self._handle_message_receive(jsonDict)

    join(self.client, queue_config[service_name]['receive'], handle_receieve_callback)

    self.log.info("Finished: " + self.name)


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventCollectorDriver(1).main())
