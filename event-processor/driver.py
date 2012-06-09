import sys
import datetime
import logging

from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client, join, create_queues)
from tim_commons import db
from event_processors import event_processor


class EventProcessorDriver(AppBase):
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
    # get the maximum priority
    max_priority = int(self.config['scanner']['maximum_priority'])
    min_duration = float(self.config['scanner']['iteration_minimum_duration'])
    min_duration = datetime.timedelta(seconds=min_duration)

    # initialize the db engine & session
    db.configure_session(db_url)

    services = services_configuration(self.option.services, self.config)

    # Get a list of all the queues and all the handler
    queues = []
    handlers = []
    for service in services:
      # List queues
      queues.append(service['queue'])

      # Create handlers
      processor = event_processor.from_service_name(service['name'],
                                                    max_priority,
                                                    min_duration,
                                                    service['oauth'])
      handler = {'queue': service['queue'],
                 'handler': create_processor_handler(processor)}
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
           'queue': config['queues'][service]['event']} for service in services]


def create_processor_handler(processor):
  def handler(message):
    body = message['message']
    with db.Context():
      processor.process(body['tim_author_id'],
                        body['service_author_id'],
                        body['service_event_json'])
  return handler


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventProcessorDriver(1).main())
