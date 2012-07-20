from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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

  """ Setup the database
  """
  db_url = db.create_url_from_config(tim_config['db'])
  db.configure_session(db_url)

  """ load the oauth configuration settings
  """
  global oauth_config
  oauth_config = tim_config['oauth']

  config = Configurator(settings=settings)

  config.add_static_view('img', 'timmobilev2:img', cache_max_age=0)
  config.add_static_view('css', 'timmobilev2:css', cache_max_age=0)
  config.add_static_view('js', 'timmobilev2:js', cache_max_age=0)

  config.add_route('index', '/')
  # config.add_route('app', '/{authorname}/')
  config.add_route('app', '/{authorname}')

  config.add_route('resource.any', '/{authorname}/asset/{resource}.{ext}')

  config.scan()

  return config.make_wsgi_app()
