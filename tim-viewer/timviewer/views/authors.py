from pyramid.view import view_config

@view_config(route_name='authors', request_method='GET', renderer='timviewer:templates/authors.pt')
def authors(request):
  return { 'author_name':None,
           'feature_name': None,
           'api_endpoint':request.registry.settings['mi.api.endpoint'],
           'theme': request.registry.settings['mi.theme.main'] }
