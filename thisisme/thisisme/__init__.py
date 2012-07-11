from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession


def main(global_config, **settings):

  """ This function returns a Pyramid WSGI application.
  """
  engine = engine_from_config(settings, 'sqlalchemy.')
  DBSession.configure(bind=engine)

  config = Configurator(settings=settings)

  config.add_static_view('static', 'static', cache_max_age=None)
  config.add_static_view('img', 'static/img', cache_max_age=None)
  config.add_static_view('css', 'static/css', cache_max_age=None)
  config.add_static_view('js', 'static/js', cache_max_age=None)

  config.add_route('home', '/')
  config.add_route('myapp', '/myapp.html')
  config.add_route('features', '/features.html')
  config.add_route('pricing', '/pricing.html')
  config.add_route('about', '/about.html')
  config.add_route('terms', '/terms.html')
  config.add_route('contact', '/contact.html')

  config.scan()

  return config.make_wsgi_app()
