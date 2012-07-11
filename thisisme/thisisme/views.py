from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
  return {'title': 'Home'}


@view_config(route_name='myapp', renderer='templates/myapp.pt')
def myapp(request):
  return {'title': 'My App'}


@view_config(route_name='features', renderer='templates/features.pt')
def features(request):
  return {'title': 'Features'}


@view_config(route_name='pricing', renderer='templates/pricing.pt')
def pricing(request):
  return {'title': 'Pricing'}


@view_config(route_name='about', renderer='templates/about.pt')
def about(request):
  return {'title': 'About'}


@view_config(route_name='terms', renderer='templates/terms.pt')
def terms(request):
  return {'title': 'Terms'}


@view_config(route_name='contact', renderer='templates/contact.pt')
def contact(request):
  return {'title': 'Contact'}
