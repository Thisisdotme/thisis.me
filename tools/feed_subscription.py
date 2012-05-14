import sys
import logging
from urlparse import parse_qs
from urllib2 import urlopen
from urllib import urlencode

from tim_commons.app_base import AppBase


class Subscriber(AppBase):
  def display_usage(self):
    return ''

  def init_args(self):
    pass

  def parse_args(self, ignore):
    pass

  def main(self):
    verify_token = self.config['feed']['verify_token']
    feed_base_url = self.config['feed']['base_url']
    app_id = self.config['oauth']['facebook']['key']
    app_secret = self.config['oauth']['facebook']['secret']

    # get the access token
    access_token_url = ('https://graph.facebook.com/oauth/access_token?' +
                        'client_id={app_id}&' +
                        'client_secret={app_secret}&' +
                        'grant_type=client_credentials')
    access_token_url = access_token_url.format(app_id=app_id, app_secret=app_secret)
    access_token = parse_qs(urlopen(access_token_url).read())['access_token'][0]
    logging.info('Using token: %s', access_token)

    # Send subscription request
    url = 'https://graph.facebook.com/{app_id}/subscriptions?access_token={access_token}'
    url = url.format(app_id=app_id, access_token=access_token)

    callback_url = feed_base_url + '/feed/facebook'
    subscription = {'object': 'user',
                    'fields': 'feed',
                    'callback_url': callback_url,
                    'verify_token': verify_token}
    data = urlencode(subscription)

    logging.info('POSTing: %s', data)
    urlopen(url, data)

if __name__ == "__main__":
  # Initialize with number of arguments script takes
  sys.exit(Subscriber().main())
