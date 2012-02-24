'''
Created on Feb 23, 2012

@author: howard
'''
from pyramid.view import view_config

@view_config(route_name='account_details', request_method='GET', permission='author', renderer='timmobile:templates/account_details.pt')
def getAccount(request):

  featureName = request.matchdict['featurename']
  
  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return { 'feature': featureName,
           'api_endpoint':request.registry.settings['mi.api.endpoint'],
           'message':message }
