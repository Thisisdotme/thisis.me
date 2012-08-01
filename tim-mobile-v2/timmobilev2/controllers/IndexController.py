'''
Created on Apr 18, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

log = logging.getLogger(__name__)


class IndexController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request

  @view_config(route_name='index', request_method='GET', renderer='timmobilev2:templates/index.pt')
  def requestHandler(self):
    return {'api_endpoint': self.request.registry.settings['mi.api.endpoint'], 'author_name': 'thisis.me'}
