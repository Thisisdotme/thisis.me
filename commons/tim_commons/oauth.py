import BaseHTTPServer
from json import load

http_status_print = BaseHTTPServer.BaseHTTPRequestHandler.responses


# Exception class for communicating errors from make_request
class OAuthError(Exception):
  def __init__(self, code, msg):
    super(OAuthError, self).__init__(msg)
    self.code = code
    self.msg = msg

  def toString(self):
    return '%s#%s' % (self.code, self.msg)


# load the oauth config
def load_oauth_config(path):

  oauthfd = open(path)
  config = load(oauthfd)
  oauthfd.close()

  return config


# Simple oauth request wrapper to handle responses and exceptions
def make_request(client, url, request_headers={}, error_string="Failed Request", method="GET", body=None):
  if body:
    resp, content = client.request(url, method, headers=request_headers, body=body)
  else:
    resp, content = client.request(url, method, headers=request_headers)

  if resp.status >= 200 and resp.status < 300:
    contentType = resp.get('content-type')
    if contentType and 'utf-8' in contentType.lower():
      content = content.decode('utf-8')
    return content
  elif resp.status >= 500 and resp.status < 600:
    message = 'An application error occurred! HTTP %s response received.' % resp.status
    raise OAuthError(resp.status, message)

  else:
    status_codes = {
            400: 'The request could not be understood by the server due to malformed syntax.  Usually this means the request was formatted incorrectly or included an unexpected parameter.',
            401: 'The request requires user authentication.  Usually this means the OAuth signature was bad.',
            403: 'The server understood the request, but is refusing to fulfill it.  This might mean a throttle limit has been reached.',
            404: 'The server has not found anything matching the Request-URI.  The resource was not found.',
            405: 'The method specified in the Request-Line is not allowed for the resource identified by the Request-URI.  Usually this means a wrong HTTP method was used (GET when you should POST, etc).'
            }
    if resp.status in status_codes:
      raise OAuthError(resp.status, status_codes[resp.status])
    else:
      raise OAuthError(resp.status, http_status_print[resp.status][1])
