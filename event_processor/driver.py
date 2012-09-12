import sys
import datetime
import logging

from tim_commons import message_queue, db, app_base
from data_access import service, post_type
import event_processor


class EventProcessorDriver(app_base.AppBase):
  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = db.create_url_from_config(config['db'])
    # get the broker and queue config
    broker_url = message_queue.create_url_from_config(config['amqp']['broker'])
    # get the maximum priority
    max_priority = int(config['scanner']['maximum_priority'])
    min_duration = float(config['scanner']['iteration_minimum_duration'])
    min_duration = datetime.timedelta(seconds=min_duration)

    # initialize the db engine & session
    db.configure_session(db_url)
    service.initialize()
    post_type.initialize()

    # Create event processor
    self.processor = event_processor.EventProcessor(
        max_priority,
        min_duration,
        config['oauth'])

    logging.info('Queue broker URL: %s', broker_url)

    # get message broker client and store in instance -- used for both receiving and sending
    self.client = message_queue.create_message_client(broker_url)
    message_queue.create_queues_from_config(self.client, config['amqp'])

    message_queue.join(
        self.client,
        config['amqp']['queues']['processor']['queue'],
        self.handler)

    logging.info("Finished...")

  def handler(self, message):
    body = message['message']
    with db.Context():
      self.processor.process(
          body['tim_author_id'],
          body['service_name'],
          body['service_author_id'],
          body['service_event_id'],
          body['state'],
          body['service_event_json'],
          body['links'])


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventProcessorDriver('event_processor', daemon_able=True).main())
