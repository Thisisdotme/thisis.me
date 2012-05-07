import threading
import puka
import json
import logging

# Thread local client
threadlocal = threading.local()
def get_current_message_client(host):
  map = getattr(threadlocal, 'puka_client', None)
  if map is None:
    map = {}
    setattr(threadlocal, 'puka_client', map)

  client = map.get(host, None)
  if client is None:
    client = create_message_client(host)
    map[host] = client

  return client

def create_message_client(host):
  client = puka.Client(host)
  promise = client.connect()
  client.wait(promise)

  return client

def send_messages(client, queue, messages):
  # Send all the messages
  promises = []
  for message in messages:
    promise = client.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=json.dumps(message))
    promises.append(promise)
      
  # Wait until all the message were sent
  for promise in promises:
    client.wait(promise)

def join(client, queue, handler):
  '''
  Receives messages from the message queue and forwards them to the
  handler. The handler needs to implement a handler method that accepts one
  parameter. The parameter is the map representing the JSON object.
  '''
  promise = client.basic_consume(queue=queue, prefetch_count=1)
  while True:
    result = client.wait(promise)
      
    try:
      message = json.loads(result['body'])
      if message['header']['type'] == queue:
        handler(message)
      else:
        logging.error('Message does not contain a header.type: %s' % result)
    except Exception, e:
      logging.exception('Error in handler for event: %s' % result)

    client.basic_ack(result)

  promise = client.close()
  client.wait(promise)


# All of the messages we send must have the following structure:
# { 'header': { 'version': <int>, 'type': <string> },
#   'message': <message> }
#
# The tuple (header.version, header.type) uniquely identifies the contect of
# the field message.


def create_facebook_notification(facebook_id):
  return { 'header': { 'version': 1,
                       'type': 'facebook.notification' },
           'message': { 'service_author_id': facebook_id} }
