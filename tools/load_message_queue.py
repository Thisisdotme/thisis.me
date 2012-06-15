import logging
import sys
import os

from tim_commons import json_serializer, app_base, message_queue


class NotificationLoad(app_base.AppBase):
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
    client = message_queue.create_message_client(options.url)

    # create all of the required queues
    message_queue.create_queues_from_config(client, config['queues'])

    # itereate and send all the interesting messages
    for message in messages:
      queue = message['header']['type']
      if queue in queues:
        message_queue.send_messages(client, [message])
        sys.stdout.write('.')
    sys.stdout.write('\n')


if __name__ == '__main__':
  sys.exit(NotificationLoad('load_message_queue').main())
