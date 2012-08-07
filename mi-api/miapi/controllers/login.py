import pyramid.view
import pyramid.security

import miapi.resource
import data_access.author


def add_views(configuration):
  configuration.add_view(
      login,
      context=miapi.resource.V1Root,
      name='login',
      request_method='POST',
      permission='login',
      renderer='jsonp')
  configuration.add_view(
      logout,
      context=miapi.resource.V1Root,
      name='logout',
      request_method='POST',
      permission='logout',
      renderer='jsonp')


def login(request):
  post = request.json_body
  login = post.get('login')
  password = post.get('password')

  user = data_access.author.query_by_author_name(login)
  if user and check_password(user.password, password):
    headers = pyramid.security.remember(request, user.id)
    request.response.headers.extend(headers)
    return request.response

  return error(request.response, AUTHN_BAD_USER_OR_PASSWD)


def logout(request):
  headers = pyramid.security.forget(request)
  request.response.headers.extend(headers)
  return request.response


# TODO move this and the error method somewhere else
AUTHN_BAD_USER_OR_PASSWD = 40001


def error(response, internal_code):
  # TODO: implement message
  response.status_int = internal_code / 100
  return {'http_code': response.status_int,
          'http_status': response.status,
          'code': internal_code}


def check_password(expected_encoded_password, actual_plain_password):
  return expected_encoded_password == actual_plain_password


def authenticate_user(user_id, request):
  # TODO: check that the user exists
  return []
