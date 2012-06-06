import logging
import sys
from abc import abstractmethod
from datetime import (datetime, timedelta)

from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap, Author)
from tim_commons import db


def from_service_name(service_name, oauth_config):
  '''Loads the module and instantiates the class for the specified collector.

  Works on convention. The module name must be <<service_name>>_event_collector and the class
  name must be <<Servicename>>EventCollector
  '''

  # load the desired module from the event_collectors package
  name = 'event_collectors.' + service_name + '_event_collector'
  __import__(name)
  mod = sys.modules[name]

  # retrieve the desired class and instantiate a new instance
  cls = getattr(mod, service_name.capitalize() + "EventCollector")
  collector = cls(service_name, oauth_config)

  return collector


class EventCollector(object):

  LAST_UPDATE_OVERLAP = timedelta(hours=1)
  LOOKBACK_WINDOW = timedelta(days=365)

  MAX_EVENTS = 10000

  def __init__(self, service_name, oauth_config):

    self.service_name = service_name
    self.oauth_config = oauth_config

    # get the service-id for this collector's service
    service_id, = db.Session().query(Service.id).filter(Service.service_name == self.service_name).one()
    self.service_id = service_id

  '''
    begin_fetch - records state for starting of fetch and creates fetch
    state object
  '''
  def fetch_begin(self, service_author_id):

    asm, author_name = db.Session().query(AuthorServiceMap, Author.author_name). \
                                    join(Author, AuthorServiceMap.author_id == Author.id). \
                                    filter(and_(AuthorServiceMap.service_id == self.service_id,
                                                AuthorServiceMap.service_author_id == service_author_id)). \
                                    one()

    now = datetime.utcnow()
    min_event_time = None
    if asm.most_recent_event_timestamp:
      min_event_time = asm.most_recent_event_timestamp - self.LAST_UPDATE_OVERLAP
    else:
      min_event_time = now - self.LOOKBACK_WINDOW

    return {'now': now,
            'asm': asm,
            'author_name': author_name,
            'min_event_time': min_event_time,
            'most_recent_event_id': asm.most_recent_event_id,
            'most_recent_event_timestamp': asm.most_recent_event_timestamp}

  '''
    end_fetch - updates the last_update_time to the time at the beginning of the fetch
    and updates most_recent_event_id and most_recent_event_timestamp if changed
  '''
  def fetch_end(self, state):

    # set the author/service map's last update time
    state['asm'].last_update_time = state['now']

    # update the most_recent_event_id and most_recent_event_timestamp if changed
    if state['most_recent_event_id'] != state['asm'].most_recent_event_id or \
       state['most_recent_event_timestamp'] != state['asm'].most_recent_event_timestamp:
      state['asm'].most_recent_event_id = state['most_recent_event_id']
      state['asm'].most_recent_event_timestamp = state['most_recent_event_timestamp']

  '''
    fetch_log - utility for logging author event fetches in a consistent manner
  '''
  def fetch_log_info(self, state):
    logging.debug('Fetching %s events for author %s (service_author_id %s)',
                  self.service_name,
                  state['author_name'],
                  state['asm'].service_author_id)

  '''
    fetch
  '''
  @abstractmethod
  def fetch(self, service_author_id, callback):
    pass

  def screen_event(self, interpreter, state):

    qualifies = False

    event_time = interpreter.get_time()

    # skip any events older than the lookback window
    if event_time >= state['min_event_time']:

      qualifies = True

      # update the most-recent event timestamp state if appropriate
      if not state['most_recent_event_timestamp'] or event_time > state['most_recent_event_timestamp']:
        state['most_recent_event_id'] = interpreter.get_id()
        state['most_recent_event_timestamp'] = event_time

    else:
      logging.debug('Skipping event older than lookback window or last-update overlap; event_time == %s' % event_time)

    return qualifies
