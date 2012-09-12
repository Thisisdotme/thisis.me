# To delete all the current queues and re-create them again do:
# sudo rabbitmqctl list_queues | sed -e '2,$!d' -e '$d' | cut -f 1 | \
#      python tools/recreate_message_queues.py --delete_from_stdin
import sys

import tim_commons.app_base
import tim_commons.message_queue


class RecreateMessageQueues(tim_commons.app_base.AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--delete_from_stdin',
                             dest='delete_from_stdin',
                             action='store_true',
                             default=False,
                             help='Delete all the queues listed in stdin')
    option_parser.add_option('--force',
                             dest='force',
                             action='store_true',
                             default=False,
                             help='Force the deleting of non-empty queues')

  def app_main(self, config, options, args):
    client = tim_commons.message_queue.create_message_client(
        tim_commons.message_queue.create_url_from_config(config['amqp']['broker']))

    if options.delete_from_stdin:
      tim_commons.message_queue.delete_queues(
          client,
          (line.strip() for line in sys.stdin.readlines()))

    # delete and create all the queues that we know about
    for queue in config['amqp']['queues'].itervalues():
      if not tim_commons.to_bool(queue['exclusive']):
        tim_commons.message_queue.delete_queues(client, [queue['queue']], force=options.force)

    tim_commons.message_queue.create_queues_from_config(client, config['amqp'])


if __name__ == '__main__':
  sys.exit(RecreateMessageQueues('recreate_messages_queue').main())
