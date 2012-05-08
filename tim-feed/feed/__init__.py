from pyramid.config import Configurator
from pyramid.events import NewRequest
from tim_commons.message_queue import get_current_message_client


def bind_add_message_client(host):
  def add_message_client(event):
    event.request.message_client = get_current_message_client(host)

  return add_message_client


def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  config = Configurator(settings=settings)

  config.add_route('facebook_feed', 'feed/facebook')

  config.add_subscriber(bind_add_message_client(settings['message.queue.url']),
                        NewRequest)

  config.scan()
  return config.make_wsgi_app()
