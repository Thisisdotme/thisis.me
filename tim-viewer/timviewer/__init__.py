from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """
  engine = engine_from_config(settings, 'sqlalchemy.')
  DBSession.configure(bind=engine)

  config = Configurator(settings=settings)

  config.add_static_view('static', 'timviewer:static', cache_max_age=None)
  config.add_static_view('img', 'timviewer:img', cache_max_age=None)
  config.add_static_view('css', 'timviewer:css', cache_max_age=None)
  config.add_static_view('js', 'timviewer:js', cache_max_age=None)
  config.add_static_view('themes', 'timviewer:themes', cache_max_age=None)
 
  config.add_route('authors', '/')
  config.add_route('feedback', '/feedback')

  config.add_route('timeline', '/{authorname}')
  config.add_route('feature_timeline', '/{authorname}/features/{featurename}')
  config.add_route('features', '/{authorname}/features')
  config.add_route('settings', '/{authorname}/settings')
  config.add_route('details', '/{authorname}/event/{eventId}')

  config.scan()

  return config.make_wsgi_app()

