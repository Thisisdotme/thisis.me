import logging
import urllib2
import urllib
import json
from datetime import datetime

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from instagram import client

from tim_commons.request_with_method import RequestWithMethod

from timmobilev2 import tim_config


SERVICE = 'instagram'

log = logging.getLogger(__name__)


@view_config(route_name='instagram', request_method='GET', renderer='timmobilev2:templates/oauth.pt')
def get_instagram(request):

  return {'feature': 'Instagram',
          'url': request.route_url(SERVICE),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='instagram', request_method='POST')
def post_instagram(request):

  config = {'client_id': tim_config['oauth'][SERVICE]['key'],
            'client_secret': tim_config['oauth'][SERVICE]['secret'],
            'redirect_uri': request.route_url('instagram_callback')}

  unauthenticated_api = client.InstagramAPI(**config)

  redirectURL = unauthenticated_api.get_authorize_url(scope=["likes", "comments"])

  return HTTPFound(location=redirectURL)


@view_config(route_name='instagram_callback', request_method='GET')
def instagram_callback(request):

  code = request.params.get('code')

  # TODO: proper handling of error case
  if not code:
    raise Exception('missing code query argument from Instagram callback')

  # Get author's login name
  author_id = authenticated_userid(request)

  config = {'client_id': tim_config['oauth'][SERVICE]['key'],
            'client_secret': tim_config['oauth'][SERVICE]['secret'],
            'redirect_uri': request.route_url('instagram_callback')}

  unauthenticated_api = client.InstagramAPI(**config)

  access_token = unauthenticated_api.exchange_code_for_access_token(code)

  # TODO: proper handling of error case
  if not access_token:
    raise Exception('no access_token returned from Instagram when exchanging code for access_token')

  # get the author's instagram user id, name, etc
  url = '{endpoint}{resource}?{token}'.format(endpoint=tim_config['oauth'][SERVICE]['endpoint'],
                                              resource='users/self',
                                              token=urllib.urlencode({'access_token': access_token}))
  try:

    r = requests.get(url)
    r.raise_for_status()

    json_dict = r.json

  except requests.exceptions.RequestException, e:
    log.error(e)
    raise e

  instagram_author_id = json_dict['data']['id']

  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE, 'access_token': access_token, 'service_author_id': instagram_author_id}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)

  return HTTPFound(location=request.route_path('settings'))
