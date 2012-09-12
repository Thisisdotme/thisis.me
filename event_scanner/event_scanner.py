import logging
import time

from tim_commons import total_seconds, messages, db, message_queue
from mi_schema import models


def scan_events(
    message_url,
    message_exchange,
    priority,
    highest_priority_duration,
    maximum_priority):
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
      current_id = _send_update_message_from_event(message_client, message_exchange, view_result)
      _decrease_priority(view_result, maximum_priority)


def _query_event_count(priority):
  query = db.Session().query(models.EventScannerPriority)
  query = query.filter_by(priority=priority)
  return query.count()


def _send_update_message_from_event(message_client, exchange, event):
  current_id = ""
  if event is not None:
    message = messages.create_event_update_message(
      event.service_name,
      event.service_user_id,
      event.service_event_id)
    message_queue.send_messages(message_client, exchange, [message])
    current_id = event.hash_id

  return current_id


def _query_event(current_id, priority):
  query = db.Session().query(models.EventScannerPriority)
  query = query.filter(models.EventScannerPriority.hash_id > current_id)
  query = query.filter(models.EventScannerPriority.priority == priority)

  return query.first()


def _decrease_priority(event, max_priority):
  if event is not None:
    event.priority += 1
    if event.priority > max_priority:
      event.priority = max_priority
