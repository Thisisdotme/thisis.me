import unittest

from mi_schema.models import EventScannerPriority


class ModelTestCase(unittest.TestCase):
  def test_event_scanner_priority(self):
    event_id = 'event_id'
    user_id = 'user_id'
    service_name = 'service_name'
    event_scanning = EventScannerPriority(event_id, user_id, service_name, 0)
    self.assertEqual(event_scanning.priority, 0)
    self.assertEqual(event_scanning.service_event_id, event_id)
    self.assertEqual(event_scanning.service_user_id, user_id)
    self.assertEqual(event_scanning.service_name, service_name)
    self.assertEqual(len(event_scanning.hash_id), 44)
