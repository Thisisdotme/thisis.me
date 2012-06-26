import unittest

from event_processors import event_processor
from tim_commons import db


class EventProcessorTestCase(unittest.TestCase):
  def setUp(self):
    db.configure_mock_session()

  def test_query_correlation_event(self):
    me_service_id = 2
    correlation_id = 'sha256_hash_id'
    author_id = 1

    event_processor.query_correlation_event(me_service_id, correlation_id, author_id)
