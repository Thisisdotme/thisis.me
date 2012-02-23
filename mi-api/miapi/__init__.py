from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.renderers import JSONP

from mi_utils.oauth import load_oauth_config

from miapi.models import initialize_sql

# object created from JSON file that stores oAuth configuration for social features
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
  config.add_view('miapi.views.about.about',
                  route_name='home',
                  renderer='templates/about.pt')
#
# check author name availablility
#

  config.add_route('status','/v1/status')
  
  # --
  # SEARCH for matching authors; JSON list of 0 or more authors returned.
  #  Query args: name
  # 
  config.add_route('search.author','/v1/search/authors')

  #
  # Return list of all authors
  #
  config.add_route('authors','/v1/authors')

  # --
  # AUTHOR BASIC functionality
  #
  #  GET info, PUT new, DELETE existing
  #
  config.add_route('author.CRUD','/v1/authors/{authorname}')
  
  #
  # AUTHOR PROFILE: profile information for the specified author
  #
  config.add_route('author.profile.CRUD','/v1/authors/{authorname}/profile')

  #
  # AUTHOR METRICS: collected from users browsing an author's model
  #
  config.add_route('author.metrics.visitor.CRUD','/v1/authors/{authorname}/metrics/visitor/{visitorID}')

  #
  # AUTHOR MODEL: rebuild/update the data for all the author's features
  #
  config.add_route('author.model.build','/v1/authors/{authorname}/build')
  config.add_route('author.model.update','/v1/authors/{authorname}/update')
  
  #
  # AUTHOR QUERY: query for the highlights/details for a particular author
  #
  config.add_route('author.query.highlights','/v1/authors/{authorname}/highlights')
  config.add_route('author.query.events','/v1/authors/{authorname}/events')
  config.add_route('author.query.events.eventId','/v1/authors/{authorname}/events/{eventID}')
  
  config.add_route('author.featureEvents','/v1/authors/{authorname}/featureEvents') # deprecated
  config.add_route('author.featureEvents.featureEvent','/v1/authors/{authorname}/featureEvents/{eventID}') # deprecated


  # --
  # AUTHOR GROUP BASIC: 
  #
  # GET - list of groups defined for the author
  config.add_route('author.groups','/v1/authors/{authorname}/groups')
  
  # GET - get group definition; PUT - create/update group info; DELETE - delete the group
  config.add_route('author.groups.CRUD','/v1/authors/{authorname}/groups/{groupname}')

  # GET - list of members in specified group
  config.add_route('author.groups.members','/v1/authors/{authorname}/groups/{groupname}/members')
  
  # GET - get info about the member; PUT - add new member; DELETE - remove member 
  config.add_route('author.groups.members.CRUD','/v1/authors/{authorname}/groups/{groupname}/members/{member}')
  
  #
  # AUTHOR GROUP QUERY: query for the highlights/details for a particular group (i.e. following)
  #
  config.add_route('author.groups.query.highlights','/v1/authors/{authorname}/groups/{groupname}/highlights')
  config.add_route('author.groups.query.events','/v1/authors/{authorname}/groups/{groupname}/events')


  # --
  # AUTHOR FEATURE: list features, add/remove features
  #
  config.add_route('author.features','/v1/authors/{authorname}/features')
  config.add_route('author.features.CRUD','/v1/authors/{authorname}/features/{featurename}')

  #
  # AUTHOR FEATURE MODEL: rebuild/update the data for the specified feature
  #
  config.add_route('author.features.build','/v1/authors/{authorname}/features/{featurename}/build')
  config.add_route('author.features.update','/v1/authors/{authorname}/features/{featurename}/update')

  #
  # AUTHOR FEATURE QUERY: query for the highlights/details of the specified feature and author
  #
  config.add_route('author.features.query.highlights','/v1/authors/{authorname}/features/{featurename}/highlights')
  config.add_route('author.features.query.events','/v1/authors/{authorname}/features/{featurename}/events')

### PICK UP HERE

  config.add_route('author.features.featureEvents','/v1/authors/{authorname}/features/{featurename}/featureEvents') # deprecated

  #
  # AUTHOR FEATURE PROFILE: get profile information from the specified feature
  #
  config.add_route('author.features.profile','/v1/authors/{authorname}/features/{featurename}/profile')
  
  #
  # AUTHOR MISC
  #
  config.add_route('author.featureEvents.featureEvent.read.user.CRUD','/v1/authors/{authorname}/featureEvents/{featureEventID}/read/{userID}')
  
  #
  # FEATURE functionality
  #
  config.add_route('features','/v1/features')
  config.add_route('feature.CRUD','/v1/features/{featurename}')
  config.add_route('feature.bundle','/v1/features/{featurename}/bundle')
  
  config.scan('miapi')

  return config.make_wsgi_app()
  
