from pyramid.config import Configurator

from pyramid.renderers import JSONP

from tim_commons.config import load_configuration
from tim_commons import db

from mi_schema import models
import data_access.service


# dictionary that holds all configuration merged from multple sources
tim_config = {}

# object created from JSON file that stores oAuth configuration for social services
oauth_config = {}

# lookup dictionary of service_object_type id to it's associated label
service_object_type_dict = {}


# create and return a service_object_type dictionary
def load_service_object_type_dict():

  service_object_type_dict = {}

  db_session = db.Session()

  for row in db_session.query(models.ServiceObjectType):
    service_object_type_dict[row.type_id] = row.label

  return service_object_type_dict


def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """

  """ Setup the config
  """
  global tim_config
  tim_config = load_configuration('{TIM_CONFIG}/config.ini')

  """ Setup the database
  """
  db_url = tim_config['db']['sqlalchemy.url']
  db.configure_session(db_url)

  # load the oauth configuration settings
  global oauth_config
  oauth_config = tim_config['oauth']

  # load the service_object_type_dict dictionary
  global service_object_type_dict
  service_object_type_dict = load_service_object_type_dict()

  data_access.service.initialize()

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
  # Author reservation functionality
  #
  config.add_route('author.reservation', '/v1/reservation/{authorname}')

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
  config.add_route('author.photoalbums.photos.CRUD', '/v1/authors/{authorname}/photoalbums/{albumID}/photos')

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
