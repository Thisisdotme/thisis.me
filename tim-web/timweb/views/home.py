from pyramid.view import view_config

@view_config(route_name='home', request_method='GET', renderer='timweb:templates/home.pt')
def about(request):
    return {'title':'Home'}
