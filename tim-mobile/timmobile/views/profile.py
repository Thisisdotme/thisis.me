'''
Created on Mar 1, 2012

@author: martin
'''
from pyramid.view import view_config
from pyramid.security import authenticated_userid

@view_config(route_name='profile', request_method='GET', permission='author', renderer='timmobile:templates/profile.pt')
def newsfeed(request):
  return { 'author_name': request.matchdict['authorname'],
           'api_endpoint':request.registry.settings['mi.api.endpoint'] }