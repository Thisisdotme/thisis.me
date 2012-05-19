'''
Created on May 10, 2012

@author: howard
'''

from abc import (abstractmethod, ABCMeta)
from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap)


class EventUpdater(object):

  __metaclass__ = ABCMeta

  def __init__(self, service_name, db_session, oauth_config, log):

    self.service_name = service_name
    self.db_session = db_session
    self.oauth_config = oauth_config
    self.log = log

    # get the service-id for this collector's service
    service_id, = self.db_session.query(Service.id).filter(Service.service_name == self.service_name).one()
    self.service_id = service_id

  @abstractmethod
  def fetch(self, service_id, service_author_id, service_event_id, callback):
    pass

  def get_author_service_map(self, service_author_id):
    return self.db_session.query(AuthorServiceMap). \
                           filter(and_(AuthorServiceMap.service_id == self.service_id,
                                       AuthorServiceMap.service_author_id == service_author_id)). \
                           one()
