import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client, join, create_queues, send_messages)
from tim_commons import db
from event_updaters import event_updater


class EventUpdaterDriver(AppBase):
  def display_usage(self):
    return 'usage: %prog [options]'

  def init_args(self):
    self.option_parser.add_option('--service',
                                  dest='services',
                                  action='append',
                                  default=[],
                                  help='Service to process')

  def parse_args(self, ignore):
    (self.option, ignore) = self.option_parser.parse_args()

    if ignore:
      self.option_parser.print_help()
      sys.exit()

  def main(self):
    logging.info("Beginning: " + self.name)

    # read the db url from the config
    db_url = self.config['db']['sqlalchemy.url']
    # get the broker and queue config
    broker_url = self.config['broker']['url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # get message broker client and store in instance -- used for both receiving and sending
    client = create_message_client(broker_url)

    services = services_configuration(self.option.services, self.config)

    durable_queues = []
    non_durable_queues = []
    handlers = []
    for service in services:
      # List queues
      durable_queues.append(service['send_queue'])
      non_durable_queues.append(service['receive_queue'])

      # Create handlers
      updater = event_updater.from_service_name(service['name'], service['oauth'])
      handler = {'queue': service['receive_queue'],
                 'handler': create_updater_handler(updater, client)}
      handlers.append(handler)

    logging.info('Queue broker URL: %s', broker_url)
    logging.info('Active queue: %s %s', durable_queues, non_durable_queues)
    logging.debug('Active handlers: %s', handlers)

    create_queues(client, non_durable_queues, durable=False)
    create_queues(client, durable_queues)

    join(client, handlers)

    logging.info("Finished: " + self.name)


def services_configuration(services, config):
  # If services is empty then get all the services in the configuration
  if not services:
    for service in config['queues'].iterkeys():
      services.append(service)

  return [{'name': service,
           'oauth': config['oauth'][service],
           'send_queue': config['queues'][service]['event'],
           'receive_queue': config['queues'][service]['update']} for service in services]


def create_event_callback(client):
  def handler(message):
    send_messages(client, [message])

  return handler


def create_updater_handler(updater, client):
  def handler(message):
    body = message['message']
    with db.Context():
      updater.fetch(body['service_id'],
                    body['service_author_id'],
                    body['service_event_id'],
                    create_event_callback(client))

  return handler

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventUpdaterDriver(1).main())
