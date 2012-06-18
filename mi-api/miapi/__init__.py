from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.renderers import JSONP

from tim_commons.oauth import load_oauth_config

from miapi.models import initialize_sql

# object created from JSON file that stores oAuth configuration for social services
oAuthConfig = {}


def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """

  """ Setup the database
  """
  engine = engine_from_config(settings, 'sqlalchemy.')
  initialize_sql(engine)

  # load the oauth configuration settings
  global oAuthConfig
  oAuthConfig = load_oauth_config(settings['mi.oauthkey_file'])

  config = Configurator(settings=settings)

  config.add_renderer('jsonp', JSONP(param_name='callback'))

  config.add_static_view(name='img', path='miapi:img', cache_max_age=3600)

  # setup route and view for home page
  config.add_route('home', '/')
  config.add_view('miapi.controllers.about.about',
                  route_name='home',
                  renderer='templates/about.pt')
  config.add_route('status', '/v1/status')

  #
  # check author name availablility
  #

  # --
  # SEARCH for matching authors; JSON list of 0 or more authors returned.
  #  Query args: name
  #
  config.add_route('search.author', '/v1/authors/search')

  #
  # Return list of all authors
  #
  config.add_route('authors', '/v1/authors')

  # --
  # AUTHOR BASIC functionality
  #
  #  GET info, PUT new, PUT existing, DELETE existing
  #
  config.add_route('author.CRUD', '/v1/authors/{authorname}')

  #
  # AUTHOR PROFILE: profile information for the specified author
  #
  config.add_route('author.profile.CRUD', '/v1/authors/{authorname}/profile')

  #
  # AUTHOR METRICS: collected from users browsing an author's model
  #
  config.add_route('author.metrics.visitor.CRUD', '/v1/authors/{authorname}/metrics/visitor/{visitorID}')

  #
  # AUTHOR MODEL: rebuild/update the data for all the author's services
  #
  config.add_route('author.model.build', '/v1/authors/{authorname}/build')
  config.add_route('author.model.update', '/v1/authors/{authorname}/update')

  #
  # AUTHOR QUERY: query for the highlights/details for a particular author
  #
  config.add_route('author.query.highlights', '/v1/authors/{authorname}/highlights')
  config.add_route('author.query.events', '/v1/authors/{authorname}/events')
  config.add_route('author.query.events.eventId', '/v1/authors/{authorname}/events/{eventID}')
  config.add_route('author.query.topstories', '/v1/authors/{authorname}/topstories')

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

  # --
  # AUTHOR SERVICE: list services, add/remove services
  #
  config.add_route('author.services', '/v1/authors/{authorname}/services')
  config.add_route('author.services.CRUD', '/v1/authors/{authorname}/services/{servicename}')

  #
  # AUTHOR SERVICE MODEL: rebuild/update the data for the specified service
  #
  config.add_route('author.services.build', '/v1/authors/{authorname}/services/{servicename}/build')
  config.add_route('author.services.update', '/v1/authors/{authorname}/services/{servicename}/update')

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
  # AUTHOR PHOTO ALBUMS: get the list of photo albums for the user
  #
  config.add_route('author.photoalbums.CRUD', '/v1/authors/{authorname}/photoalbums')

  #
  # AUTHOR PHOTO ALBUMS: get the list of photo albums for the user
  #
  config.add_route('author.photoalbums.photos.CRUD', '/v1/authors/{authorname}/photoalbums/{albumname}/photos')


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
  config.add_route('feature.bundle', '/v1/features/{featurename}/bundle')

  # --
  # AUTHOR FEATURE: list features, add/remove features
  #

  # resources for controlling an author's default features
  config.add_route('author.features.default', '/v1/authors/{authorname}/features/default')
  config.add_route('author.features.default.CRUD', '/v1/authors/{authorname}/features/default/{featurename}')

  # resources for listing, adding, and removing an author's features
  config.add_route('author.features', '/v1/authors/{authorname}/features')
  config.add_route('author.features.CRUD', '/v1/authors/{authorname}/features/{featurename}')

  config.scan('miapi')

  return config.make_wsgi_app()
