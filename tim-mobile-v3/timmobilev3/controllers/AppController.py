'''
Created on Apr 18, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from timmobilev3 import tim_config

log = logging.getLogger(__name__)


class AppController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request

  @view_config(route_name='app', request_method='GET', renderer='timmobilev3:templates/app.pt')
  def requestHandler(self):
    return {'author_name': self.request.matchdict['authorname'],
            'api_endpoint': tim_config['api']['endpoint']}

  @view_config(route_name='settings', request_method='GET', renderer='timmobilev3:templates/settings.pt')
  def settingsHandler(self):
    return {'author_name': 'this is me',
            'api_endpoint': tim_config['api']['endpoint']}

  @view_config(route_name='login', request_method='GET', renderer='timmobilev3:templates/login.pt')
  def loginHandler(self):
    return {'author_name': 'this is me',
            'api_endpoint': tim_config['api']['endpoint']}
