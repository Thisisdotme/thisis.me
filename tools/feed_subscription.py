from urllib2 import urlopen, URLError, HTTPError
from urllib import urlencode
from sys import exit
from mi_utils.app_base import AppBase
from feed.views import verify_token
import json

# TODO: Get this somewhere else
APP_AUTH = {'app_id': '237395986367316',
            'access_token': '237395986367316|Beiq_CgBN5lBET_J1mE_zBi2j5I'}
URL = 'https://graph.facebook.com/%(app_id)s/subscriptions?access_token=%(access_token)s'
CALLBACK_URL = 'http://ec2-50-16-11-63.compute-1.amazonaws.com:8888/feed/facebook'


class Subscriber(AppBase):
  def display_usage(self):
    pass

  def init_args(self):
    self.option_parser.add_option('--feed', dest='feed',
                                  help='Name of feed to subscribe: facebook')

  def main(self):
    # Send subscription request
    subscription = {'object': 'user',
                    'fields': 'feed',
                    'callback_url': CALLBACK_URL,
                    'verify_token': verify_token}

    data = urlencode(subscription)
    url = URL % APP_AUTH

    try:
      response = urlopen(url, data)
      self.log.info(response.info())
      self.log.info(json.loads(response.read()))
    except HTTPError, e:
      self.log.error("code = %d, body=%s", e.code, e.read())
    except URLError, e:
      self.log.error("Failed to reach the server: %s", e.reason)

if __name__ == "__main__":
  # Initialize with number of arguments script takes
  exit(Subscriber(0).main())
