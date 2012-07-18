import sys
import logging

from event_collectors import event_collector
from tim_commons import message_queue, db, app_base
import data_access.service


class EventCollectorDriver(app_base.AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--service',
                              dest='services',
                              action='append',
                              default=[],
                              help='Services to process')

  def create_event_callback(self):
    def handler(message):
      message_queue.send_messages(self.client, [message])

    return handler

  def create_collector_handler(self, collector):
    def handler(message):
      with db.Context():
        collector.fetch(message['message']['service_author_id'], self.create_event_callback())

    return handler

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = db.create_url_from_config(config['db'])
    # get the broker and queue config
    broker_url = message_queue.create_url_from_config(config['broker'])

    # initialize the db engine & session
    db.configure_session(db_url)
    data_access.service.initialize()

    services = services_configuration(options.services, config)

    # Get a list of all the handlers
    handlers = []
    for service in services:
      # Create handlers
      collector = event_collector.from_service_name(service['name'], service['oauth'])
      handler = {'queue': service['queue'],
                 'handler': self.create_collector_handler(collector)}
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
           'queue': config['queues'][service]['notification']['name']} for service in services]


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventCollectorDriver('event_collector', daemon_able=True).main())
