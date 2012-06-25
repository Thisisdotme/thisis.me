'''
Created on Apr 18, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

log = logging.getLogger(__name__)


class AppController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request

  @view_config(route_name='app', request_method='GET', renderer='timmobilev2:templates/app.pt')
  def requestHandler(self):
    return {'author_name': self.request.matchdict['authorname'],
            'api_endpoint': self.request.registry.settings['mi.api.endpoint']}
