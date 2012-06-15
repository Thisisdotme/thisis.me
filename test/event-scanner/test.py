import unittest

from tim_commons import mock, db
from mi_schema import models
from event_scanner import (_send_update_message_from_event,
                           _query_event,
                           _query_event_count,
                           _decrease_priority)


class ScannerTestCase(unittest.TestCase):
  def test_send_update_messages(self):
    client = mock.DummyMessageClient()
    event = models.EventScannerPriority('event_id', 'user_id', 'facebook', 2)

    _send_update_message_from_event(client, event)

  def test_query_event_count(self):
    db.configure_mock_session()
    _query_event_count(10)

  def test_query_event(self):
    db.configure_mock_session()
    current_id = ""
    maximum_priority = 5

    _query_event(current_id, maximum_priority)

  def test_decrease_priority(self):
    db.configure_mock_session()
    event = models.EventScannerPriority('event_id', 'user_id', 'facebook', 2)
    _decrease_priority(event, 3)
    self.assertEqual(event.priority, 3)
    _decrease_priority(event, 3)
    self.assertEqual(event.priority, 3)  # shouldn't go beyond the max priority
