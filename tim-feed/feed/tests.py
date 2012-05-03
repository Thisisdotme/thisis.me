import unittest

from pyramid import testing
from webob.multidict import MultiDict
from feed.views import FacebookFeed, verify_token

class FacebookFeedTestCase(unittest.TestCase):
  def setUp(self):
    self.config = testing.setUp()

  def tearDown(self):
    testing.tearDown()

  def __createMultiDict(self):
    result =  MultiDict()
    result.add('hub.mode', 'subscribe')
    result.add('hub.challenge', 'secret')
    result.add('hub.verify_token', verify_token)

    return result

  def test_subscriptionVerification(self):
    request = testing.DummyRequest()
    request.GET = self.__createMultiDict()

    feed = FacebookFeed(request)
    result = feed.get()

    self.assertEqual(result.status_int, 200)
    self.assertEqual(result.body, 'secret')

  def test_incorrectMode(self):
    request = testing.DummyRequest()
    request.GET = self.__createMultiDict()
    request.GET.pop('hub.mode')
    request.GET.add('hub.mode', 'incorrect')

    feed = FacebookFeed(request)
    result = feed.get()

    self.assertEqual(result.status_int, 404)

  def test_incorrectToken(self):
    request = testing.DummyRequest()
    request.GET = self.__createMultiDict()
    request.GET.pop('hub.verify_token')
    request.GET.add('hub.verify_token', 'incorrect')

    feed = FacebookFeed(request)
    result = feed.get()

    self.assertEqual(result.status_int, 404)

  def test_postJson(self):
    request = testing.DummyRequest()
    request.headers['Content-Type'] = 'application/json'
    request.body = '''{"object": "user", "entry": [ { "uid": 1335845740, 
"changed_fields": [ "name", "picture" ], "time": 232323 }, { "uid": 1234,
"changed_fields": [ "friends" ], "time": 232325 } ] }'''

    feed = FacebookFeed(request)
    result = feed.post()

    self.assertEqual(result.status_int, 200)
