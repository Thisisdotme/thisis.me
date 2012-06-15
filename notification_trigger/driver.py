import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons.messages import (create_notification_message)
from tim_commons import message_queue
from tim_commons import db

from mi_schema.models import (Service, AuthorServiceMap)


class NotificationDriver(AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--service',
                             dest='services',
                             action='append',
                             default=[],
                             help='Services to process')

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    # read the db url from the config
    db_url = config['db']['sqlalchemy.url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # if services option is empty default to all available configured services
    if not options.services:
      service_names = []
      # generate the list of service name's from queue list
      for key in config['queues'].iterkeys():
        service_names.append(key)
    else:
      service_names = options.services

    # get the broker and queue config
    broker_url = config['broker']['url']

    # get message broker client and store in instance
    client = message_queue.create_message_client(broker_url)

    # for each specified service
    for service_name in service_names:

      # create the queue for this service
      message_queue.create_queues_from_config(client, config['queues'])

      # post a notification for each author subscribed to this service
      for asm in db.Session().query(AuthorServiceMap). \
                              join(Service, AuthorServiceMap.service_id == Service.id). \
                              filter(Service.service_name == service_name).all():
        message_queue.send_messages(client,
                                    [create_notification_message(service_name,
                                                                 asm.service_author_id)])

    logging.info("Finished...")

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(NotificationDriver('notification_trigger').main())
