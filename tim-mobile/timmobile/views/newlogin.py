'''
Created on Feb 23, 2012

@author: howard
'''
from pyramid.view import view_config

@view_config(route_name='newlogin', request_method='GET', renderer='timmobile:templates/newlogin.pt')
def newuser(request):
  return { 'api_endpoint':request.registry.settings['mi.api.endpoint'] }