import threading
import puka
import logging
import os

import tim_commons.json_serializer

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


def create_exchange(client, exchange, type):
  promise = client.exchange_declare(exchange=exchange, type=type)
  client.wait(promise)


def create_queue(client, queue, exchange, routing_keys, durable=True, exclusive=False):
  ''' Creates a queue

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queue -- the queue name
  exchange -- name of the exchange
  routing_keys -- array of routing keys
  '''

  promise = client.queue_declare(queue=queue, durable=durable)
  client.wait(promise)

  for routing_key in routing_keys:
    promise = client.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
    client.wait(promise)


def create_queues_from_config(client, config):
  # lets create the exchange
  create_exchange(client, config['exchange']['name'], config['exchange']['type'])

  for queue in config['queues'].itervalues():
    if not tim_commons.to_bool(queue['exclusive']):
      create_queue(
          client,
          queue['queue'],
          queue['exchange'],
          queue['routing_keys'],
          tim_commons.to_bool(queue['durable']),
          tim_commons.to_bool(queue['exclusive']))
    else:
      logging.info('Not creating queue %s from config because it is exclusing', queue)


def delete_queues(client, queues, force=False):
  promises = []
  for queue in queues:
    promise = client.queue_delete(queue=queue, if_empty=not force)
    promises.append(promise)

  for promise in promises:
    try:
      client.wait(promise)
    except puka.NotFound:
      # Lets ignore not found errors
      pass
    except puka.PreconditionFailed, e:
      logging.info('Unable to delete queue: %s', e)


def send_messages(client, exchange, messages):
  ''' Sends a list of messages to the appropriate queue.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  messages -- list of message to push
  '''
  # Send all the messages
  for message in messages:
    routing_key = message['header']['type'].encode('ascii')
    body = tim_commons.json_serializer.dump_string(message)
    promise = client.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body)
    client.wait(promise)


def join(client, queue, handler):
  '''
  Receives messages from the message queues and forwards them to the
  handler for the corresponding queue. The handler needs to accepts
  one parameter. The parameter is the map representing the JSON object.

  Arguments:
  client -- the object returned by create_message_client or
            get_current_message_client
  queue --  the name of queue to listen on
  handler -- the handler to execute for each messagea
  '''

  # Start recieving message from all the queues
  promise = client.basic_consume(queue=queue, prefetch_count=1)
  while True:
    result = client.wait(promise)

    try:
      message = tim_commons.json_serializer.load_string(result['body'])
      if message['header']['type'] == result['routing_key']:
        handler(message)
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
