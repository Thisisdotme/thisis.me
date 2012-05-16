import sys
import random
import base64
import os
import contextlib
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tim_commons.app_base import AppBase
from mi_schema.models import EventScannerPriority


class LoadScannerTableApplication(AppBase):
  def display_usage(self):
    return 'usage: %prog [options]'

  def init_args(self):
    self.option_parser.add_option('--number_of_events',
                            dest='events',
                            default=1024,
                            help='Number of random events to load into the database')

  def parse_args(self, ignore):
    (self.option, ignore) = self.option_parser.parse_args()

    if ignore:
      self.option_parser.print_help()
      sys.exit()

  def main(self):
    DBSession = _create_database(self.config)
    services = _lookup_services_with_event_queue(self.config)
    maximum_priority = int(self.config['scanner']['maximum_priority'])

    logging.info("Adding %s events to the scanner", self.option.events)
    with contextlib.closing(DBSession()) as db_session:
      for ignore in xrange(self.option.events):
        service_id = random.choice(services)
        priority = random.randint(0, maximum_priority)
        user_id = _random_string(32)
        event_id = _random_string(64)

        scanner_event = EventScannerPriority(event_id, user_id, service_id, priority)
        db_session.add(scanner_event)
        db_session.commit()
        sys.stdout.write('.')

    sys.stdout.write('\n')


def _random_string(length):
  return base64.urlsafe_b64encode(os.urandom(length))


def _create_database(config):
  db_url = config['db']['sqlalchemy.url']
  engine = create_engine(db_url, encoding='utf-8', echo=True)
  return sessionmaker(bind=engine, autocommit=False)


def _lookup_services_with_event_queue(config):
  result = []
  for service, queues in config['queues'].iteritems():
    if 'event' in queues:
      result.append(service)

  return result


if __name__ == '__main__':
  sys.exit(LoadScannerTableApplication().main())
