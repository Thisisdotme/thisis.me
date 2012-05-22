import sys
import logging
import contextlib
import math
import datetime
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tim_commons import total_seconds
from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client,
                                       send_messages,
                                       close_message_client,
                                       create_queues)
from tim_commons.messages import create_event_update_message
from mi_schema.models import EventScannerPriority


class ScannerApplication(AppBase):
  def display_usage(self):
    return '%prog [options]'

  def init_args(self):
    self.option_parser.add_option('--iterations',
                            dest='iterations',
                            type="int",
                            default=0,
                            help='Number of iteration before existing. 0 is for ifinite')

  def parse_args(self, ignore):
    (self.option, ignore) = self.option_parser.parse_args()

    if ignore or self.option.iterations < 0:
      self.option_parser.print_help()
      sys.exit()

  def _create_database(self):
    db_url = self.config['db']['sqlalchemy.url']
    engine = create_engine(db_url, encoding='utf-8', echo=False)
    return sessionmaker(bind=engine, autocommit=True)

  def _create_message_client(self):
    message_url = self.config['broker']['url']
    return create_message_client(message_url)

  def main(self):
    DBSession = self._create_database()

    message_client = self._create_message_client()

    maximum_priority = int(self.config['scanner']['maximum_priority'])
    batch_size = int(self.config['scanner']['batch_size'])
    iteration_minimum_duration = float(self.config['scanner']['iteration_minimum_duration'])
    iteration_minimum_duration = datetime.timedelta(seconds=iteration_minimum_duration)

    queues = self.config['queues']
    _create_event_queues(message_client, queues)

    iteration_counter_module = maximum_priority
    if self.option.iterations != 0:
      iteration_counter_module = _lcm(maximum_priority, self.option.iterations)

    current_iteration = 1
    start = None
    while not _done(current_iteration, self.option.iterations):
      if start is not None:
        duration = iteration_minimum_duration - (datetime.datetime.now() - start)
        if total_seconds(duration) > 0:
          logging.debug('Sleeping for %s seconds.', total_seconds(duration))
          time.sleep(total_seconds(duration))

      start = datetime.datetime.now()

      iteration_maximum_priority = int(math.log(_gcd(maximum_priority, current_iteration), 2))

      current_id = ""

      processed_all_events = False
      while not processed_all_events:
        with contextlib.closing(DBSession()) as session:
          view_result = _query_events(session, current_id, iteration_maximum_priority, batch_size)

        if not view_result:
          processed_all_events = True
        else:
          logging.debug('Sending %s events to the queue', len(view_result))

        current_id = _send_update_message_from_event(message_client, queues, view_result)

      current_iteration = (current_iteration % iteration_counter_module) + 1

    close_message_client(message_client)


def  _lcm(a, b):
  gcd = _gcd(a, b)
  return (a / gcd) * b


def _gcd(a, b):
  while b != 0:
    (a, b) = (b, a % b)

  return a


def _done(current_iteration, iterations):
  if iterations < 1:
    return False
  else:
    return current_iteration > iterations


def _create_event_queues(message_client, queues_config):
  for service_queues in queues_config.itervalues():
    queue = service_queues.get('update', None)
    if queue is not None:
      create_queues(message_client, [queue], durable=False)


def _send_update_message_from_event(message_client, queues, events):
  current_id = ""

  for event in events:
    queue = queues[event.service_id]['update']
    message = create_event_update_message(event.service_id,
                                          event.service_user_id,
                                          event.service_event_id)
    send_messages(message_client, queue, [message])
    current_id = event.hash_id

  return current_id


def _query_events(db_session, current_id, maximum_priority, set_size):
  query = db_session.query(EventScannerPriority)
  query = query.filter(EventScannerPriority.hash_id > current_id)
  query = query.filter(EventScannerPriority.priority <= maximum_priority)

  return query[0:set_size]


if __name__ == '__main__':
  sys.exit(ScannerApplication().main())
