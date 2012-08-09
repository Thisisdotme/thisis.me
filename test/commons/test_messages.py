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
    service_event_id = '987654321'
    service_link_name = 'instagram'
    service_link_event_id = '543216789'
    json_dict = {'key': 'value'}

    for service in services:
      message = messages.create_event_message(
          service,
          tim_author_id,
          messages.CURRENT_STATE,
          service_user_id,
          service_event_id,
          json_dict,
          [messages.create_event_link(service_link_name, service_link_event_id)])

      self.assertEqual(message['header']['type'], service + '.event')
      self.assertEqual(message['message']['tim_author_id'], tim_author_id)
      self.assertEqual(message['message']['state'], messages.CURRENT_STATE)
      self.assertEqual(message['message']['service_author_id'], service_user_id)
      self.assertEqual(message['message']['service_event_id'], service_event_id)
      self.assertEqual(message['message']['service_event_json'], json_dict)
      self.assertEqual(message['message']['links'][0]['service_id'], service_link_name)
      self.assertEqual(message['message']['links'][0]['service_event_id'], service_link_event_id)
