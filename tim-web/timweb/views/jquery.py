from pyramid.view import view_config

@view_config(route_name='jquery', request_method='GET', renderer='timweb:templates/jquery.pt')
def jquery(request):
  return {}

@view_config(route_name='jquery_json', request_method='POST', renderer='jsonp')
def jquery_json(request):
  print request.json_body
  return {'status':'ok'}