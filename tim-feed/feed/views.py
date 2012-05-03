import logging
import json

from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

# TODO: remove this variable
verify_token = 'FJ2ZU6OqL1hgBhIN6pUkt1upge3Zu8NarPc5XRM6s' 

@view_defaults(route_name='facebook_feed')
class FacebookFeed(object):
  def __init__(self, request):
    self.request = request

  @view_config(request_method='GET')
  def get(self):
    if (self.request.GET.getone('hub.mode') == 'subscribe' and 
        self.request.GET.getone('hub.verify_token') == verify_token):
      return Response(body=self.request.GET.getone('hub.challenge'))

    return HTTPNotFound()

  @view_config(request_method='POST', header="Content-Type:application/json")
  def post(self):
    print json.loads(self.request.body)

    return Response()
