import logging

import pyramid.config
import pyramid.authentication
import pyramid.authorization

import tim_commons.config
import tim_commons.db
import data_access.service
import data_access.post_type

import miapi.resource
import miapi.controllers.login
import miapi.controllers.author
import miapi.controllers.author_reservation
import miapi.controllers.author_query
import miapi.controllers.author_photoalbum
import miapi.controllers.author_photos
import miapi.controllers.author_service
import miapi.controllers.author_feature


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
      root_factory=miapi.resource.root_factory,
      settings=settings)
  # TODO: secret should be configurable
  authentication = pyramid.authentication.AuthTktAuthenticationPolicy(
      'secret',
      callback=miapi.controllers.login.authenticate_user,
      wild_domain=False)
  configuration.set_authentication_policy(authentication)
  configuration.set_authorization_policy(pyramid.authorization.ACLAuthorizationPolicy())
  # Require that every view specify a permission by setting the default to some random string
  configuration.set_default_permission('some_random_string')  # TODO: make this really random

  configuration.add_renderer('jsonp', pyramid.renderers.JSONP(param_name='callback'))

  configuration.add_static_view(name='img', path='miapi:img', cache_max_age=3600)

  add_views(configuration)

  return configuration.make_wsgi_app()

  # TODO: add status view: config.add_route('status', '/v1/status')
  # TODO: do someething about the about template...
  #       config.add_route('home', '/')
  #       config.add_view('miapi.controllers.about.about',
  #                       route_name='home',
  #                       renderer='templates/about.pt')


def add_views(configuration):
  miapi.controllers.login.add_views(configuration)
  miapi.controllers.author.add_views(configuration)
  miapi.controllers.author_reservation.add_views(configuration)
  miapi.controllers.author_query.add_views(configuration)
  miapi.controllers.author_photoalbum.add_views(configuration)
  miapi.controllers.author_photos.add_views(configuration)
  miapi.controllers.author_service.add_views(configuration)
  miapi.controllers.author_feature.add_views(configuration)


'''
  # TODO: We can never have an author with name search. Are we suing this? Can we add this later?
  # --
  # SEARCH for matching authors; JSON list of 0 or more authors returned.
  #  Query args: name
  #
  config.add_route('search.author', '/v1/authors/search')

  #
  # AUTHOR PROFILE: profile information for the specified author
  #
  config.add_route('author.profile.CRUD', '/v1/authors/{authorname}/profile')

  # TODO: Are we using this?
  #
  # AUTHOR METRICS: collected from users browsing an author's model
  #
  config.add_route('author.metrics.visitor.CRUD', '/v1/authors/{authorname}/metrics/visitor/{visitorID}')

  # TODO: What is this?
  #
  # AUTHOR MODEL: rebuild/update the data for all the author's services
  #
  config.add_route('author.model.build', '/v1/authors/{authorname}/build')
  config.add_route('author.model.update', '/v1/authors/{authorname}/update')

  #
  # AUTHOR QUERY: query for the highlights/details for a particular author
  #
  config.add_route('author.query.highlights', '/v1/authors/{authorname}/highlights')

  # TODO: Implememnting group is not an immidiate need. We should remove this urls
  # --
  # AUTHOR GROUP BASIC:
  #
  # GET - list of groups defined for the author
  config.add_route('author.groups', '/v1/authors/{authorname}/groups')

  # GET - get group definition; PUT - create/update group info; DELETE - delete the group
  config.add_route('author.groups.CRUD', '/v1/authors/{authorname}/groups/{groupname}')

  # GET - list of members in specified group
  config.add_route('author.groups.members', '/v1/authors/{authorname}/groups/{groupname}/members')

  # GET - get info about the member; PUT - add new member; DELETE - remove member
  config.add_route('author.groups.members.CRUD', '/v1/authors/{authorname}/groups/{groupname}/members/{member}')

  #
  # AUTHOR GROUP QUERY: query for the highlights/details for a particular group (i.e. following)
  #
  config.add_route('author.groups.query.highlights', '/v1/authors/{authorname}/groups/{groupname}/highlights')
  config.add_route('author.groups.query.events', '/v1/authors/{authorname}/groups/{groupname}/events')

  #
  # AUTHOR SERVICE QUERY: query for the highlights/details of the specified service and author
  #
  config.add_route('author.services.query.highlights', '/v1/authors/{authorname}/services/{servicename}/highlights')
  config.add_route('author.services.query.events', '/v1/authors/{authorname}/services/{servicename}/events')

  #
  # AUTHOR SERVICE PROFILE: get profile information from the specified service
  #
  config.add_route('author.services.profile', '/v1/authors/{authorname}/services/{servicename}/profile')

  #
  # SERVICE functionality
  #
  config.add_route('services', '/v1/services')
  config.add_route('services.CRUD', '/v1/services/{servicename}')

  #
  # FEATURE functionality
  #
  config.add_route('features', '/v1/features')
  config.add_route('feature.CRUD', '/v1/features/{featurename}')
  # TODO: What is bundle?
  config.add_route('feature.bundle', '/v1/features/{featurename}/bundle')

  # --
  # AUTHOR FEATURE: list features, add/remove features
  #

  # TODO: what is this and why do we need this?
  # resources for controlling an author's default features
  config.add_route('author.features.default', '/v1/authors/{authorname}/features/default')
  config.add_route('author.features.default.CRUD', '/v1/authors/{authorname}/features/default/{featurename}')

  # resources for listing, adding, and removing an author's features
  config.add_route('author.features', '/v1/authors/{authorname}/features')
  config.add_route('author.features.CRUD', '/v1/authors/{authorname}/features/{featurename}')
'''
