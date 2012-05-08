'''
Created on May 4, 2012

@author: howard
'''

from abc import abstractmethod
from datetime import (datetime, timedelta)

from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap)


class EventCollector(object):

  SERVICE_NAME = 'unknown'

  def __init__(self, db_session, oauth_config, log):

    self.db_session = db_session
    self.oauth_config = oauth_config
    self.log = log
    self.lookbackWindow = datetime.now() - timedelta(days=365)

    # get the service-id for this collector's service
    service_id, = self.db_session.query(Service.id).filter(Service.service_name == self.SERVICE_NAME).one()
    self.service_id = service_id

  def get_author_service_map_for_fetch(self, service_author_id):
    asm = self.db_session.query(AuthorServiceMap). \
                          filter(and_(AuthorServiceMap.service_id == self.service_id,
                                      AuthorServiceMap.service_author_id == service_author_id)). \
                          one()
    return asm

  @abstractmethod
  def fetch(self, service_author_id, callback):
    self.log.debug('Fetching %s events for service_author_id %s' % (self.SERVICE_NAME, service_author_id))

  '''
    Utility method for creating service specific event message for posting
    to service event queue
  '''
  @abstractmethod
  def create_event_message(self, tim_author_id, service_author_id, jsonEventDict):
    pass
