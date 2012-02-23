from pyramid.view import view_config
from pyramid.response import Response

from timweb.exceptions import GenericError
from timweb.exceptions import UnexpectedAPIResponse 

@view_config(context=GenericError)
def generic_error(exc, request):
  response =  Response('Generic error: %s' % exc.msg)
  response.status_int = 500
  return response

@view_config(context=UnexpectedAPIResponse)
def generic_error(exc, request):
  response =  Response('Unexpected API response error: %s' % exc.msg)
  response.status_int = 500
  return response

#@view_config(context=Exception)
#def catchall_error(exc, request):
#  response =  Response('Unexpected error')
#  response.status_int = 500
#  return response