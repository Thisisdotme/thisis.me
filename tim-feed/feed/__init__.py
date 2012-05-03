from pyramid.config import Configurator

def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  config = Configurator(settings=settings)

  config.add_route('facebook_feed', 'feed/facebook')

  config.scan()
  return config.make_wsgi_app()
