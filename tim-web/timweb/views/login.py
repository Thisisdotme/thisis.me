import logging

from pyramid.view import view_config
from pyramid.httpexceptions import (HTTPFound, HTTPForbidden)
from pyramid.security import (authenticated_userid,remember,forget)
from pyramid.url import route_url

from sqlalchemy import func

from mi_schema.models import Author

from timweb.models import DBSession

log = logging.getLogger(__name__)

@view_config(context=HTTPForbidden)
def forbidden_view(request):

  # do not allow a user to login if they are already logged in
  if authenticated_userid(request):
      return HTTPForbidden()
  
  loc = request.route_url('login', _query=(('forward', request.path),))
  return HTTPFound(location=loc)


@view_config(route_name='login', renderer='timweb:templates/login.pt')
def login_view(request):
  
  login = ''
  password = ''
  message = ''

  forward = request.params.get('forward') or request.route_url('home')

  if 'form.submitted' in request.POST:

    login = request.POST.get('login', '')
    password = request.POST.get('password', '')

    # query the db for the username/password combo
    dbsession = DBSession()
    count = dbsession.query(func.count('*')).select_from(Author).filter_by(author_name=login,password=password).scalar()

    if count == 1:
      log.info('Login for user: %s' % login)
      request.session['logged_id'] = '1'
      headers = remember(request, login)
      return HTTPFound(location=forward, headers=headers)
  
    message = 'Failed login.  Invalid authorname or password'

  return dict(
    message = message,
    url = request.route_path('login'),
    forward = forward,
    login = login,
    password = password,
    title = 'Login'
    )


@view_config(route_name='logout')
def logout(request):
  
  # delete everything from the session
  request.session.delete()

  log.info('Logout for user %s' % authenticated_userid(request))
  headers = forget(request)
  return HTTPFound(location = route_url('home', request),
         headers = headers)
