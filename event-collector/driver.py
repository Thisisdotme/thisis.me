import sys
import logging

from tim_commons.app_base import AppBase
from event_collectors import event_collector
from tim_commons.message_queue import (create_message_client, join, send_messages, create_queues)
from tim_commons import db


class EventCollectorDriver(AppBase):

  def display_usage(self):
    return 'Usage: ' + self.name + '.py <<service_name>> \nExample: ' + self.name + '.py facebook'

  def _handle_event(self, msg):
    send_messages(self.client, self.send_queue, [msg])

  def _handle_message_receive(self, msg):

    def handle_event_callback(callback_msg):
      self._handle_event(callback_msg)

    with db.Context():
      self.collector.fetch(msg['message']['service_author_id'], handle_event_callback)

  def main(self):

    logging.info("Beginning: " + self.name)

    service_name = self.args[0]
    if not service_name:
      logging.fatal("Missing required argument: service-name")
      return

    # read the db url from the config
    db_url = self.config['db']['sqlalchemy.url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # get the oauth application config for this collector
    oauth_config = self.config['oauth'][service_name]

    # get the broker and queue config
    broker_url = self.config['broker']['url']
    queue_config = self.config['queues']
    self.send_queue = queue_config[service_name]['event']
    receive_queue = queue_config[service_name]['notification']

    logging.info('Queue broker URL: %s' % broker_url)
    logging.info('Receive queue: %s' % receive_queue)
    logging.info('Send queue: %s' % self.send_queue)

    self.collector = event_collector.from_service_name(service_name, oauth_config)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = create_message_client(broker_url)

    create_queues(self.client, [self.send_queue, receive_queue])

    def handle_receieve_callback(callback_msg):
      self._handle_message_receive(callback_msg)

    join(self.client, receive_queue, handle_receieve_callback)

    logging.info("Finished: " + self.name)

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventCollectorDriver(1).main())
