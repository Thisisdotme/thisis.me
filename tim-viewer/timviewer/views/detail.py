from pyramid.view import view_config

@view_config(route_name='details', request_method='GET', renderer='timviewer:templates/detail.pt')
def detail(request):
  author_name = request.matchdict['authorname']
  event_id = request.matchdict['eventId']
  return { 'author_name':author_name,
           'feature_name':None,
           'event_id': event_id,
           'api_endpoint':request.registry.settings['mi.api.endpoint'],
           'theme': request.registry.settings['mi.theme.main'] }
