'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession


log = logging.getLogger(__name__)


#
# AUTHOR GROUP QUERY: query for the highlights/details for a particular group (i.e. following)
#

# type and author required; group and feature are optional
def authorGroupQuery(type,author,group=None,feature=None):

  dbSession = DBSession()

  return {'error':'not implemented'}


# return highlights for the group
#

# /v1/authors/{authorname}/groups/{groupname}/highlights
#
@view_config(route_name='author.groups.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
def authorGroupHighlights(request):
  
  authorName = request.matchdict['authorname']
  groupName = request.matchdict['groupname']
  
  return authorGroupQuery('highlights',authorName,group=groupName)


# /v1/authors/{authorname}/groups/{groupname}/events
#
# return all authors that match the specified search criteria
#
@view_config(route_name='author.groups.query.events', request_method='GET', renderer='jsonp', http_cache=0)
def authorGroupEvents(request):
  
  authorName = request.matchdict['authorname']
  groupName = request.matchdict['groupname']
  
  return authorGroupQuery('events',authorName,group=groupName)

