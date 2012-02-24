'''
Created on Feb 23, 2012

@author: howard
'''
from pyramid.view import view_config

@view_config(route_name='accounts', request_method='GET', permission='author', renderer='timmobile:templates/accounts.pt')
def accounts(request):
  return { 'api_endpoint':request.registry.settings['mi.api.endpoint'] }