import logging
import urllib
import json

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import unauthenticated_userid

from timmobilev2 import tim_config

log = logging.getLogger(__name__)

SERVICE = 'googleplus'


# GET
#
@view_config(route_name='googleplus', request_method='GET', renderer='timmobilev2:templates/oauth.pt')
def googleplus_get(request):
  return {'feature': 'GooglePlus',
          'url': request.route_url('googleplus'),
          'api_endpoint': tim_config['api']['endpoint']}


# POST
#
@view_config(route_name='googleplus', request_method='POST')
def googleplus_post(request):

  queryArgs = urllib.urlencode([('client_id', tim_config['oauth'][SERVICE]['key']),
                                ('redirect_uri', request.route_url('googleplus_callback'))])

  url = '{endpoint}{args}'.format(endpoint=tim_config['oauth'][SERVICE]['oauth_url'],
                                  args=queryArgs)

  return HTTPFound(location=url)


@view_config(route_name='googleplus_callback', request_method='GET', renderer='timmobilev2:templates/settings.pt')
def googleplus_callback(request):

  error_msg = None

  author_id = unauthenticated_userid(request)

  code = request.params.get('code')
  if not code:
    error = request.params.get('error')
    log.error('Google+ oauth failed: %s' % error)
    raise Exception(error)

  # let's exchange the authorization code for an access token and a refresh token
  query_args = {'code': code,
                'client_id': tim_config['oauth'][SERVICE]['key'],
                'client_secret': tim_config['oauth'][SERVICE]['secret'],
                'redirect_uri': request.route_url('googleplus_callback'),
                'grant_type': 'authorization_code'}

  try:

    r = requests.post(tim_config['oauth'][SERVICE]['oauth_exchange_url'], data=query_args)
    r.raise_for_status()

    json_dict = r.json

  except requests.exceptions.RequestException, e:
    log.error(e)
    raise e

  access_token = json_dict['access_token']
  if not 'refresh_token' in json_dict:
    raise Exception('Google+ already authorized')

  refresh_token = json_dict['refresh_token']

  url = tim_config['oauth'][SERVICE]['oauth_endpoint'].format(resource='userinfo',
                                                              token=access_token)

  # now let's get some information about the user -- namely their id
  try:

    r = requests.get(url)
    r.raise_for_status()
    json_dict = r.json

  except requests.exceptions.RequestException, e:
    log.error(e)
    raise e

  google_user_id = json_dict['id']

  # add the feature via the API
  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE, 'access_token': refresh_token, 'service_author_id': google_user_id}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)
    if e.response.status_code == 409:
      error_msg = 'Service already exists for this author ({message})'.format(message=e.message)

  log.info("Added Google+ feature for author %s" % author_id)

  json_dict = {'api_endpoint': tim_config['api']['endpoint']}

  if error_msg:
    json_dict['error_msg'] = error_msg

  return json_dict
