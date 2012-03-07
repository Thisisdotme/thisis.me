'''
Created on Feb 23, 2012

@author: howard
'''
from pyramid.view import view_config
from pyramid.security import authenticated_userid

@view_config(route_name='timeline', request_method='GET', permission='author', renderer='timmobile:templates/timeline.pt')
def newsfeed(request):
  return { 'author_name': authenticated_userid(request),
           'timeline_author_name': request.matchdict['authorname'],
           'api_endpoint':request.registry.settings['mi.api.endpoint'] }