from pyramid.config import Configurator
from sqlalchemy import engine_from_config

import pyramid_beaker

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from mi_utils.oauth import load_oauth_config

from models import initialize_sql
from security import groupfinder

# object created from JSON file that stores oAuth configuration for social features
oAuthConfig = None

def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """
  engine = engine_from_config(settings, 'sqlalchemy.')
  initialize_sql(engine)

  # load the oauth configuration settings
  global oAuthConfig
  oAuthConfig = load_oauth_config(settings['mi.oauthkey_file'])

  authn_policy = AuthTktAuthenticationPolicy('tim_secret', callback=groupfinder, timeout=1800, reissue_time=180, max_age=1800, debug=True)
  authz_policy = ACLAuthorizationPolicy()
  
  session_factory = pyramid_beaker.session_factory_from_settings(settings) 

  config = Configurator(settings=settings,
                        root_factory='timmobile.context.RootFactory',
                        authentication_policy=authn_policy,
                        authorization_policy=authz_policy,
                        session_factory=session_factory)

  config.add_static_view('static', 'timmobile:static', cache_max_age=0)
  config.add_static_view('img', 'timmobile:img', cache_max_age=0)
  config.add_static_view('css', 'timmobile:css', cache_max_age=0)
  config.add_static_view('js', 'timmobile:js', cache_max_age=0)

  # define routes
  #
  config.add_route('home', '/')

  config.add_route('login', '/login')
  config.add_route('logout', '/logout')

  config.add_route('newlogin', '/newlogin')
  config.add_route('accounts', '/accounts')
  config.add_route('account_details', '/accounts/{featurename}')
  config.add_route('newsfeed', '/newsfeed')
  
  config.add_route('timeline', '/{authorname}/timeline')
  
  config.add_route('profile', '/{authorname}/profile')
  config.add_route('followers', '/followers')
  
  #
  # oauth setup paths
  #

  # twitter oauth
  config.add_route('twitter','/oauth/twitter')
  config.add_route('twitter_callback', '/oauth/twitter/callback')

  # facebook auth
  config.add_route('facebook','/oauth/facebook')
  config.add_route('facebook_callback', '/oauth/facebook/callback')
  
  # linkedin auth
  config.add_route('linkedin','/oauth/linkedin')
  config.add_route('linkedin_callback', '/oauth/linkedin/callback')
 
  # google+ auth
  config.add_route('googleplus','/oauth/googleplus')
  config.add_route('googleplus_callback', '/oauth/googleplus/callback')

  # instagram auth
  config.add_route('instagram','/oauth/instagram')
  config.add_route('instagram_callback', '/oauth/instagram/callback')

  # flickr auth
  config.add_route('flickr','/oauth/flickr')
  config.add_route('flickr_callback', '/oauth/flickr/callback')

  # foursquare auth
  config.add_route('foursquare','/oauth/foursquare')
  config.add_route('foursquare_callback', '/oauth/foursquare/callback')
  
  # generic oauth
  config.add_route('oauth','/oauth/{featurename}')
  config.add_route('oauth_callback', '/oauth/{featurename}/callback')
  
  config.scan()

  return config.make_wsgi_app()

