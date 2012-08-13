import logging
import json

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

import flickrapi

from timmobilev2 import tim_config

log = logging.getLogger(__name__)

SERVICE = 'flickr'


@view_config(route_name='flickr', request_method='GET', renderer='timmobilev2:templates/oauth.pt')
def flickr_get(request):
  return {'feature': 'Flickr',
          'url': request.route_url('flickr'),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='flickr', request_method='POST', permission='author')
def flickr_post(request):

  f = flickrapi.FlickrAPI(tim_config['oauth'][SERVICE]['key'],
                          tim_config['oauth'][SERVICE]['secret'],
                          token=None,
                          store_token=False)

  url = f.web_login_url(perms='read')

  return HTTPFound(location=url)


@view_config(route_name='flickr_callback', request_method='GET')
def flickr_callback(request):

  author_id = authenticated_userid(request)

  frob = request.params.get('frob')

  f = flickrapi.FlickrAPI(tim_config['oauth'][SERVICE]['key'],
                          tim_config['oauth'][SERVICE]['secret'],
                          token=None,
                          store_token=False)

  flickr_access_token = f.get_token(frob)

  # TODO: query for flickr user_id
  flickr_user_id = 'UNKNOWN'

  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE, 'access_token': flickr_access_token, 'service_author_id': flickr_user_id}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)

  log.info("Added Flicr service for author %s" % author_id)

  return HTTPFound(location=request.route_path('newsfeed'))
