#!/usr/bin/env python

import sys
import logging

from sqlalchemy import and_

from tim_commons.app_base import AppBase
from tim_commons.messages import (create_event_update_message)
from tim_commons import message_queue
from tim_commons import db

from mi_schema.models import (Service, AuthorServiceMap, Author, ServiceEvent)


class EventUpdateTrigger(AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--service',
                             dest='services',
                             action='append',
                             default=[],
                             help='Services to process')

    option_parser.add_option('--author',
                             dest='authors',
                             action='append',
                             default=[],
                             help='Authors to process')

  def app_main(self, config, options, args):
    logging.info("Beginning...")

    db.configure_session(url=db.create_url_from_config(config['db']))

    # if services option is empty default to all available configured services
    if not options.services:
      service_names = []
      # generate the list of service name's from queue list
      for key in config['queues'].iterkeys():
        service_names.append(key)
    else:
      service_names = options.services

    # if authors option is empty default to all authors
    if not options.authors:
      author_names = [author_name for author_name in db.Session().query(Author.author_name).all()]
    else:
      author_names = options.authors

    # get the broker and queue config
    broker_url = config['broker']['url']

    # get message broker client and store in instance
    client = message_queue.create_message_client(broker_url)

    # for each specified service
    for service_name in service_names:

      # create the queue for this service
      message_queue.create_queues_from_config(client, config['queues'])

      # for each specified author
      for author_name in author_names:

        # post a update message for service & author
        for asm, event in db.Session().query(AuthorServiceMap, ServiceEvent). \
                                       join(ServiceEvent, and_(AuthorServiceMap.author_id == ServiceEvent.author_id,
                                                               AuthorServiceMap.service_id == ServiceEvent.service_id)). \
                                       join(Service, AuthorServiceMap.service_id == Service.id). \
                                       join(Author, AuthorServiceMap.author_id == Author.id). \
                                       filter(and_(Service.service_name == service_name,
                                                   Author.author_name == author_name)).all():

          if event.type_id == 2:
            continue

          message_queue.send_messages(client,
                                      [create_event_update_message(service_name,
                                                                   asm.service_author_id,
                                                                   event.event_id)])

    logging.info("Finished...")

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventUpdateTrigger('event_update_trigger').main())
