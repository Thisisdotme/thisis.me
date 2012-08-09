import unittest

from tim_commons import message_queue
from tim_commons import mock
from tim_commons import messages


class MessageQueueTestQueue(unittest.TestCase):
  def test_get_current_message_client(self):
    first_client = message_queue.get_current_message_client('amqp://localhost')
    second_client = message_queue.get_current_message_client('amqp://localhost')

    self.assertTrue(first_client is second_client)

  def test_close_message_client(self):
    mock_client = mock.DummyMessageClient()
    message_queue.close_message_client(mock_client)

  def test_create_queues(self):
    mock_client = mock.DummyMessageClient()
    message_queue.create_queues(mock_client, ['one', 'two'])
    message_queue.create_queues(mock_client, ['one', 'two'], durable=False)

  def test_send_messages(self):
    mock_client = mock.DummyMessageClient()
    message_queue.send_messages(mock_client,
                                [messages.create_notification_message('service', 'id')])

  def test_create_queues_from_config(self):
    mock_client = mock.DummyMessageClient()
    config = {'facebook': {'notification': {'name': 'facebook.notification',
                                            'durable': 'True'},
                           'event': {'name': 'facebook.event',
                                     'durable': 'True'}},
              'foursquare': {'notification': {'name': 'foursquare.notification',
                                              'durable': 'True'}}}
    message_queue.create_queues_from_config(mock_client, config)
