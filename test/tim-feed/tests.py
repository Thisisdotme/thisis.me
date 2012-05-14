import unittest

from pyramid import testing
from webob.multidict import MultiDict

import tim_commons.mock
from feed.views import get_facebook_feed, post_facebook_feed, convert_facebook_notification
from tim_commons.config import ENVIRONMENT_KEY


class FacebookFeedHTTPTestCase(unittest.TestCase):
  verify_token = 'secret_token'

  def setUp(self):
    self.config = testing.setUp()

  def tearDown(self):
    testing.tearDown()

  def _create_multidict(self):
    result = MultiDict()
    result.add('hub.mode', 'subscribe')
    result.add('hub.challenge', 'secret')
    result.add('hub.verify_token', self.verify_token)

    return result

  def test_subscription_verification(self):
    request = testing.DummyRequest()
    request.registry.settings[ENVIRONMENT_KEY] = {'feed': {'verify_token': self.verify_token}}

    request.GET = self._create_multidict()

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 200)
    self.assertEqual(result.body, 'secret')

  def test_incorrect_mode(self):
    request = testing.DummyRequest()
    request.registry.settings[ENVIRONMENT_KEY] = {'feed': {'verify_token': self.verify_token}}

    request.GET = self._create_multidict()
    request.GET.pop('hub.mode')
    request.GET.add('hub.mode', 'incorrect')

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 404)

  def test_incorrect_token(self):
    request = testing.DummyRequest()
    request.registry.settings[ENVIRONMENT_KEY] = {'feed': {'verify_token': self.verify_token}}

    request.GET = self._create_multidict()
    request.GET.pop('hub.verify_token')
    request.GET.add('hub.verify_token', 'incorrect')

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 404)

  def test_post_json(self):
    request = testing.DummyRequest()
    request.registry.settings[ENVIRONMENT_KEY] = {'queues': {'facebook': {'notification': 'name'}}}

    request.message_client = tim_commons.mock.DummyMessageClient()
    request.headers['Content-Type'] = 'application/json'
    request.body = '''{"object": "user", "entry": [ { "uid": 1335845740,
"changed_fields": [ "name", "picture" ], "time": 232323 }, { "uid": 1234,
"changed_fields": [ "friends" ], "time": 232325 } ] }'''

    result = post_facebook_feed(request)

    self.assertEqual(result.status_int, 200)


class FacebookFeedInternalTestCase(unittest.TestCase):
  def test_convert_facebook_notification(self):
    notification = {"object": "user",
                    "entry": [{"uid": 1335845740,
                                 "changed_fields": ["name", "picture"],
                                 "time": 232323},
                               {"uid": 1234,
                                 "changed_fields": ["friends"],
                                 "time": 232325}]}

    notifications = convert_facebook_notification(notification)
    self.assertEquals(1335845740,
                      notifications[0]['message']['service_author_id'])
    self.assertEquals(1234,
                      notifications[1]['message']['service_author_id'])
    self.assertEquals(len(notifications), 2)
