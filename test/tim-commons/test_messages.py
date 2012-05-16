import unittest

from tim_commons.messages import create_event_update_message


class MessagesTestClass(unittest.TestCase):
  def test_create_event_update_message(self):
    message_type = 'facebook'
    service_user_id = 'service_user_id'
    service_event_id = 'service_event_id'
    message = create_event_update_message(message_type, service_user_id, service_event_id)

    self.assertEqual(message['header']['type'], message_type + '.update')
    self.assertEqual(message['message']['service_author_id'], service_user_id)
    self.assertEqual(message['message']['service_event_id'], service_event_id)
