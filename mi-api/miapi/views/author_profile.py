'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession


log = logging.getLogger(__name__)


# return all authors that match the specified search criteria
#
@view_config(route_name='author.profile.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def searchAuthors(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}