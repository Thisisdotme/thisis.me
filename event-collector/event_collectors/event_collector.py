'''
Created on May 4, 2012

@author: howard
'''

from abc import abstractmethod
from datetime import (datetime, timedelta)

from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap, Author)


class EventCollector(object):

  def __init__(self, service_name, db_session, oauth_config, log):

    self.service_name = service_name
    self.db_session = db_session
    self.oauth_config = oauth_config
    self.log = log
    self.lookbackWindow = datetime.now() - timedelta(days=365)

    # get the service-id for this collector's service
    service_id, = self.db_session.query(Service.id).filter(Service.service_name == self.service_name).one()
    self.service_id = service_id

  '''
    begin_fetch - records state for starting of fetch and creates fetch
    state object
  '''
  def fetch_begin(self, service_author_id):

    asm, author_name = self.db_session.query(AuthorServiceMap, Author.author_name). \
                          join(Author, AuthorServiceMap.author_id == Author.id). \
                          filter(and_(AuthorServiceMap.service_id == self.service_id,
                                      AuthorServiceMap.service_author_id == service_author_id)). \
                          one()

    return {'now': datetime.now(),
            'asm': asm,
            'author_name': author_name,
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

    self.db_session.flush()
    self.db_session.commit()

  '''
    fetch_log - utility for logging author event fetches in a consistent manner
  '''
  def fetch_log(self, state):
    self.log.debug('Fetching %s events for author %s (service_author_id %s)' %
                      (self.service_name, state['author_name'], state['asm'].service_author_id))

  '''
    fetch
  '''
  @abstractmethod
  def fetch(self, service_author_id, callback):
    pass

