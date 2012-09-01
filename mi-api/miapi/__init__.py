import logging
import urlparse
import datetime

import zope.interface
import pyramid.config
import pyramid.authentication
import pyramid.authorization
import pyramid.security
import pyramid.interfaces

import tim_commons.config
import tim_commons.db
import data_access.service
import data_access.post_type

import resource
import error
import controllers.login
import controllers.author
import controllers.author_reservation
import controllers.author_query
import controllers.author_photoalbum
import controllers.author_photos
import controllers.author_service
import controllers.author_group
import controllers.author_group_query
import controllers.feature
import controllers.services
import controllers.author_service_profile
import controllers.author_service_query
import controllers.author_feature
import controllers.status


# dictionary that holds all configuration merged from multiple sources
tim_config = {}


# object created from JSON file that stores oAuth configuration for social services
oauth_config = {}

# "origin" hosts that are allowed to call the API
_acceptable_host = ['localhost']


def main(global_config, **settings):
  global tim_config
  tim_config = tim_commons.config.load_configuration('{TIM_CONFIG}/config.ini')

  db_url = tim_commons.db.create_url_from_config(tim_config['db'])
  logging.info('Creating DB session to: %s', db_url)
  tim_commons.db.configure_session(db_url)

  global oauth_config
  oauth_config = tim_config['oauth']

  global _acceptable_host
  _acceptable_host = tim_config['api']['cors_whitelist']

  data_access.service.initialize()
  data_access.post_type.initialize()

  configuration = pyramid.config.Configurator(
      root_factory=resource.root_factory,
      settings=settings)
  authentication = AuthenticationPolicy(
      tim_config['api']['authentication_secret'],
      callback=controllers.login.authenticate_user)
  configuration.set_authentication_policy(authentication)
  configuration.set_authorization_policy(pyramid.authorization.ACLAuthorizationPolicy())

  configuration.add_renderer('jsonp', pyramid.renderers.JSONP(param_name='callback'))

  configuration.add_static_view(name='img', path='miapi:img', cache_max_age=3600)

  # configure not found for option
  configuration.add_notfound_view(
      view=preflight_crossdomain_access_control,
      request_method='OPTIONS',
      renderer='jsonp')
  configuration.add_notfound_view(not_found, renderer='jsonp')

  # decorate cross domain calls
  configuration.add_subscriber(crossdomain_access_control_response, pyramid.events.NewResponse)
  add_views(configuration)

  return configuration.make_wsgi_app()


def add_views(configuration):
  controllers.status.add_views(configuration)

  controllers.login.add_views(configuration)

  controllers.author.add_views(configuration)
  controllers.author_reservation.add_views(configuration)
  controllers.author_query.add_views(configuration)
  controllers.author_photoalbum.add_views(configuration)
  controllers.author_photos.add_views(configuration)
  controllers.author_service.add_views(configuration)
  controllers.author_group.add_views(configuration)
  controllers.author_group_query.add_views(configuration)
  controllers.author_service_profile.add_views(configuration)
  controllers.author_service_query.add_views(configuration)
  controllers.author_feature.add_views(configuration)

  controllers.services.add_views(configuration)
  controllers.feature.add_views(configuration)

  configuration.add_view(
      unauthorized_request_to_self,
      context=resource.V1Root,
      name='self',
      renderer='jsonp')


def preflight_crossdomain_access_control(request):
  origin = request.headers.get('Origin')
  if origin is not None:
    request.response.headers['Access-Control-Allow-Origin'] = origin
    request.response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
    request.response.headers['Access-Control-Max-Age'] = tim_config['api']['cors_ttl']
    request.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    # parse the origin url
    origin_url = urlparse.urlparse(origin)
    origin_domain = origin_url.netloc.split(':')[0]

    if origin_domain in _acceptable_host:
      request.response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
      logging.info(
          'Not allowing domain (%s) because (%s) not in %s',
          origin,
          origin_domain,
          _acceptable_host)
      request.response.headers['Access-Control-Allow-Credentials'] = 'false'

    return request.response

  return error.http_error(request.response, **error.NOT_FOUND)


def not_found(request):
  return error.http_error(request.response, **error.NOT_FOUND)


def unauthorized_request_to_self(request):
  return error.http_error(request.response, **error.UNAUTHORIZED)


def crossdomain_access_control_response(event):
  request = event.request
  origin = request.headers.get('Origin')
  if origin:
    request.response.headers['Access-Control-Allow-Origin'] = origin
    request.response.headers['Access-Control-Max-Age'] = tim_config['api']['cors_ttl']

    # parse the origin url
    origin_url = urlparse.urlparse(origin)
    origin_domain = origin_url.netloc.split(':')[0]

    if origin_domain in _acceptable_host:
      request.response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
      logging.info(
          'Not allowing domain (%s) because (%s) not in %s',
          origin,
          origin_domain,
          _acceptable_host)
      request.response.headers['Access-Control-Allow-Credentials'] = 'false'

  return request.response


@zope.interface.implementer(pyramid.interfaces.IAuthenticationPolicy)
class AuthenticationPolicy(pyramid.authentication.AuthTktAuthenticationPolicy):
  def __init__(
      self,
      secret,
      callback=None,
      cookie_name='auth_tkt',
      secure=False,
      include_ip=False,
      timeout=None,
      reissue_time=None,
      max_age=None,
      path="/",
      http_only=False,
      wild_domain=True,
      debug=False):
    self.cookie = AuthTktCookieHelper(
        secret,
        cookie_name=cookie_name,
        secure=secure,
        include_ip=include_ip,
        timeout=timeout,
        reissue_time=reissue_time,
        max_age=max_age,
        http_only=http_only,
        path=path,
        wild_domain=wild_domain)
    self.callback = callback
    self.debug = debug


class AuthTktCookieHelper(pyramid.authentication.AuthTktCookieHelper):
  def _get_cookies(self, environ, value, max_age=None):
    cookies = super(AuthTktCookieHelper, self)._get_cookies(environ, value, max_age)

    if max_age is pyramid.authentication.EXPIRE:
        max_age = "; Max-Age=0; Expires=Wed, 31-Dec-97 23:59:59 GMT"
    elif max_age is not None:
        later = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(max_age))
        # Wdy, DD-Mon-YY HH:MM:SS GMT
        expires = later.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # the Expires header is *required* at least for IE7 (IE7 does
        # not respect Max-Age)
        max_age = "; Max-Age=%s; Expires=%s" % (max_age, expires)
    else:
        max_age = ''

    cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
    if ':' in cur_domain:
      cur_domain = cur_domain.split(':', 1)[0]

    if self.wild_domain:
      if '.' in cur_domain:
        top_domain = cur_domain.split('.')[1:]
        print top_domain, cur_domain
        if len(top_domain) > 1:
          cur_domain = '.'.join(top_domain)
        else:
          cur_domain = top_domain[0]

        wild_domain = '.' + cur_domain
        print wild_domain
        cookies.append(('Set-Cookie', '%s="%s"; Path=%s; Domain=%s%s%s' % (
                self.cookie_name, value, self.path, wild_domain, max_age,
                self.static_flags)))

    return cookies


'''
  #
  # AUTHOR MODEL: rebuild/update the data for all the author's services
  #
  config.add_route('author.model.build', '/v1/authors/{authorname}/build')
  config.add_route('author.model.update', '/v1/authors/{authorname}/update')

  #
  # AUTHOR QUERY: query for the highlights/details for a particular author
  #
  config.add_route('author.query.highlights', '/v1/authors/{authorname}/highlights')

  #
  # AUTHOR SERVICE QUERY: query for the highlights/details of the specified service and author
  #
  config.add_route('author.services.query.highlights', '/v1/authors/{authorname}/services/{servicename}/highlights')
'''
