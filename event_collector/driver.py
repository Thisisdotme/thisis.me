import sys
import logging

from event_collectors import event_collector
import tim_commons.message_queue
import tim_commons.db
import tim_commons.app_base
import data_access.service


class EventCollectorDriver(tim_commons.app_base.AppBase):
  def event_callback(self, message):
    tim_commons.message_queue.send_messages(self.client, self.amqp_exchange, [message])

  def handler(self, message):
    with tim_commons.db.Context():
      self.handlers[message['message']['service_name']].fetch(
          message['message']['service_author_id'],
          self.event_callback)

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = tim_commons.db.create_url_from_config(config['db'])
    # get the broker and queue config
    broker_url = tim_commons.message_queue.create_url_from_config(config['amqp']['broker'])
    # get exchange information
    self.amqp_exchange = config['amqp']['exchange']['name']

    # initialize the db engine & session
    tim_commons.db.configure_session(db_url)
    data_access.service.initialize()

    # Get a list of all the handlers
    self.handlers = {}
    for service in _services_configuration(config):
      self.handlers[service['name']] = event_collector.from_service_name(
          service['name'], service['oauth'])

    logging.info('Queue broker URL: %s', broker_url)
    logging.debug('Active handlers: %s', self.handlers)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = tim_commons.message_queue.create_message_client(broker_url)
    tim_commons.message_queue.create_queues_from_config(self.client, config['amqp'])

    tim_commons.message_queue.join(
        self.client,
        config['amqp']['queues']['collector']['queue'],
        self.handler)

    logging.info("Finished...")


def _services_configuration(config):
  return [{'name': service, 'oauth': config['oauth'][service]}
      for service in config['oauth'].iterkeys()]


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventCollectorDriver('event_collector', daemon_able=True).main())
