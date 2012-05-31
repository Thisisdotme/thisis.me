#!/usr/bin/env python
import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons.messages import (create_notification_message)
from tim_commons.message_queue import (create_message_client, create_queues, send_messages)
from tim_commons import db

from mi_schema.models import (Service, AuthorServiceMap)


class NotificationDriver(AppBase):

  def display_usage(self):
    return 'Usage: ' + self.name + '.py --service=service_name [--service=service_name ...] \nExample: ' + self.name + '.py --service=facebook'

  def init_args(self):
    self.option_parser.add_option('--service',
                                  dest='services',
                                  action='append',
                                  default=[],
                                  help='Services to process')

  def parse_args(self, ignore):
    (self.options, ignore) = self.option_parser.parse_args()

    if ignore:
      self.option_parser.print_help()
      sys.exit()

  def main(self):

    logging.info("Beginning: " + self.name)

    # read the db url from the config
    db_url = self.config['db']['sqlalchemy.url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # if services option is empty default to all available configured services
    if not self.options.services:
      service_names = []
      # generate the list of service name's from queue list
      for key in self.config['queues'].iterkeys():
        service_names.append(key)
    else:
      service_names = self.options.services

    # get the broker and queue config
    broker_url = self.config['broker']['url']

    # get message broker client and store in instance
    self.client = create_message_client(broker_url)

    # for each specified service
    for service_name in service_names:

      # create the queue for this service
      create_queues(self.client, [self.config['queues'][service_name]['notification']])

      # post a notification for each author subscribed to this service
      for asm in db.Session().query(AuthorServiceMap). \
                              join(Service, AuthorServiceMap.service_id == Service.id). \
                              filter(Service.service_name == service_name).all():
        send_messages(self.client, [create_notification_message(service_name, asm.service_author_id)])

    logging.info("Finished: " + self.name)

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(NotificationDriver().main())
