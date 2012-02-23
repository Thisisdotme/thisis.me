from pyramid.view import view_config

from time import ctime

@view_config(route_name='status', request_method='GET', renderer='jsonp', http_cache=0)
def status(request):
  
  return {'status':'ok','date':ctime()}

