import logging
import sys
import os
import json

from tim_commons.app_base import AppBase
from tim_commons.message_queue import create_message_client, send_messages

_TIM_DATA = 'TIM_DATA'


class NotificationLoad(AppBase):

  def display_usage(self):
    return 'usage: %prog [options] queues...'

  def init_args(self):
    self.option_parser.add_option('--url',
                            dest='url',
                            default='amqp://localhost',
                            help='URL for the message queue')
    self.option_parser.add_option('--messagefile',
                            dest='message_file',
                            default='%(TIM_DATA)s/messages.json',
                            help='File containing all the message events')

  def parse_args(self, ignore):
    (self.option, self.queues) = self.option_parser.parse_args()

    if len(self.queues) < 1:
      self.option_parser.print_help()
      sys.exit()

  def main(self):
    data_directory = os.environ.get(_TIM_DATA, None)
    if data_directory is None:
      logging.error('Environment variable %s not defined', _TIM_DATA)
      sys.exit()

    file = self.option.message_file % {_TIM_DATA: os.environ[_TIM_DATA]}

    if not os.path.exists(file):
      logging.warning('File "%s" does not exist' % file)
      sys.exit()

    # read the message file
    try:
      messages = json.load(open(file, 'r'))
    except Exception:
      logging.error('Failed to read json file: %s', file)
      raise

    # create amqp connection
    client = create_message_client(self.option.url)

    # itereate and send all the interesting messages
    for message in messages:
      queue = message['header']['type'].encode('ascii')
      if queue in self.queues:
        send_messages(client, queue, [message])


if __name__ == '__main__':
  sys.exit(NotificationLoad().main())
