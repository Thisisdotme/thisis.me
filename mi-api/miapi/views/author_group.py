'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession


log = logging.getLogger(__name__)


# GET /v1/authors/{authorname}/groups
#
# return all authors that match the specified search criteria
#
@view_config(route_name='author.groups', request_method='GET', renderer='jsonp', http_cache=0)
def listGroups(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}


# GET /v1/authors/{authorname}/groups/{groupname}
#
@view_config(route_name='author.groups.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def getGroup(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# PUT /v1/authors/{authorname}/groups/{groupname}
#
@view_config(route_name='author.groups.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def addUpdateGroup(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# DELETE /v1/authors/{authorname}/groups/{groupname}
#
@view_config(route_name='author.groups.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def deleteGroup(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# GET /v1/authors/{authorname}/groups/{groupname}/members
#
@view_config(route_name='author.groups.members', request_method='GET', renderer='jsonp', http_cache=0)
def getGroupMembers(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# GET /v1/authors/{authorname}/groups/{groupname}/members/{member}
#
@view_config(route_name='author.groups.members.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def getGroupMember(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# PUT /v1/authors/{authorname}/groups/{groupname}/members/{member}
#  
@view_config(route_name='author.groups.members.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def addUpdateGroupMember(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}

# DELETE /v1/authors/{authorname}/groups/{groupname}/members/{member}
#
@view_config(route_name='author.groups.members.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def deleteGroupMember(request):
  
  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}
