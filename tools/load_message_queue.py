import logging
import sys
import os

from tim_commons.app_base import AppBase
from tim_commons.message_queue import create_message_client, send_messages, create_queues
from tim_commons import json_serializer


class NotificationLoad(AppBase):
  def display_usage(self):
    return 'usage: %prog [options] queues...'

  def init_args(self, option_parser):
    option_parser.add_option('--url',
                             dest='url',
                             default='amqp://localhost',
                             help='URL for the message queue')
    option_parser.add_option('--messagefile',
                             dest='message_file',
                             default='{tim_data}/messages.json',
                             help='File containing all the message events')
    option_parser.add_option('--non-durable',
                             dest='durable',
                             action='store_false',
                             default=True,
                             help='Flag specifying message queue durability')

  def parse_args(self, queues):
    if len(queues) < 1:
      self.error('Most specify a queue')

  def app_main(self, config, options, queues):
    TIM_DATA = 'TIM_DATA'
    data_directory = os.environ.get(TIM_DATA, None)
    if data_directory is None:
      logging.error('Environment variable %s not defined', TIM_DATA)
      sys.exit()

    file = options.message_file.format(tim_data=data_directory)

    if not os.path.exists(file):
      logging.warning('File "%s" does not exist', file)
      sys.exit()

    # read the message file
    try:
      messages = json_serializer.load(open(file, 'r'))
    except Exception:
      logging.error('Failed to read json file: %s', file)
      raise

    # create amqp connection
    client = create_message_client(options.url)

    # create all of the required queues
    create_queues(client, queues, durable=options.durable)

    # itereate and send all the interesting messages
    for message in messages:
      queue = message['header']['type']
      if queue in queues:
        send_messages(client, [message])
        sys.stdout.write('.')
    sys.stdout.write('\n')


if __name__ == '__main__':
  sys.exit(NotificationLoad('load_message_queue').main())
