import logging
import urllib
import json

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import unauthenticated_userid

from timmobilev2 import tim_config

log = logging.getLogger(__name__)

SERVICE = 'foursquare'


@view_config(route_name='foursquare', request_method='GET', renderer='timmobilev2:templates/oauth.pt')
def foursquare_get(request):
  return {'feature': 'Foursquare',
          'url': request.route_url('foursquare'),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='foursquare', request_method='POST')
def foursquare_post(request):

  queryArgs = urllib.urlencode([('client_id', tim_config['oauth'][SERVICE]['key']),
                                ('response_type', 'code'),
                                ('redirect_uri', request.route_url('foursquare_callback'))])

  url = tim_config['oauth'][SERVICE]['oauth_url'].format(args=queryArgs)

  return HTTPFound(location=url)


@view_config(route_name='foursquare_callback', request_method='GET', renderer='timmobilev2:templates/settings.pt')
def foursquare_callback(request):

  error_msg = None

  author_id = unauthenticated_userid(request)

  code = request.params.get('code')
  if not code:
    error = request.params.get('error')
    raise Exception('Error authenticating user with Foursquare: {error}'.format(error=error))

  # let's get the acces_token
  queryArgs = urllib.urlencode([('client_id', tim_config['oauth'][SERVICE]['key']),
                                ('client_secret', tim_config['oauth'][SERVICE]['secret']),
                                ('grant_type', 'authorization_code'),
                                ('redirect_uri', request.route_url('foursquare_callback')),
                                ('code', code)])

  url = tim_config['oauth'][SERVICE]['access_token_url'].format(args=queryArgs)

  try:

    r = requests.get(url)
    r.raise_for_status()

    json_dict = r.json

  except requests.exceptions.RequestException, e:
    log.error(e)
    raise e

  access_token = json_dict['access_token']

  url = tim_config['oauth'][SERVICE]['4sq_endpoint'].format(resource='users/self',
                                                            token=access_token)

  # now let's get some information about the user -- namely their id
  try:

    r = requests.get(url)
    r.raise_for_status()

    json_dict = r.json

  except requests.exceptions.RequestException, e:
    log.error(e)
    raise e

  if json_dict['meta']['code'] == 200:
    userId = json_dict['response']['user']['id']
  else:
    # TODO: this needs to be cleaned up
    raise Exception('Unexpected error')

  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE, 'access_token': access_token, 'service_author_id': userId}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)
    if e.response.status_code == 409:
      error_msg = 'Service already exists for this author ({message})'.format(message=e.message)

  log.info("Added Foursquare service for author %s" % author_id)

  json_dict = {'api_endpoint': tim_config['api']['endpoint']}

  if error_msg:
    json_dict['error_msg'] = error_msg

  return json_dict
