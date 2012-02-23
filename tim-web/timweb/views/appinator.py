from pyramid.view import view_config

@view_config(route_name='appinator', request_method='GET', renderer='timweb:templates/appinator.pt', permission='author')
def appinator(request):
  return {'title':'Appinator'}
