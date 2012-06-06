import sys
import logging
import math
import datetime
import time

from tim_commons import total_seconds
from tim_commons.app_base import AppBase
from tim_commons.message_queue import (create_message_client,
                                       send_messages,
                                       close_message_client,
                                       create_queues)
from tim_commons import db
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
    db.configure_session(db_url)

  def _create_message_client(self):
    message_url = self.config['broker']['url']
    return create_message_client(message_url)

  def main(self):
    self._create_database()
    message_client = self._create_message_client()

    maximum_priority = int(self.config['scanner']['maximum_priority'])
    batch_size = int(self.config['scanner']['batch_size'])
    iteration_minimum_duration = float(self.config['scanner']['iteration_minimum_duration'])
    iteration_minimum_duration = datetime.timedelta(seconds=iteration_minimum_duration)

    _create_event_queues(message_client, self.config['queues'])

    iteration_counter_module = _compute_maximum_iteration(maximum_priority, self.option.iterations)

    current_iteration = 1
    start = None
    while not _done(current_iteration, self.option.iterations):
      if start is not None:
        duration = iteration_minimum_duration - (datetime.datetime.now() - start)
        if total_seconds(duration) > 0:
          logging.debug('Sleeping for %s seconds.', total_seconds(duration))
          time.sleep(total_seconds(duration))

      start = datetime.datetime.now()

      iteration_maximum_priority = _compute_iteration_maximum_priority(maximum_priority,
                                                                       current_iteration)

      current_id = ""

      processed_all_events = False
      while not processed_all_events:
        with db.Context():
          view_result = _query_events(current_id, iteration_maximum_priority, batch_size)

          if not view_result:
            processed_all_events = True
          else:
            logging.debug('Sending %s events to the queue', len(view_result))

          current_id = _send_update_message_from_event(message_client, view_result)
          _decrease_priority(view_result, maximum_priority)

      current_iteration = (current_iteration % iteration_counter_module) + 1

    close_message_client(message_client)


def _compute_maximum_iteration(max_priority, max_iterations):
  if max_iterations == 0:
    return 2 ** max_priority
  else:
    return _lcm(2 ** max_priority, max_iterations)


def _compute_iteration_maximum_priority(maximum_priority, current_iteration):
  return int(math.log(_gcd(2 ** maximum_priority, current_iteration), 2))


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


def _send_update_message_from_event(message_client, events):
  current_id = ""

  for event in events:
    message = create_event_update_message(event.service_id,
                                          event.service_user_id,
                                          event.service_event_id)
    send_messages(message_client, [message])
    current_id = event.hash_id

  return current_id


def _query_events(current_id, maximum_priority, set_size):
  query = db.Session().query(EventScannerPriority)
  query = query.filter(EventScannerPriority.hash_id > current_id)
  query = query.filter(EventScannerPriority.priority <= maximum_priority)

  return query[0:set_size]


def _decrease_priority(events, max_priority):
  for event in events:
    event.priority += 1
    if event.priority > max_priority:
      event.priority = max_priority


if __name__ == '__main__':
  sys.exit(ScannerApplication().main())
