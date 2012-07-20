import sys
import oauth2 as oauth
import time
import urllib
import datetime
import logging


from StringIO import StringIO
from twisted.python.log import err, PythonLoggingObserver
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.protocols.basic import LineReceiver
from twisted.web.client import Agent, FileBodyProducer
from twisted.web.http_headers import Headers
from twisted.enterprise import adbapi
from twisted_amqp import AmqpFactory

from tim_commons import app_base, json_serializer, messages, message_queue
from mi_schema import models
import event_interpreter


class EventTwitterFeedDriver(app_base.AppBase):
  user_ids = set()

  def app_main(self, config, options, args):
    # TODO: deal with new user registrations by listening to amqp and schedule the rest

    observer = PythonLoggingObserver()
    observer.start()

    # Grab twitter consumer keys
    self.consumer_key = config['oauth']['twitter']['key']
    self.consumer_secret = config['oauth']['twitter']['secret']
    self.default_token_key = config['oauth']['twitter']['default_access_token']
    self.default_token_secret = config['oauth']['twitter']['default_access_token_secret']

    # Grab feed configuration
    self.wait_on_collector_query_delay = float(config['feed']['wait_on_collector_query_delay'])

    # Configure amqp
    amqp_host = config['broker']['host']
    amqp_port = int(config['broker']['port'])
    amqp_spec = message_queue.create_spec_path(config['broker']['spec'])

    self.amqp = AmqpFactory(host=amqp_host, port=amqp_port, spec_file=amqp_spec)

    db_host = config['db']['host']
    db_user = config['db']['user']
    db_passwd = config['db']['password']
    db_database = config['db']['database']
    db_unicode = bool(config['db']['unicode'])

    self.db_pool = adbapi.ConnectionPool(
        'MySQLdb',
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        db=db_database,
        use_unicode=db_unicode,
        cp_noisy=True)
    self._process_twitter_users()

    reactor.run()

  def _handle_twitter_query_result(self, result_set):
    users_without_oauth = []
    for twitter_user in result_set:
      # start a connection to twitter
      asm = _create_author_service_map(twitter_user)

      if (asm.access_token and
          asm.access_token_secret):
        self._handle_users(asm.access_token, asm.access_token_secret, [asm])
      else:
        users_without_oauth.append(asm)

    self._handle_users(self.default_token_key, self.default_token_secret, users_without_oauth)

  def _handle_users(self, token_key, token_secret, author_service_maps):
    handlers = []
    for asm in author_service_maps:
      if (asm.service_author_id not in self.user_ids):
        self.user_ids.add(asm.service_author_id)
        handler = TwitterHandler(asm, self)
        handlers.append(handler)

    group_handler = GroupTwitterHandler(handlers, self)

    self._listen_to_twitter(token_key, token_secret, group_handler)

    for handler in handlers:
      self._notify_event_collector(handler.author_service_map)
      handler.schedule_collector_done()

  def _notify_event_collector(self, asm):
    notification = messages.create_notification_message('twitter', asm.service_author_id)
    queue = notification['header']['type']
    body = json_serializer.dump_string(notification)
    self.amqp.send_message(exchange='', routing_key=queue, msg=body)

  def _listen_to_twitter(self, token_key, token_secret, handler):
    method = 'POST'
    url = 'https://stream.twitter.com/1/statuses/filter.json'
    data = {'follow': ','.join(handler.list_of_twitter_ids())}

    headers = _sign_request(
        method=method,
        url=url,
        data=data,
        consumer_key=self.consumer_key,
        consumer_secret=self.consumer_secret,
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
      if response.code == 200:
        logging.info('Starting to listen for stream from: %s', data)
        response.deliverBody(TwitterStreamProtocol(handler))
      else:
        logging.info(
            'Got a bad response: %s, phrase: %s, for: %s',
            response.code,
            response.phrase,
            data)

    d.addCallback(handle_response)
    d.addErrback(err)

  def _process_twitter_users(self):
    twitter_service_id = 2  # TODO: would be nice to remove this
    deferred = self.db_pool.runQuery(
        '''SELECT author_id, service_id, access_token, access_token_secret, service_author_id,
                  id, last_update_time, most_recent_event_id, most_recent_event_timestamp
           FROM author_service_map
           WHERE service_id = %s;''',
        (twitter_service_id,))
    deferred.addCallback(self._handle_twitter_query_result)
    deferred.addErrback(err)


class GroupTwitterHandler:
  def __init__(self, handlers, factory):
    self.handlers = handlers
    self.factory = factory

    self.id_to_handler = {}
    for handler in self.handlers:
      self.id_to_handler[handler.author_service_map.service_author_id] = handler

  def list_of_twitter_ids(self):
    return [handler.author_service_map.service_author_id for handler in self.handlers]

  def handle(self, tweet):
    interpreter = event_interpreter.create_event_interpreter(
        'twitter',
        tweet,
        None,
        None)

    service_author_id = interpreter.service_author_id()
    handler = self.id_to_handler.get(service_author_id, None)
    if handler:
      handler.handle(interpreter)
    else:
      logging.info('Skipping tweet by user %s because we do not have an author with that id',
                   service_author_id)


class TwitterHandler:
  def __init__(self, author_service_map, factory):
    self.author_service_map = author_service_map
    self.factory = factory
    self.write_date = False
    self.last_update_time = author_service_map.last_update_time
    self.most_recent_event_id = None
    self.most_recent_event_timestamp = None

  def handle(self, interpreted_tweet):
    event_message = messages.create_event_message(
        'twitter',
        self.author_service_map.author_id,
        messages.CURRENT_STATE,
        self.author_service_map.service_author_id,
        interpreted_tweet.event_id(),
        interpreted_tweet.json,
        [])
    self._send_message(event_message)

    if self.write_date:
      self._update_database(
          self.author_service_map.id,
          datetime.datetime.utcnow(),
          interpreted_tweet.event_id(),
          interpreted_tweet.created_time())
    else:
      self.last_update_time = datetime.datetime.utcnow()
      self.most_recent_event_id = interpreted_tweet.event_id()
      self.most_recent_event_timestamp = interpreted_tweet.created_time()

  def _send_message(self, message):
    queue = message['header']['type']
    body = json_serializer.dump_string(message)
    self.factory.amqp.send_message(exchange='', routing_key=queue, msg=body)

  def schedule_collector_done(self):
    def query_service_event_map_by_id():
      deferred = self.factory.db_pool.runQuery(
          '''SELECT author_id, service_id, access_token, access_token_secret, service_author_id,
                    id, last_update_time, most_recent_event_id, most_recent_event_timestamp
             FROM author_service_map
             WHERE id = %s''',
          (self.author_service_map.id,))
      deferred.addCallback(self._check_date_status)
      deferred.addErrback(err)

    reactor.callLater(self.factory.wait_on_collector_query_delay, query_service_event_map_by_id)

  def _check_date_status(self, result):
    # TODO: assert that there is at least one row
    asm = _create_author_service_map(result[0])
    if asm.last_update_time != self.author_service_map.last_update_time:
      self.write_date = True
      if (self.last_update_time and
          self.last_update_time > asm.last_update_time):
        self._update_database(
            asm.id,
            self.last_update_time,
            self.most_recent_event_id,
            self.most_recent_event_timestamp)
    else:
      self.schedule_collector_done()

  def _update_database(
      self,
      id,
      last_update_time,
      most_recent_event_id,
      most_recent_event_timestamp):
    deferred = self.factory.db_pool.runOperation(
        '''UPDATE author_service_map
           SET last_update_time=%s, most_recent_event_id=%s, most_recent_event_timestamp=%s
           WHERE id = %s''',
        (last_update_time, most_recent_event_id, most_recent_event_timestamp, id))
    deferred.addErrback(err)


class TwitterStreamProtocol(LineReceiver):
  def __init__(self, handler):
    self.handler = handler

  def lineReceived(self, line):
    if line:
      try:
        self.handler.handle(json_serializer.load_string(line))
      except:
        logging.exception('Error handling twitter event: %s', line)

  def connectionLost(self, reason):
    # TODO: restart connection on error
    logging.info('Finished receiving body: %s', reason.getErrorMessage())
    logging.info('Data: %s', self.handler.list_of_twitter_ids())
    logging.info(reason.getTraceback())


class WebClientContextFactory(ClientContextFactory):
  def getContext(self, hostname, port):
    return ClientContextFactory.getContext(self)


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


def _create_author_service_map(twitter_user):
  asm = models.AuthorServiceMap(
      twitter_user[0],
      twitter_user[1],
      twitter_user[2],
      twitter_user[3],
      twitter_user[4])
  asm.id = twitter_user[5]
  asm.last_update_time = twitter_user[6]
  asm.most_recent_event_id = twitter_user[7]
  asm.most_recent_event_timestamp = twitter_user[8]

  return asm


if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(EventTwitterFeedDriver('event_twitter_feed', daemon_able=True).main())
