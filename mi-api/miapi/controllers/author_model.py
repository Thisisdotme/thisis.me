'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession

log = logging.getLogger(__name__)


class AuthorModelController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()


  @view_config(route_name='author.model.build', request_method='GET', renderer='jsonp', http_cache=0)
  def authorFull(self):
  
    authorName = self.request.matchdict['authorname']
  
    return {'error':'not implemented'}


  @view_config(route_name='author.model.update', request_method='GET', renderer='jsonp', http_cache=0)
  def authorIncremental(self):
  
    authorName = self.request.matchdict['authorname']
  
    return {'error':'not implemented'}
  
