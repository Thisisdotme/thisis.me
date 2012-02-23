from pyramid.view import view_config

@view_config(route_name='feature_timeline', request_method='GET', renderer='timviewer:templates/feature.pt')
def timeline(request):
  author_name = request.matchdict['authorname']
  feature_name = request.matchdict['featurename']
  return { 'author_name':author_name,
           'feature_name':feature_name,
           'api_endpoint':request.registry.settings['mi.api.endpoint'],
           'theme': request.registry.settings['mi.theme.main'] }
