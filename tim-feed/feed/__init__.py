from pyramid.config import Configurator
from pyramid.events import ApplicationCreated, NewRequest, subscriber
from tim_commons.message_queue import get_current_message_client


@subscriber(NewRequest)
def add_message_client(event):
  url = event.request.registry.settings['message.queue.url']
  event.request.message_client = get_current_message_client(url)


@subscriber(ApplicationCreated)
def create_feed_queue(event):
  print event.app.registry.settings


def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  config = Configurator(settings=settings)

  config.add_route('facebook_feed', 'feed/facebook')

  config.scan()
  return config.make_wsgi_app()
