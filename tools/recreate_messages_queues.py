# To delete all the current queues and re-create them again do:
# sudo rabbitmqctl list_queues | sed -e '2,$!d' -e '$d' | cut -f 1 | \
#      python tools/recreate_message_queus.py --delete_from_stdin
import sys

from tim_commons import app_base, message_queue


class RecreateMessageQueues(app_base.AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--delete_from_stdin',
                             dest='delete_from_stdin',
                             action='store_true',
                             default=False,
                             help='Delete all the queues listed in stdin')

  def app_main(self, config, options, args):
    client = message_queue.create_message_client(
        message_queue.create_url_from_config(config['broker']))

    if options.delete_from_stdin:
      message_queue.delete_queues(client, (line.strip() for line in sys.stdin.readlines()))

    # delete and create all the queues that we know about
    for service_queue_config in config['queues'].itervalues():
      for queue_config in service_queue_config.itervalues():
        queue = queue_config['name']
        message_queue.delete_queues(client, [queue])
        message_queue.create_queues(client, [queue], bool(queue_config['durable']))


if __name__ == '__main__':
  sys.exit(RecreateMessageQueues('recreate_messages_queue').main())
