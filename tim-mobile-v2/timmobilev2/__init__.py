from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from mi_utils.oauth import load_oauth_config

from .models import DBSession

# object created from JSON file that stores oAuth configuration for social features
oAuthConfig = None

def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """
  
  engine = engine_from_config(settings, 'sqlalchemy.')
  DBSession.configure(bind=engine)
  
  # load the oauth configuration settings
  global oAuthConfig
  oAuthConfig = load_oauth_config(settings['mi.oauthkey_file'])
  
  config = Configurator(settings=settings)

  config.add_static_view('img', 'timmobilev2:img', cache_max_age=0)
  config.add_static_view('css', 'timmobilev2:css', cache_max_age=0)
  config.add_static_view('js', 'timmobilev2:js', cache_max_age=0)

  config.add_route('index', '/')
  config.add_route('app', '/{authorname}/')

  config.add_route('resource.any', '/{authorname}/asset/{resource}.{ext}')

  config.scan()

  return config.make_wsgi_app()
  
