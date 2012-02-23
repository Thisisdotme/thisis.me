from pyramid.view import view_config

@view_config(route_name='about', request_method='GET', renderer='timweb:templates/about.pt')
def about(request):
    return {'title':'About'}
