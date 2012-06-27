'''
Created on May 9, 2012

@author: howard
'''

from abc import (abstractmethod, ABCMeta)


class ServiceEventInterpreter(object):

  __metaclass__ = ABCMeta

  def __init__(self, json, author_service_map, oauth_config):
    self.json = json
    self.author_service_map = author_service_map
    self.oauth_config = oauth_config

  '''
    get the type of the event (status, photo, album, checkin, etc.)
  '''
  @abstractmethod
  def get_type(self):
    pass

  '''
    get the service's unique identifier for the event
  '''
  @abstractmethod
  def get_id(self):
    pass

  '''
    get the time the event the created as a Python Time object
  '''
  @abstractmethod
  def get_create_time(self):
    pass

  '''
    get the time the event was last updated as a Python Time object
  '''
  def get_update_time(self):
    None

  '''
    get the events headline - a brief caption
  '''
  def get_headline(self):
    return None

  '''
    get the event's tagline or deck - a sentence or few sentences which summarizes
    # the post
  '''
  def get_tagline(self):
    return None

  '''
    get the event's content -- the full story or body of text
  '''
  def get_content(self):
    return None

  '''
    get the primary photo, if any, associated with the event
  '''
  def get_photo(self):
    return None

  '''
    get the url of the event's service page
  '''
  def get_url(self):
    return None

  '''
    get the geo coordinates for this event
  '''
  def get_location(self):
    return None

  '''
    get any auxiliary content for the event
  '''
  def get_auxiliary_content(self):
    return None

  '''
    get the origin for the event.  For events that get shared
    on multile platforms the origin identifies the originating
    service
  '''
  def get_origin(self):
    return None
