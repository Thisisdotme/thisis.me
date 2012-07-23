from pyramid.config import Configurator
from pyramid.events import ApplicationCreated, NewRequest, subscriber
from tim_commons import message_queue, config


@subscriber(NewRequest)
def add_message_client(event):
  environment = event.request.registry.settings[config.ENVIRONMENT_KEY]
  url = message_queue.create_url_from_config(environment['broker'])
  event.request.message_client = message_queue.get_current_message_client(url)


@subscriber(ApplicationCreated)
def create_feed_queue(event):
  environment = event.app.registry.settings[config.ENVIRONMENT_KEY]

  url = message_queue.create_url_from_config(environment['broker'])
  client = message_queue.get_current_message_client(url)
  message_queue.create_queues_from_config(client, environment['queues'])


def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  # Load global environment configuration
  config.update_pyramid_configuration(settings)

  configuration = Configurator(settings=settings)

  configuration.add_route('facebook_feed', 'feed/facebook')

  configuration.scan()
  return configuration.make_wsgi_app()
