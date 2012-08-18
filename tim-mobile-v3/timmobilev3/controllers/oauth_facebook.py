import logging
import urllib
from urlparse import parse_qs
import json

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import unauthenticated_userid

from timmobilev3 import tim_config

log = logging.getLogger(__name__)

SERVICE = 'facebook'


@view_config(route_name='facebook', request_method='GET', renderer='timmobilev3:templates/oauth.pt')
def get_facebook(request):

  return {'feature': 'Facebook',
          'url': request.route_url('facebook'),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='facebook', request_method='POST')
def post_facebook(request):

  query_args = urllib.urlencode([('client_id', tim_config['oauth'][SERVICE]['key']),
                                ('redirect_uri', request.route_url('facebook_callback')),
                                ('scope', 'offline_access,read_stream,user_photos,user_checkins,user_events,user_groups,user_videos,user_about_me,user_education_history,user_status')])

  url = tim_config['oauth'][SERVICE]['oauth_url'].format(args=query_args)

  return HTTPFound(location=url)


@view_config(route_name='facebook_callback', request_method='GET', renderer='timmobilev3:templates/settings.pt')
def facebook_callback(request):

  error_msg = None

  author_id = unauthenticated_userid(request)

  access_token = None
  fb_user_id = None

  code = request.params.get('code')
  if code:

    # let's get the acces_token
    api_key = tim_config['oauth'][SERVICE]['key']
    api_secret = tim_config['oauth'][SERVICE]['secret']

    query_args = urllib.urlencode([('client_id', api_key),
                                  ('redirect_uri', request.route_url('facebook_callback')),
                                  ('client_secret', api_secret),
                                  ('code', code)])

    url = tim_config['oauth'][SERVICE]['access_token_url'].format(args=query_args)

    try:

      r = requests.get(url)
      r.raise_for_status()

      fb_dict = parse_qs(r.text)

      access_token = fb_dict['access_token'][0]

    except requests.exceptions.RequestException, e:
      log.error(e)
      raise e

    # now let's get some information about the user -- namely their id
    url = '{endpoint}{resource}?access_token={token}'.format(endpoint=tim_config['oauth'][SERVICE]['endpoint'],
                                                             resource='me',
                                                             token=access_token)

    try:
      r = requests.get(url)
      r.raise_for_status()

      me_dict = r.json

      fb_user_id = me_dict['id']

    except requests.exceptions.RequestException, e:
      log.error(e)
      raise e

  else:
    error_reason = request.params.get('error_reason')
    error = request.params.get('error')
    error_description = request.params.get('error_description')
    msg = '%s - %s - %s' % (error_reason, error, error_description)
    log.error(msg)
    raise Exception(msg)

  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE, 'access_token': access_token, 'service_author_id': fb_user_id}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)
    if e.response.status_code == 409:
      error_msg = 'Service already exists for this author ({message})'.format(message=e.message)

  log.info("Added Facebook service for author %s" % author_id)

  json_dict = {'api_endpoint': tim_config['api']['endpoint']}

  if error_msg:
    json_dict['error_msg'] = error_msg

  return json_dict
