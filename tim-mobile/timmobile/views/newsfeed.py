'''
Created on Feb 23, 2012

@author: howard
'''
from pyramid.view import view_config

@view_config(route_name='home', request_method='GET', permission='author', renderer='timmobile:templates/newsfeed.pt')
@view_config(route_name='newsfeed', request_method='GET', permission='author', renderer='timmobile:templates/newsfeed.pt')
def newsfeed(request):
  return { 'api_endpoint':request.registry.settings['mi.api.endpoint'] }