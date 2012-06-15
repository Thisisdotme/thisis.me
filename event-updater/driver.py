import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons import message_queue
from tim_commons import db
from event_updaters import event_updater


class EventUpdaterDriver(AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--service',
                             dest='services',
                             action='append',
                             default=[],
                             help='Service to process')

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = config['db']['sqlalchemy.url']
    # get the broker and queue config
    broker_url = config['broker']['url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # get message broker client and store in instance -- used for both receiving and sending
    client = message_queue.create_message_client(broker_url)

    services = services_configuration(options.services, config)

    handlers = []
    for service in services:
      # Create handlers
      updater = event_updater.from_service_name(service['name'], service['oauth'])
      handler = {'queue': service['queue'],
                 'handler': create_updater_handler(updater, client)}
      handlers.append(handler)

    logging.info('Queue broker URL: %s', broker_url)
    logging.debug('Active handlers: %s', handlers)

    message_queue.create_queues_from_config(client, config['queues'])

    message_queue.join(client, handlers)

    logging.info("Finished...")


def services_configuration(services, config):
  # If services is empty then get all the services in the configuration
  if not services:
    for service in config['queues'].iterkeys():
      services.append(service)

  return [{'name': service,
           'oauth': config['oauth'][service],
           'queue': config['queues'][service]['update']['name']} for service in services]


def create_event_callback(client):
  def handler(message):
    message_queue.send_messages(client, [message])

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
  sys.exit(EventUpdaterDriver('event_updater', daemon_able=True).main())
