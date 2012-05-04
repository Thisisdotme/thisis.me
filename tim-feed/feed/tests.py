import unittest
import mock

from pyramid import testing
from webob.multidict import MultiDict
from feed.views import (get_facebook_feed, post_facebook_feed, verify_token,
                        convert_facebook_notification)

class FacebookFeedHTTPTestCase(unittest.TestCase):
  def setUp(self):
    self.config = testing.setUp()

  def tearDown(self):
    testing.tearDown()

  def _create_multidict(self):
    result =  MultiDict()
    result.add('hub.mode', 'subscribe')
    result.add('hub.challenge', 'secret')
    result.add('hub.verify_token', verify_token)

    return result

  def test_subscription_verification(self):
    request = testing.DummyRequest()
    request.GET = self._create_multidict()

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 200)
    self.assertEqual(result.body, 'secret')

  def test_incorrect_mode(self):
    request = testing.DummyRequest()
    request.GET = self._create_multidict()
    request.GET.pop('hub.mode')
    request.GET.add('hub.mode', 'incorrect')

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 404)

  def test_incorrect_token(self):
    request = testing.DummyRequest()
    request.GET = self._create_multidict()
    request.GET.pop('hub.verify_token')
    request.GET.add('hub.verify_token', 'incorrect')

    result = get_facebook_feed(request)

    self.assertEqual(result.status_int, 404)

  def test_post_json(self):
    request = testing.DummyRequest()
    request.message_client = mock.MessageClient()
    request.headers['Content-Type'] = 'application/json'
    request.body = '''{"object": "user", "entry": [ { "uid": 1335845740, 
"changed_fields": [ "name", "picture" ], "time": 232323 }, { "uid": 1234,
"changed_fields": [ "friends" ], "time": 232325 } ] }'''

    result = post_facebook_feed(request)

    self.assertEqual(result.status_int, 200)

class FacebookFeedInternalTestCase(unittest.TestCase):
  def test_convert_facebook_notification(self):
    notification = {"object": "user",
                    "entry": [ { "uid": 1335845740,
                                 "changed_fields": [ "name", "picture" ],
                                 "time": 232323 },
                               { "uid": 1234,
                                 "changed_fields": [ "friends" ],
                                 "time": 232325 } ] }

    id = convert_facebook_notification(notification)
    self.assertTrue(1335845740 in id)
    self.assertTrue(1234 in id)
