'''
Created on Jan 9, 2012

@author: howard
'''
import logging


from pyramid.view import view_config


log = logging.getLogger(__name__)


##
## author FeatureEvents functionality
##

  

# mark as read
@view_config(route_name='author.featureEvents.featureEvent.read.user.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def authorFeatureEventPut(request):
  return {'status':'not yet implemented'}


# mark as unread
@view_config(route_name='author.featureEvents.featureEvent.read.user.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def authorFeatureEventDelete(request):
  return {'status':'not yet implemented'}

