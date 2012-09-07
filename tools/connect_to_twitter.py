import sys
import oauth2 as oauth
import time

import requests

import tim_commons.db
import tim_commons.app_base
import data_access.service
import data_access.post_type
import data_access.author
import data_access.author_service_map


class ConnectToTwitter(tim_commons.app_base.AppBase):
  def display_usage(self):
    return 'usage: %prog [options] author_name'

  def parse_args(self, args):
    if len(args) != 1:
      self.error('Only one positional parameter supported')

  def app_main(self, config, options, args):
    tim_commons.db.configure_session(tim_commons.db.create_url_from_config(config['db']))

    data_access.service.initialize()
    data_access.post_type.initialize()

    # Grab twitter consumer keys
    consumer_key = config['oauth']['twitter']['key']
    consumer_secret = config['oauth']['twitter']['secret']

    twitter_id = data_access.service.name_to_id('twitter')
    author = data_access.author.query_by_author_name(args[0])
    author_service_map = data_access.author_service_map.query_asm_by_author_and_service(
        author.id,
        twitter_id)

    # Make request
    method = 'POST'
    url = 'https://stream.twitter.com/1/statuses/filter.json'
    data = {'follow': author_service_map.service_author_id}

    headers = _sign_request(
        method=method,
        url=url,
        data=data,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        token_key=author_service_map.access_token,
        token_secret=author_service_map.access_token_secret)
    headers['Authorization'] = headers['Authorization'].encode('ascii')
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    response = requests.request(method, url, data=data, headers=headers)
    response.raise_for_status()


def _sign_request(method, url, consumer_key, consumer_secret, token_key, token_secret, data):
  token = oauth.Token(key=token_key, secret=token_secret)
  consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
  params = dict(
      {'oauth_version': '1.0',
       'oauth_nonce': oauth.generate_nonce(),
       'oauth_timestamp': int(time.time())},
      **data)
  req = oauth.Request(url=url, method=method, parameters=params)
  signature_method = oauth.SignatureMethod_HMAC_SHA1()
  req.sign_request(signature_method, consumer, token)

  header = req.to_header()
  return header


if __name__ == '__main__':
  sys.exit(ConnectToTwitter('conntect_to_twitter').main())
