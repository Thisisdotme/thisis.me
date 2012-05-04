import threading
import puka
import json

# Thread local client
# TODO: should probably use tornado so we don't need to do this
threadlocal = threading.local()
def get_current_message_client(host):
  map = getattr(threadlocal, 'puka_client', None)
  if map is None:
    map = {}
    setattr(threadlocal, 'puka_client', map)

  client = map.get(host, None)
  if not client:
    client = MessageClient(puka.Client(host))

    # Connect to message queue
    promise = client._client.connect()
    client._client.wait(promise)

    map[host] = client

  return client

class MessageClient:
  def __init__(self, client):
    self._client = client

  # Send message
  def send_messages(self, queue, messages):
    def send_message(message):
      return self._client.basic_publish(exchange='',
                                        routing_key=queue,
                                        body=message)

    # TODO: probably want to remove queue declaration out of here
    promise = self._client.queue_declare(queue=queue, durable=True)
    self._client.wait(promise)

    promises = map(send_message, messages)
      
    for promise in promises:
      self._client.wait(promise)

class MessageReceiver:
  '''
  Receives messages from the message queue and forwards them to the
  handler. The handler needs to implement a handler method that accepts one
  parameter. The parameter is the map representing the JSON object.
  '''
  def __init__(self, client, queue, handler):
    self._client = client
    self._handler = handler
    self._queue = queue

  def join(self):
    pass


# All of the messages we send must have the following structure:
# { 'header': { 'version': <int>, 'type': <string> },
#   'message': <message> }
#
# The tuple (header.version, header.type) uniquely identifies the contect of
# the field message.


def create_facebook_notification(facebook_id):
  return json.dumps({ 'header': { 'version': 1,
                                  'type': 'facebook.notification' },
                      'message': { 'service_author_id': facebook_id} })
