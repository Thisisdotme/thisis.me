import threading
import puka
import logging

from tim_commons import json_serializer

# Thread local client
threadlocal = threading.local()


def get_current_message_client(url):
  '''Creates or gets a thread local message queue client for the given url.

  Arguments:
  url -- the URL of the message queue server. E.g. amqp://localhost
  '''
  map = getattr(threadlocal, 'puka_client', None)
  if map is None:
    map = {}
    setattr(threadlocal, 'puka_client', map)

  client = map.get(url, None)
  if client is None:
    client = create_message_client(url)
    map[url] = client

  return client


def create_message_client(url):
  '''Creates a message queue client for the given url.

  Arguments:
  url -- the URL of the message queue server. E.g. amqp://localhost

  '''
  client = puka.Client(url)
  promise = client.connect()
  client.wait(promise)

  return client


def close_message_client(client):
  promise = client.close()
  client.wait(promise)


def create_queues(client, queues, durable=True):
  ''' Creates a set of queues

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queues -- list of queues to create
  '''
  promises = []
  for queue in queues:
    promise = client.queue_declare(queue=queue, durable=durable)
    promises.append(promise)

  for promise in promises:
    client.wait(promise)


def send_messages(client, queue, messages):
  ''' Sends a list of messages to the specified queue.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queue -- the queue to push all the messages
  messages -- list of message to push to the queue
  '''
  # Send all the messages
#  promises = []
  for message in messages:
    body = json_serializer.dump_string(message)
    promise = client.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=body)
    client.wait(promise)

  # Wait until all the message were sent
#  for promise in promises:


def join(client, queue, handler):
  '''
  Receives messages from the message queue and forwards them to the
  handler. The handler needs to implement a handler method that accepts one
  parameter. The parameter is the map representing the JSON object.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queue -- the queue to push all the messages
  handler -- closer to call when a message is received from the message queue
  '''
  promise = client.basic_consume(queue=queue, prefetch_count=1)
  while True:
    result = client.wait(promise)

    try:
      message = json_serializer.load_string(result['body'])
      if message['header']['type'] == queue:
        handler(message)
      else:
        logging.error('Message does not contain a header.type: %s' % result)
    except Exception:
      logging.exception('Error in handler for event: %s' % result)

    client.basic_ack(result)

  promise = client.close()
  client.wait(promise)
