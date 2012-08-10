import logging
import urllib
from urlparse import parse_qs
import json

import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from timmobilev2 import tim_config

log = logging.getLogger(__name__)

FEATURE = 'facebook'


@view_config(route_name='facebook', request_method='GET', renderer='timmobilev2:templates/oauth.pt', permission='author')
def get_facebook(request):

  # TODO - how do we do this ???

  return {'feature': 'Facebook',
          'url': request.route_url('facebook'),
          'api_endpoint': request.registry.settings['mi.api.endpoint']}


@view_config(route_name='facebook', request_method='POST', permission='author')
def post_facebook(request):

  api_key = tim_config['oauth'][FEATURE]['key']

  query_args = urllib.urlencode([('client_id', api_key),
                                ('redirect_uri', request.route_url('facebook_callback')),
                                ('scope', 'offline_access,read_stream,user_photos,user_checkins,user_events,user_groups,user_videos,user_about_me,user_education_history,user_status')])

  url = tim_config['oauth'][FEATURE]['oauth_url'].format(args=query_args)

  return HTTPFound(location=url)


@view_config(route_name='facebook_callback', request_method='GET', renderer='timmobilev2:templates/confirmation.pt')
def facebook_callback(request):

  authorName = authenticated_userid(request)

  access_token = None
  fb_user_id = None

  code = request.params.get('code')
  if code:

    print 'code => %s' % code

    # let's get the acces_token
    api_key = tim_config['oauth'][FEATURE]['key']
    api_secret = tim_config['oauth'][FEATURE]['secret']

    query_args = urllib.urlencode([('client_id', api_key),
                                  ('redirect_uri', request.route_url('facebook_callback')),
                                  ('client_secret', api_secret),
                                  ('code', code)])

    url = tim_config['oauth'][FEATURE]['access_token_url'].format(args=query_args)

    try:

      r = requests.get(url)
      fb_dict = parse_qs(r.text)

#      req = urllib2.Request(url)
#      res = urllib2.urlopen(req)
#      fbDict = parse_qs(res.read())

      access_token = fb_dict['access_token'][0]

#    except urllib2.URLError, e:
#      log.error(e.reason)
#      raise e

    except requests.exceptions.RequestException, e:
      log.error(e)
      raise e

    # now let's get some information about the user -- namely their id
    url = '{endpoint}{resource}?access_token={token}'.format(endpoint=tim_config['oauth'][FEATURE]['url'],
                                                             resource='me',
                                                             token=access_token)

    r = requests.get(url)
    me_dict = r.json

    fb_user_id = me_dict['id']

  else:
    error_reason = request.params.get('error_reason')
    error = request.params.get('error')
    error_description = request.params.get('error_description')
    msg = '%s - %s - %s' % (error_reason, error, error_description)
    log.error(msg)
    raise Exception(msg)

  url = '{endpoint}/v1/authors/{author}/services/{service}'.format(endpoint=tim_config['api']['endpoint'],
                                                                   author=authorName,
                                                                   service=FEATURE)
  payload = {'access_token': access_token, 'service_author_id': fb_user_id}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  r = requests.put(url, data=json.dumps(payload), headers=headers, cookies=cookies)
  res_json = r.json

#  req = RequestWithMethod('%s/v1/authors/%s/services/%s' %
#                                  (,authorName,FEATURE),
#                          'PUT',
#                          json_payload,
#                          headers)
#  res = urllib2.urlopen(req)
#  resJSON = json.loads(res.read())

  log.info("Added Facebook feature for author %s" % authorName)

  request.session.flash('Your Facebook account has been successfully added.')
  return HTTPFound(location=request.route_path('newsfeed'))
