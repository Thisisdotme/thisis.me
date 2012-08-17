'''
Created on Apr 18, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from timmobilev3 import tim_config

log = logging.getLogger(__name__)


class IndexController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request

  @view_config(route_name='index', request_method='GET', renderer='timmobilev3:templates/index.pt')
  def requestHandler(self):
    return {'api_endpoint': tim_config['api']['endpoint'], 'author_name': 'thisis.me'}
