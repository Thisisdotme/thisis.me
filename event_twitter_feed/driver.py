import sys
import oauth2 as oauth
import time
import urllib


from pprint import pformat
from StringIO import StringIO
from twisted.python.log import err
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.protocols.basic import LineReceiver
from twisted.web.client import Agent, FileBodyProducer
from twisted.web.http_headers import Headers
from twisted.enterprise import adbapi
from twisted_amqp import AmqpFactory

from tim_commons import app_base, json_serializer, messages

# TODO: remove this when confortable
#method = 'POST'
#url = 'http://requestb.in/13stbfk1'
#url = 'https://stream.twitter.com/1/statuses/filter.json'
#data = {'follow': 563165708}
#consumer_key = '2Ey4mYesvLGXEmhXgaWQpw'
#consumer_secret = '1coL8wYHbTc7PRNTuvkJblRF1vRgCb8U7x1jYg'
#token_key = '563165708-Vuhr6aILmWNyyyXxaVbTsbEP7bmvUTSt6aCrFdpc'
#token_secret = 'H3DVvEnvCHWF7PffZpVA9j0Xd5UNEmL0g81ZbARE'


class EventTwitterFeedDriver(app_base.AppBase):
  user_ids = set()

  def app_main(self, config, options, args):
    # TODO: deal with new user registrations by listening to amqp and schedule the rest

    # Configure amqp
    # TODO: grab this form the configuration file
    amqp_host = 'localhost'
    amqp_port = 5672
    amqp_spec = 'amqp0-9-1.xml'

    self.amqp = AmqpFactory(host=amqp_host, port=amqp_port, spec_file=amqp_spec)

    # TODO: grab this from the configuration file
    db_host = 'localhost'
    db_user = 'mi'
    db_passwd = 'mi'
    db_name = 'mi'

    db_pool = adbapi.ConnectionPool(
        'MySQLdb',
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        db=db_name,
        use_unicode=True,
        cp_noisy=True)
    self.process_twitter_users(db_pool)

    reactor.run()

  def handle_twitter_query_result(self, result_set):
    print 'Result:', result_set

    for twitter_user in result_set:
      # start a connection to twitter
      method = 'POST'
      url = 'https://stream.twitter.com/1/statuses/filter.json'
      user_id = twitter_user[2]
      tim_author_id = twitter_user[3]
      consumer_key = '2Ey4mYesvLGXEmhXgaWQpw'  # TODO: get this from config
      consumer_secret = '1coL8wYHbTc7PRNTuvkJblRF1vRgCb8U7x1jYg'  # TODO: get this from config
      token_key = twitter_user[0]
      token_secret = twitter_user[1]

      self.listen_to_twitter(
          method,
          url,
          user_id,
          tim_author_id,
          token_key,
          token_secret,
          consumer_key,
          consumer_secret)

  def listen_to_twitter(
      self,
      method,
      url,
      user_id,
      tim_author_id,
      token_key,
      token_secret,
      consumer_key,
      consumer_secret):

    if user_id not in self.user_ids:
      self.user_ids.add(user_id)

      data = {'follow': user_id}

      headers = sign_request(
          method=method,
          url=url,
          data=data,
          consumer_key=consumer_key,
          consumer_secret=consumer_secret,
          token_key=token_key,
          token_secret=token_secret)
      headers['Authorization'] = [headers['Authorization'].encode('ascii')]
      headers['Content-Type'] = ['application/x-www-form-urlencoded']

      body = FileBodyProducer(StringIO(urllib.urlencode(data)))

      contextFactory = WebClientContextFactory()
      agent = Agent(reactor, contextFactory)
      d = agent.request(
          method,
          url,
          Headers(headers),
          body)

      def handle_response(response):
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        print 'Response headers:'
        print pformat(list(response.headers.getAllRawHeaders()))

        response.deliverBody(TwitterStreamProtocol(tim_author_id, user_id, self))

      d.addCallback(handle_response)
      d.addErrback(err)

  def process_twitter_users(self, db_pool):
    twitter_service_id = 2  # TODO: would be nice to remove this
    deferred = db_pool.runQuery(
        '''SELECT access_token, access_token_secret, service_author_id, author_id
           FROM author_service_map
           WHERE service_id = %s''',
        (twitter_service_id,))
    deferred.addCallback(self.handle_twitter_query_result)
    deferred.addErrback(err)


class TwitterStreamProtocol(LineReceiver):
  def __init__(self, tim_author_id, service_author_id, factory):
    self.tim_author_id = tim_author_id
    self.service_author_id = service_author_id
    self.factory = factory

  def lineReceived(self, line):
    if line:
      json_dict = json_serializer.load_string(line)
      event_message = messages.create_event_message(
          'twitter',
          self.tim_author_id,
          messages.CURRENT_STATE,
          self.service_author_id,
          '00',  # TODO: service_event_id: interpret the raw event
          json_dict,
          [])
      self._send_message(event_message)
    else:
      print "Heartbeat!"

  def connectionLost(self, reason):
    # TODO: restart connection on error
    print 'Finished receiving body:', reason.getErrorMessage()

  def _send_message(self, message):
    try:  # TODO: remove this crap
      queue = message['header']['type']
      body = json_serializer.dump_string(message)
      self.factory.amqp.send_message(exchange='', routing_key=queue, msg=body)
    except:
      from twisted.python import log
      log.err()


class WebClientContextFactory(ClientContextFactory):
  def getContext(self, hostname, port):
    return ClientContextFactory.getContext(self)


def sign_request(method, url, consumer_key, consumer_secret, token_key, token_secret, data):
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

'''
def listen_to_twitter():
  header = sign_request(
      method=method,
      url=url,
      data=data,
      consumer_key=consumer_key,
      consumer_secret=consumer_secret,
      token_key=token_key,
      token_secret=token_secret)

  response = requests.post(url,
                           data=data,
                           headers=header)
  print response.request.headers

  print response.status_code
  for line in response.iter_lines(chunk_size=1):
    if line:
      print json_serializer.load_string(line)
    else:
      print 'Heartbeat!'
'''


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventTwitterFeedDriver('event_collector', daemon_able=True).main())
