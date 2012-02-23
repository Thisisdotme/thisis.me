
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

import pyramid_beaker

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from mi_utils.oauth import load_oauth_config

from timweb.models import initialize_sql
from timweb.security import groupfinder

# object created from JSON file that stores oAuth configuration for social features
oAuthConfig = None

def main(global_config, **settings):
  
  """ This function returns a Pyramid WSGI application.
  """
  
  # initial db setup and connection
  engine = engine_from_config(settings, 'sqlalchemy.')
  initialize_sql(engine)

  # load the oauth configuration settings
  global oAuthConfig
  oAuthConfig = load_oauth_config(settings['mi.oauthkey_file'])

  authn_policy = AuthTktAuthenticationPolicy('tim_secret', callback=groupfinder, timeout=1800, reissue_time=180, max_age=1800, debug=True)
  authz_policy = ACLAuthorizationPolicy()
  
  session_factory = pyramid_beaker.session_factory_from_settings(settings) 

  config = Configurator(settings=settings,
                        root_factory='timweb.context.RootFactory',
                        authentication_policy=authn_policy,
                        authorization_policy=authz_policy,
                        session_factory=session_factory)

  config.add_static_view('static', 'timweb:static', cache_max_age=None)
  config.add_static_view('img', 'timweb:img', cache_max_age=None)
  config.add_static_view('css', 'timweb:css', cache_max_age=None)
  config.add_static_view('js', 'timweb:js', cache_max_age=None)

  # define routes
  #
  config.add_route('login', '/login')
  config.add_route('logout', '/logout')

  config.add_route('home', '/')
  
  config.add_route('about', '/about.html')
  config.add_route('appinator', '/appinator.html')
  config.add_route('features', '/features.html')

  config.add_route('jquery', '/jquery.html')
  config.add_route('jquery_json','/jquery.json')

  config.add_route('supported_features', '/supported_features.html')

  # twitter auth
  config.add_route('twitter','/twitter.html')
  config.add_route('twitter_callback', '/twitter_callback')
  config.add_route('twitter_confirmation', '/twitter_confirmation.html')
  
  # instagram auth
  config.add_route('instagram','/instagram.html')
  config.add_route('instagram_callback', '/instagram_callback')
  config.add_route('instagram_confirmation', '/instagram_confirmation.html')

  # flickr auth
  config.add_route('flickr','/flickr.html')
  config.add_route('flickr_callback', '/flickr_callback')
  config.add_route('flickr_confirmation', '/flickr_confirmation.html')

  # facebook auth
  config.add_route('facebook','/facebook.html')
  config.add_route('facebook_callback', '/facebook_callback')
  config.add_route('facebook_confirmation', '/facebook_confirmation.html')

  # linkedin auth
  config.add_route('linkedin','/linkedin.html')
  config.add_route('linkedin_callback', '/linkedin_callback')
  config.add_route('linkedin_confirmation', '/linkedin_confirmation.html')

  # google+ auth
  config.add_route('googleplus','/googleplus.html')
  config.add_route('googleplus_callback', '/google_callback')
  config.add_route('googleplus_confirmation', '/googleplus_confirmation.html')
  
  # google+ auth
  config.add_route('foursquare','/foursquare.html')
  config.add_route('foursquare_callback', '/foursquare_callback')
  config.add_route('foursquare_confirmation', '/foursquare_confirmation.html')
  
  config.scan('timweb')

  return config.make_wsgi_app()

