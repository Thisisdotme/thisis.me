from pyramid.view import view_config

@view_config(route_name='features', request_method='GET', renderer='timweb:templates/features.pt')
def about(request):
    return {'title':'Features'}
