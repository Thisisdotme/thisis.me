import logging

import pyramid.view
import pyramid.security

from miapi import resource
from data_access import author


@pyramid.view.view_config(
    context=resource.V1Root,
    name='login',
    request_method='POST',
    renderer='jsonp')
def login(request):
  post = request.json_body
  login = post.get('login')
  password = post.get('password')

  user = author.query_by_author_name(login)
  if user and check_password(user.password, password):
    headers = pyramid.security.remember(request, user.id)
    logging.info('header: %s', headers)
    request.response.headers.update(headers)
    return request.response

  return error(request.response, AUTHN_BAD_USER_PASSWD)


@pyramid.view.view_config(
    context=resource.V1Root,
    name='logout',
    request_method='POST',
    renderer='jsonp')
def logout(request):
  headers = pyramid.security.forget(request)
  request.response.headers.update(headers)
  return request.response


# TODO move this and the error method somewhere else
AUTHN_BAD_USER_PASSWD = 40001


def error(response, internal_code):
  # TODO: implement message
  response.status_int = internal_code / 100
  return {'http_code': response.status_int,
          'http_status': response.status,
          'code': internal_code}


def check_password(expected_encoded_password, actual_plain_password):
  return expected_encoded_password == actual_plain_password
