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
  verify_token = request.registry.settings[ENVIRONMENT_KEY]['feed']['verify_token']

  if (request.GET.getone('hub.mode') == 'subscribe' and
      request.GET.getone('hub.verify_token') == verify_token):
    return Response(body=request.GET.getone('hub.challenge'))

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
