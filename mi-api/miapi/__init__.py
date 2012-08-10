import logging
import urlparse

import pyramid.config
import pyramid.authentication
import pyramid.authorization
import pyramid.security

import tim_commons.config
import tim_commons.db
import data_access.service
import data_access.post_type

import resource
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


# dictionary that holds all configuration merged from multple sources
tim_config = {}


# object created from JSON file that stores oAuth configuration for social services
oauth_config = {}


def main(global_config, **settings):
  global tim_config
  tim_config = tim_commons.config.load_configuration('{TIM_CONFIG}/config.ini')

  db_url = tim_commons.db.create_url_from_config(tim_config['db'])
  logging.info('Creating DB session to: %s', db_url)
  tim_commons.db.configure_session(db_url)

  global oauth_config
  oauth_config = tim_config['oauth']

  data_access.service.initialize()
  data_access.post_type.initialize()

  configuration = pyramid.config.Configurator(
      root_factory=resource.root_factory,
      settings=settings)
  authentication = pyramid.authentication.AuthTktAuthenticationPolicy(
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

  # TODO: add status view: config.add_route('status', '/v1/status')
  # TODO: do someething about the about template...
  #       config.add_route('home', '/')
  #       config.add_view('miapi.controllers.about.about',
  #                       route_name='home',
  #                       renderer='templates/about.pt')


def add_views(configuration):
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

  controllers.services.add_views(configuration)
  controllers.feature.add_views(configuration)


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

  # TODO: better error
  request.response = pyramid.httpexceptions.HTTPNotFound()
  return {'error': 'not found'}


def not_found(request):
  # TODO: better error
  request.response = pyramid.httpexceptions.HTTPNotFound()
  return {'error': 'not found'}


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


# call with credential. only allow *.host to call it
# TODO: move this config
_acceptable_host = ['localhost', 'mvp2.thisis.me', 'mvp3.thisis.me', 'www.thisis.me', 'blog.thisis.me']


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
