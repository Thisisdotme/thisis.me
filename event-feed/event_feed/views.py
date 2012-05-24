import logging
import json

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from tim_commons.message_queue import send_messages
from tim_commons.messages import create_facebook_notification
from tim_commons.config import ENVIRONMENT_KEY


@view_config(request_method='GET', route_name='facebook_feed')
def get_facebook_feed(request):
  hub_mode = request.GET.get('hub.mode', None)
  hub_verify_token = request.GET.get('hub.verify_token', None)
  hub_challenge = request.GET.get('hub.challenge', None)

  verify_token = request.registry.settings[ENVIRONMENT_KEY]['feed']['verify_token']

  if (hub_mode == 'subscribe' and
      hub_verify_token == verify_token and
      hub_challenge is not None):
    return Response(body=request.GET.getone('hub.challenge'))
  else:
    logging.info('Invalid request: mode = %s, verify_token = %s, challenge = %s',
                 hub_mode,
                 hub_verify_token,
                 hub_challenge)
    return HTTPNotFound()


@view_config(request_method='POST',
             route_name='facebook_feed',
             header="Content-Type:application/json")
def post_facebook_feed(request):
  facebook_notification = json.loads(request.body)

  events = convert_facebook_notification(facebook_notification)
  queue = request.registry.settings[ENVIRONMENT_KEY]['queues']['facebook']['notification']
  send_messages(request.message_client, queue, events)

  return Response()


def convert_facebook_notification(facebook_notification):
  def has_id(notification):
    uid = notification.get('uid', None)
    if uid is None:
      logging.warning('The facebook notification did not contain an id: %s',
                      notification)

    return uid is not None

  def convert(notification):
    return create_facebook_notification(notification['uid'])

  # Only deal with changes to the user object
  object = facebook_notification.get('object', None)
  if object == 'user':
    return map(convert, filter(has_id,
                               facebook_notification.get('entry', None)))

  else:
    # Right now we are only subscribing to user object so we should only get
    # user objects
    logging.warning('Received a notifaction for an object that is not user: %s',
                    facebook_notification)
    return []
