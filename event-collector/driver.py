import sys
import logging

from tim_commons.app_base import AppBase
from event_collectors import event_collector
from tim_commons.message_queue import (create_message_client, join, send_messages, create_queues)
from tim_commons import db


class EventCollectorDriver(AppBase):

  def display_usage(self):
    return 'usage: %prog [options]'

  def init_args(self):
    self.option_parser.add_option('--service',
                                  dest='services',
                                  action='append',
                                  default=[],
                                  help='Services to process')

  def parse_args(self, ignore):
    (self.option, ignore) = self.option_parser.parse_args()

    if ignore:
      self.option_parser.print_help()
      sys.exit()

  def create_event_callback(self):
    def handler(message):
      send_messages(self.client, [message])

    return handler

  def create_collector_handler(self, collector):
    def handler(message):
      with db.Context():
        collector.fetch(message['message']['service_author_id'], self.create_event_callback())

    return handler

  def main(self):
    logging.info("Beginning: " + self.name)

    # read the db url from the config
    db_url = self.config['db']['sqlalchemy.url']
    # get the broker and queue config
    broker_url = self.config['broker']['url']

    # initialize the db engine & session
    db.configure_session(db_url)

    services = services_configuration(self.option.services, self.config)

    # Get a list of all the queues and all the handlers
    queues = []
    handlers = []
    for service in services:
      # List queues
      queues.append(service['send_queue'])
      queues.append(service['receive_queue'])

      # Create handlers
      collector = event_collector.from_service_name(service['name'], service['oauth'])
      handler = {'queue': service['receive_queue'],
                 'handler': self.create_collector_handler(collector)}
      handlers.append(handler)

    logging.info('Queue broker URL: %s', broker_url)
    logging.info('Active queues: %s', queues)
    logging.debug('Active handlers: %s', handlers)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = create_message_client(broker_url)
    create_queues(self.client, queues)

    join(self.client, handlers)

    logging.info("Finished: " + self.name)


def services_configuration(services, config):
  # If services is empty then get all the services in the configuration
  if not services:
    for service in config['queues'].iterkeys():
      services.append(service)

  return [{'name': service,
           'oauth': config['oauth'][service],
           'send_queue': config['queues'][service]['event'],
           'receive_queue': config['queues'][service]['notification']} for service in services]


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventCollectorDriver(1).main())
