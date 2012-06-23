'''
Created on Jan 16, 2012

@author: howard
'''

from abc import abstractmethod
import sys

from sqlalchemy import (and_)

from mi_schema.models import (Service, AuthorServiceMap)

from tim_commons import db


def from_service_name(service_name, oauth_config):
  '''Loads the module and instantiates the class for the specified collector.

  Works on convention. The module name must be <<service_name>>_profile_fetcher and the class
  name must be <<Servicename>>ProfileFetcher
  '''

  # load the desired module from the event_collectors package
  name = 'profile_fetchers.' + service_name + '_profile_fetcher'
  __import__(name)
  mod = sys.modules[name]

  # retrieve the desired class and instantiate a new instance
  cls = getattr(mod, service_name.capitalize() + "ProfileFetcher")
  collector = cls(service_name, oauth_config)

  return collector


'''
This is the superclass for all profile retrievers.  It provides a common infrastructure for all retrievers
'''


class ProfileFetcher(object):

  '''
  Constructor
  '''
  def __init__(self, service_name, oauth_config):

    self.service_name = service_name
    self.oauth_config = oauth_config

    # get the service-id for this collector's service
    service_id, = db.Session().query(Service.id).filter(Service.service_name == self.service_name).one()
    self.service_id = service_id

  @abstractmethod
  def get_author_profile(self, service_author_id, asm=None):
    pass

  '''
    begin_fetch - establishes table for profile fetching
  '''
  def fetch_begin(self, service_author_id, asm):

    if not asm:
      asm = db.Session().query(AuthorServiceMap). \
                         filter(and_(AuthorServiceMap.service_id == self.service_id,
                                     AuthorServiceMap.service_author_id == service_author_id)). \
                         one()

    return asm
