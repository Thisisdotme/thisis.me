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
    events = [EventScannerPriority('event_id', 'user_id', 'facebook', 2),
              EventScannerPriority('event_id', 'user_id', 'instagram', 2)]

    driver._send_update_message_from_event(client, events)

  def test_query_event(self):
    db_session = mock.DummyDBSession()
    current_id = ""
    maximum_priority = 5
    set_size = 1000

    driver._query_events(db_session, current_id, maximum_priority, set_size)

  def test_iteration_modulo(self):
    modulo = driver._compute_maximum_iteration(3, 0)
    self.assertEqual(modulo, 8)

    modulo = driver._compute_maximum_iteration(8, 0)
    self.assertEqual(modulo, 256)

    modulo = driver._compute_maximum_iteration(8, 3)
    self.assertEqual(modulo, 768)

    modulo = driver._compute_maximum_iteration(3, 10)
    self.assertEqual(modulo, 40)

  def test_iteration_priority(self):
    max_priority = 6
    priority = driver._compute_iteration_maximum_priority(
        max_priority,
        driver._compute_maximum_iteration(max_priority, 0))
    self.assertEqual(priority, max_priority)

    for i in xrange(0, max_priority):
      priority = driver._compute_iteration_maximum_priority(max_priority, 2 ** i)
      self.assertEqual(priority, i)
      priority = driver._compute_iteration_maximum_priority(max_priority, 3 * (2 ** i))
      self.assertEqual(priority, i)
