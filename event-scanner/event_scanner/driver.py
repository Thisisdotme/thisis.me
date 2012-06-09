import sys
import logging
import datetime
import time
import threading

from tim_commons import total_seconds
from tim_commons.app_base import AppBase
from tim_commons import message_queue
from tim_commons import db
from tim_commons.messages import create_event_update_message
from mi_schema.models import EventScannerPriority


class ScannerApplication(AppBase):
  def display_usage(self):
    return '%prog [options]'

  def init_args(self):
    pass

  def parse_args(self, ignore):
    (ignore, ignore) = self.option_parser.parse_args()

    if ignore:
      self.option_parser.print_help()
      sys.exit()

  def main(self):
    db_url = self.config['db']['sqlalchemy.url']
    message_url = self.config['broker']['url']

    maximum_priority = int(self.config['scanner']['maximum_priority'])
    iteration_minimum_duration = float(self.config['scanner']['iteration_minimum_duration'])
    iteration_minimum_duration = datetime.timedelta(seconds=iteration_minimum_duration)

    db.configure_session(db_url)

    message_client = message_queue.create_message_client(message_url)
    _create_event_queues(message_client, self.config['queues'])
    message_queue.close_message_client(message_client)

    for priority in range(0, maximum_priority + 1):
      scanner = threading.Thread(target=_scan_events,
                                 args=(message_url,
                                       priority,
                                       iteration_minimum_duration,
                                       maximum_priority))
      scanner.start()


def _scan_events(message_url, priority, highest_priority_duration, maximum_priority):
  priority_duration = (2 ** priority) * highest_priority_duration
  message_client = message_queue.create_message_client(message_url)
  current_id = ""

  while True:
    with db.Context():
      event_count = _query_event_count(priority)
      event_interval = highest_priority_duration
      if event_count != 0:
        event_interval = priority_duration / event_count
      logging.info("Sleepging for %s seconds for priorrity %s",
                   total_seconds(event_interval),
                   priority)

      time.sleep(total_seconds(event_interval))

      view_result = _query_event(current_id, priority)
      current_id = _send_update_message_from_event(message_client, view_result)
      _decrease_priority(view_result, maximum_priority)


def _query_event_count(priority):
  query = db.Session().query(EventScannerPriority)
  query = query.filter_by(priority=priority)
  return query.count()


def _create_event_queues(message_client, queues_config):
  for service_queues in queues_config.itervalues():
    queue = service_queues.get('update', None)
    if queue is not None:
      message_queue.create_queues(message_client, [queue], durable=False)


def _send_update_message_from_event(message_client, event):
  current_id = ""
  if event is not None:
    message = create_event_update_message(event.service_id,
                                          event.service_user_id,
                                          event.service_event_id)
    message_queue.send_messages(message_client, [message])
    current_id = event.hash_id

  return current_id


def _query_event(current_id, priority):
  query = db.Session().query(EventScannerPriority)
  query = query.filter(EventScannerPriority.hash_id > current_id)
  query = query.filter(EventScannerPriority.priority == priority)

  return query.first()


def _decrease_priority(event, max_priority):
  if event is not None:
    event.priority += 1
    if event.priority > max_priority:
      event.priority = max_priority


if __name__ == '__main__':
  sys.exit(ScannerApplication('event_scanner').main())
