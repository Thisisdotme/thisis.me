import threading
import puka
import logging
import os

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


def create_queues_from_config(client, config):
  for service_queue_config in config.itervalues():
    for queue_config in service_queue_config.itervalues():
      create_queues(client, [queue_config['name']], bool(queue_config['durable']))


def delete_queues(client, queues):
  promises = []
  for queue in queues:
    promise = client.queue_delete(queue=queue, if_empty=True)
    promises.append(promise)

  for promise in promises:
    try:
      client.wait(promise)
    except puka.NotFound:
      # Lets ignore not found errors
      pass
    except puka.PreconditionFailed, e:
      logging.info('Unable to delete queue: %s', e)


def send_messages(client, messages):
  ''' Sends a list of messages to the appropriate queue.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  messages -- list of message to push
  '''
# Send all the messages
  for message in messages:
    queue = message['header']['type'].encode('ascii')
    body = json_serializer.dump_string(message)
    promise = client.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=body)
    client.wait(promise)


def join(client, queues):
  '''
  Receives messages from the message queues and forwards them to the
  handler for the corresponding queue. The handler needs to accepts
  one parameter. The parameter is the map representing the JSON object.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queues -- a list of {'queue': <queue name>, 'handler': <handler>}i
  '''
# Populate the handlers
  handlers = {}
  for queue in queues:
    queue_name = queue['queue']
    if queue_name in handlers:
      raise Exception('Queue {0} appears twice in the set of queues'.format(queue_name))

    handlers[queue_name] = queue['handler']

# Start recieving message from all the queues
  promise = client.basic_consume_multi(queues=queues, prefetch_count=1)
  while True:
    result = client.wait(promise)

    try:
      message = json_serializer.load_string(result['body'])
      if message['header']['type'] == result['routing_key']:
        handlers[result['routing_key']](message)
      else:
        logging.error('Message does not contain a header.type: %s' % result)
    except Exception:
      logging.exception('Error in handler for event: %s' % result)

    client.basic_ack(result)

  promise = client.close()
  client.wait(promise)


def create_url_from_config(config):
  return 'amqp://{0}:{1}'.format(config['host'], config['port'])


def create_spec_path(base_name):
  return os.path.join(os.environ['TIM_CONFIG'], base_name)
