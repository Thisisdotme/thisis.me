import sys
import logging

from tim_commons import message_queue, db, app_base
from event_updaters import event_updater
import data_access.service
import data_access.post_type


class EventUpdaterDriver(app_base.AppBase):
  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = db.create_url_from_config(config['db'])
    # get the broker and queue config
    broker_url = message_queue.create_url_from_config(config['amqp']['broker'])
    # get exchange information
    self.amqp_exchange = config['amqp']['exchange']['name']

    # initialize the db engine & session
    db.configure_session(db_url)
    data_access.service.initialize()
    data_access.post_type.initialize()

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = message_queue.create_message_client(broker_url)

    self.handlers = {}
    for service in _services_configuration(config):
      self.handlers[service['name']] = event_updater.from_service_name(
          service['name'],
          service['oauth'])

    logging.info('Queue broker URL: %s', broker_url)
    logging.debug('Active handlers: %s', self.handlers)

    message_queue.create_queues_from_config(self.client, config['amqp'])
    message_queue.join(
        self.client,
        config['amqp']['queues']['updater']['queue'],
        self.handler)

    logging.info("Finished...")

  def handler(self, message):
    body = message['message']
    with db.Context():
      self.handlers[body['service_name']].fetch(
        body['service_name'],
        body['service_author_id'],
        body['service_event_id'],
        self.event_callback)

  def event_callback(self, message):
    message_queue.send_messages(self.client, self.amqp_exchange, [message])


def _services_configuration(config):
  return [{'name': service, 'oauth': config['oauth'][service]}
      for service in config['oauth'].iterkeys()]


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventUpdaterDriver('event_updater', daemon_able=True).main())
