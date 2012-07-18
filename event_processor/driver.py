#!/usr/bin/env python

import sys
import datetime
import logging

from tim_commons import message_queue, db, app_base
from event_processors import event_processor
import data_access.service


class EventProcessorDriver(app_base.AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--service',
                             dest='services',
                             action='append',
                             default=[],
                             help='Service to process')

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = db.create_url_from_config(config['db'])
    # get the broker and queue config
    broker_url = message_queue.create_url_from_config(config['broker'])
    # get the maximum priority
    max_priority = int(config['scanner']['maximum_priority'])
    min_duration = float(config['scanner']['iteration_minimum_duration'])
    min_duration = datetime.timedelta(seconds=min_duration)

    # initialize the db engine & session
    db.configure_session(db_url)
    data_access.service.initialize()

    services = services_configuration(options.services, config)

    # Get a list of all the handler
    handlers = []
    for service in services:
      # Create handlers
      processor = event_processor.from_service_name(service['name'],
                                                    max_priority,
                                                    min_duration,
                                                    service['oauth'])
      handler = {'queue': service['queue'],
                 'handler': create_processor_handler(processor)}
      handlers.append(handler)

    logging.info('Queue broker URL: %s', broker_url)
    logging.debug('Active handlers: %s', handlers)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = message_queue.create_message_client(broker_url)
    message_queue.create_queues_from_config(self.client, config['queues'])

    message_queue.join(self.client, handlers)

    logging.info("Finished...")


def services_configuration(services, config):
  # If services is empty then get all the services in the configuration
  if not services:
    for service in config['queues'].iterkeys():
      services.append(service)

  return [{'name': service,
           'oauth': config['oauth'][service],
           'queue': config['queues'][service]['event']['name']} for service in services]


def create_processor_handler(processor):
  def handler(message):
    body = message['message']
    with db.Context():
      processor.process(body['tim_author_id'],
                        body['service_author_id'],
                        body['service_event_id'],
                        body['state'],
                        body['service_event_json'],
                        body['links'])
  return handler


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventProcessorDriver('event_processor', daemon_able=True).main())
