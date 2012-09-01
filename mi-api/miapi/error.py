AUTHN_BAD_USER_OR_PASSWD = {'http_code': 400, 'code': 1}
NOT_FOUND = {'http_code': 404, 'code': 2}
UNAUTHORIZED = {'http_code': 401, 'code': 3}


def http_error(response, http_code=400, code=None, message=None):
  response.status_int = http_code
  return {'http_code': response.status_int,
          'http_status': response.status,
          'code': code}
