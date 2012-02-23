'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession
from mi_schema.models import Author

log = logging.getLogger(__name__)


@view_config(route_name='author.model.build', request_method='GET', renderer='jsonp', http_cache=0)
def authorFull(request):

  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

@view_config(route_name='author.model.update', request_method='GET', renderer='jsonp', http_cache=0)
def authorIncremental(request):

  dbSession = DBSession()
  
  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

