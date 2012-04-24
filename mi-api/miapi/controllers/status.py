from pyramid.view import view_config

from time import ctime

class StatusController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request

  @view_config(route_name='status', request_method='GET', renderer='jsonp', http_cache=0)
  def status(self):

    return {'status':'ok','date':ctime()}
  
