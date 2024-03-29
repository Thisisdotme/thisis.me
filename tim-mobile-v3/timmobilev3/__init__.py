from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

import pyramid_beaker

from tim_commons import db
from tim_commons.config import load_configuration

# dictionary that holds all configuration merged from multple sources
tim_config = {}

# object created from JSON file that stores oAuth configuration for social services
oauth_config = {}


def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """

  """ Setup the config
  """
  global tim_config
  tim_config = load_configuration('{TIM_CONFIG}/config.ini')

  # TODO: THIS NEEDS TO EVENTUALL BE REMOVED
  if 'api.endpoint' in settings:
    tim_config['api']['endpoint'] = settings['api.endpoint']

  """ Setup the database
  """
  db_url = db.create_url_from_config(tim_config['db'])
  db.configure_session(db_url)

  session_factory = pyramid_beaker.session_factory_from_settings(settings)

  authn_policy = AuthTktAuthenticationPolicy(tim_config['api']['authentication_secret'])
  authz_policy = ACLAuthorizationPolicy()

  config = Configurator(settings=settings,
                        authentication_policy=authn_policy,
                        authorization_policy=authz_policy,
                        session_factory=session_factory)

  config.add_static_view('img', 'timmobilev3:img', cache_max_age=0)
  config.add_static_view('css', 'timmobilev3:css', cache_max_age=0)
  config.add_static_view('js', 'timmobilev3:js', cache_max_age=0)

  config.add_route('index', '/')
  config.add_route('settings', '/settings')
  config.add_route('login', '/login')
  # config.add_route('app', '/{authorname}/')
  config.add_route('app', '/{authorname}')

  # twitter oauth
  config.add_route('twitter', '/oauth/twitter')
  config.add_route('twitter_callback', '/oauth/twitter/callback')

  # facebook auth
  config.add_route('facebook', '/oauth/facebook')
  config.add_route('facebook_callback', '/oauth/facebook/callback')

  # linkedin auth
  config.add_route('linkedin', '/oauth/linkedin')
  config.add_route('linkedin_callback', '/oauth/linkedin/callback')

  # google+ auth
  config.add_route('googleplus', '/oauth/googleplus')
  config.add_route('googleplus_callback', '/oauth/googleplus/callback')

  # instagram auth
  config.add_route('instagram', '/oauth/instagram')
  config.add_route('instagram_callback', '/oauth/instagram/callback')

  # flickr auth
  config.add_route('flickr', '/oauth/flickr')
  config.add_route('flickr_callback', '/oauth/flickr/callback')

  # foursquare auth
  config.add_route('foursquare', '/oauth/foursquare')
  config.add_route('foursquare_callback', '/oauth/foursquare/callback')

  # generic oauth
  config.add_route('oauth', '/oauth/{servicename}')
  config.add_route('oauth_callback', '/oauth/{servicename}/callback')

  config.add_route('resource.any', '/{authorname}/asset/{resource}.{ext}')

  config.scan()

  return config.make_wsgi_app()
