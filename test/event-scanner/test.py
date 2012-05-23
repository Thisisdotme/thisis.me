import unittest

from event_scanner import driver
from tim_commons import mock
from mi_schema.models import EventScannerPriority


class ScannerTestCase(unittest.TestCase):
  def test_create_event_queue(self):
    client = mock.DummyMessageClient()
    queues = {'facebook': {'update': 'queue_name'},
              'instagram': {'update': 'queue'}}

    driver._create_event_queues(client, queues)

  def test_send_update_messages(self):
    client = mock.DummyMessageClient()
    queues = {'facebook': {'update': 'queue_name'},
              'instagram': {'update': 'another_queue_name'}}
    events = [EventScannerPriority('event_id', 'user_id', 'facebook', 2),
              EventScannerPriority('event_id', 'user_id', 'instagram', 2)]

    driver._send_update_message_from_event(client, queues, events)

  def test_query_event(self):
    db_session = mock.DummyDBSession()
    current_id = ""
    maximum_priority = 5
    set_size = 1000

    driver._query_events(db_session, current_id, maximum_priority, set_size)
