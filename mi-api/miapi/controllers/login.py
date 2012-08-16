import passlib.hash
import pyramid.security

import data_access.author

import miapi.resource
import miapi.error
import miapi.json_renders.author


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
    return miapi.json_renders.author.to_person_fragment_JSON_dictionary(user)

  return miapi.error.http_error(request.response, **miapi.error.AUTHN_BAD_USER_OR_PASSWD)


def logout(request):
  headers = pyramid.security.forget(request)
  request.response.headers.extend(headers)
  return request.response


def check_password(expected_encoded_password, actual_plain_password):
  return passlib.hash.sha256_crypt.verify(actual_plain_password, expected_encoded_password)


def authenticate_user(user_id, request):
  # TODO: check that the user exists
  return []
