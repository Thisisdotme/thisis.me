import unittest

from tim_commons import messages


class MessagesTestClass(unittest.TestCase):
  def test_create_event_update_message(self):
    service_id = 'facebook'
    service_user_id = 'service_user_id'
    service_event_id = 'service_event_id'
    message = messages.create_event_update_message(service_id, service_user_id, service_event_id)

    self.assertEqual(message['header']['type'], service_id + '.update')
    self.assertEqual(message['message']['service_author_id'], service_user_id)
    self.assertEqual(message['message']['service_event_id'], service_event_id)

  def test_create_notification_message(self):
    services = ['facebook', 'twitter', 'instagram', 'foursquare', 'linkedin']
    service_user_id = 'service_user_id'

    for service in services:
      message = messages.create_notification_message(service, service_user_id)

      self.assertEqual(message['header']['type'], service + '.notification')
      self.assertEqual(message['message']['service_author_id'], service_user_id)

  def test_create_event_message(self):
    services = ['facebook', 'twitter', 'instagram', 'foursquare', 'linkedin']
    tim_author_id = 1234
    service_user_id = 'service_user_id'
    json_dict = {'key': 'value'}

    for service in services:
      message = messages.create_event_message(service, tim_author_id, service_user_id, json_dict)

      self.assertEqual(message['header']['type'], service + '.event')
      self.assertEqual(message['message']['tim_author_id'], tim_author_id)
      self.assertEqual(message['message']['service_author_id'], service_user_id)
      self.assertEqual(message['message']['service_event_json'], json_dict)
