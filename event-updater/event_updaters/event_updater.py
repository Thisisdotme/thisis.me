import sys
from abc import (abstractmethod, ABCMeta)
from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap)
from tim_commons import db


def from_service_name(service_name, oauth_config):
  # load the desired module from the event_collectors package
  name = 'event_updaters.' + service_name + '_event_updater'
  __import__(name)
  mod = sys.modules[name]

  # retrieve the desired class and instantiate a new instance
  cls = getattr(mod, service_name.capitalize() + "EventUpdater")
  collector = cls(service_name, oauth_config)

  return collector


class EventUpdater(object):

  __metaclass__ = ABCMeta

  def __init__(self, service_name, oauth_config):

    self.service_name = service_name
    self.oauth_config = oauth_config

    # get the service-id for this collector's service
    query = db.Session.query(Service.id).filter(Service.service_name == self.service_name)
    self.service_id, = query.one()

  @abstractmethod
  def fetch(self, service_id, service_author_id, service_event_id, callback):
    pass

  def get_author_service_map(self, service_author_id):
    query = db.Session.query(AuthorServiceMap)
    query = query.filter(and_(AuthorServiceMap.service_id == self.service_id,
                              AuthorServiceMap.service_author_id == service_author_id))
    return query.one()
