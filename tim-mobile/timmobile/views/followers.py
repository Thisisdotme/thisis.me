'''
Created on Mar 8, 2012

@author: Andrew
'''
from pyramid.view import view_config
from pyramid.security import authenticated_userid

@view_config(route_name='followers', request_method='GET', permission='author', renderer='timmobile:templates/followers.pt')
def followers(request):
  return { 'author_name': authenticated_userid(request),
           'api_endpoint':request.registry.settings['mi.api.endpoint']
           }
