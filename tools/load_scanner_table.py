import sys
import random
import base64
import os
import logging

from tim_commons.app_base import AppBase
from tim_commons import db
from mi_schema.models import EventScannerPriority


class LoadScannerTableApplication(AppBase):
  def init_args(self, option_parser):
    option_parser.add_option('--number_of_events',
                             dest='events',
                             default=1024,
                             type=int,
                             help='Number of random events to load into the database')

  def app_main(self, config, options, args):
    db.configure_session(url=config['db']['sqlalchemy.url'])
    services = _lookup_services_with_event_queue(config)
    maximum_priority = int(config['scanner']['maximum_priority'])

    logging.info("Adding %s events to the scanner", options.events)
    with db.Context():
      for ignore in xrange(options.events):
        service_id = random.choice(services)
        priority = random.randint(0, maximum_priority)
        user_id = _random_string(32)
        event_id = _random_string(64)

        scanner_event = EventScannerPriority(event_id, user_id, service_id, priority)
        db.Session().add(scanner_event)
        sys.stdout.write('.')

    sys.stdout.write('\n')


def _random_string(length):
  return base64.urlsafe_b64encode(os.urandom(length))


def _lookup_services_with_event_queue(config):
  result = []
  for service, queues in config['queues'].iteritems():
    if 'event' in queues:
      result.append(service)

  return result


if __name__ == '__main__':
  sys.exit(LoadScannerTableApplication('load_scanner_table').main())
