import logging
import urlparse
import urllib
import oauth2 as oauth
import json
import requests

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import unauthenticated_userid

from tim_commons.oauth import make_request

from timmobilev2 import tim_config

log = logging.getLogger(__name__)

SERVICE = 'twitter'


@view_config(route_name='twitter', request_method='GET', renderer='timmobilev2:templates/oauth.pt')
def get_twitter(request):

  return {'feature': 'Twitter',
          'url': request.route_url(SERVICE),
          'api_endpoint': tim_config['api']['endpoint']}


@view_config(route_name='twitter', request_method='POST')
def post_twitter(request):

  consumer_key = tim_config['oauth'][SERVICE]['key']
  consumer_secret = tim_config['oauth'][SERVICE]['secret']

  consumer = oauth.Consumer(consumer_key, consumer_secret)
  client = oauth.Client(consumer)

  # Step 1: Get a request token. This is a temporary token that is used for
  # having the user authorize an access token and to sign the request to obtain
  # said access token.
  callback = request.route_url('twitter_callback')
  resp, content = client.request(tim_config['oauth'][SERVICE]['request_token_url'], "POST", body=urllib.urlencode({'oauth_callback': callback}))
  if resp['status'] != '200':
    raise Exception('Invalid response {status} ({message}).'.format(status=resp['status'],
                                                                    message=content))

  request_token = dict(urlparse.parse_qsl(content))

  # Step 2: Redirect to the provider.
  request.session['oauth_token_secret'] = request_token['oauth_token_secret']

  redirectURL = "{endpoint}?oauth_token={token}".format(endpoint=tim_config['oauth'][SERVICE]['authorize_url'],
                                                        token=request_token['oauth_token'])

  return HTTPFound(location=redirectURL)


@view_config(route_name='twitter_callback', request_method='GET')
def twitter_callback(request):

  author_id = unauthenticated_userid(request)

  # the oauth_token is request as a query arg; the auth_token_secret is in session store
  oauth_token = request.params['oauth_token']
  oauth_token_secret = request.session['oauth_token_secret']

  oauth_verifier = request.params['oauth_verifier']

  # Step 3: Once the consumer has redirected the user back to the oauth_callback
  # URL you can request the access token the user has approved. You use the
  # request token to sign this request. After this is done you throw away the
  # request token and use the access token returned. You should store this
  # access token somewhere safe, like a database, for future use.
  consumer_key = tim_config['oauth'][SERVICE]['key']
  consumer_secret = tim_config['oauth'][SERVICE]['secret']

  consumer = oauth.Consumer(consumer_key, consumer_secret)
  token = oauth.Token(oauth_token, oauth_token_secret)

  client = oauth.Client(consumer, token)

  token.set_verifier(oauth_verifier)

  resp, content = client.request(tim_config['oauth'][SERVICE]['access_token_url'], "POST")
  if resp['status'] != '200':
    raise Exception('Invalid response {status} ({message}).'.format(status=resp['status'],
                                                                    message=content))

  access_token = dict(urlparse.parse_qsl(content))

  # these tokens are the real deal and need to be passed to the API
  oauth_token = access_token['oauth_token']
  oauth_token_secret = access_token['oauth_token_secret']

  token = oauth.Token(oauth_token, oauth_token_secret)
  client = oauth.Client(consumer, token)

  # get some information about the user from twitter
  url = '{endpoint}account/verify_credentials.json'.format(endpoint=tim_config['oauth'][SERVICE]['endpoint'])
  json_dict = json.loads(make_request(client, url).decode('utf-8'))

  url = '{endpoint}/v1/authors/{author}/services'.format(endpoint=tim_config['api']['endpoint'],
                                                         author=author_id)
  payload = {'name': SERVICE,
             'access_token': oauth_token,
             'access_token_secret': oauth_token_secret,
             'service_author_id': json_dict['id']}
  headers = {'content-type': 'application/json; charset=utf-8'}
  cookies = request.cookies

  try:
    r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)
    r.raise_for_status()
  except requests.exceptions.RequestException, e:
    log.error(e.message)

  log.info("Added Twitter service for author %s" % author_id)

  return HTTPFound(location=request.route_path('settings'))
