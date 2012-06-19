from pyramid.config import Configurator
from pyramid.events import ApplicationCreated, NewRequest, subscriber
from tim_commons.message_queue import get_current_message_client, create_queues_from_config
from tim_commons.config import update_pyramid_configuration, ENVIRONMENT_KEY


@subscriber(NewRequest)
def add_message_client(event):
  environment = event.request.registry.settings[ENVIRONMENT_KEY]
  url = environment['broker']['url']
  event.request.message_client = get_current_message_client(url)


@subscriber(ApplicationCreated)
def create_feed_queue(event):
  environment = event.app.registry.settings[ENVIRONMENT_KEY]

  client = get_current_message_client(environment['broker']['url'])
  create_queues_from_config(client, environment['queue'])


def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  # Load global environment configuration
  update_pyramid_configuration(settings)

  config = Configurator(settings=settings)

  config.add_route('facebook_feed', 'feed/facebook')

  config.scan()
  return config.make_wsgi_app()
