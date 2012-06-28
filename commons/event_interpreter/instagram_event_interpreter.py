'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from mi_schema.models import ServiceObjectType
from service_event_interpreter import ServiceEventInterpreter


class InstagramEventInterpreter(ServiceEventInterpreter):

  def get_type(self):
    return ServiceObjectType.PHOTO_TYPE

  def get_id(self):
    return self.json['id']

  def get_create_time(self):
    return datetime.utcfromtimestamp(float(self.json['created_time']))

  def get_headline(self):
    return self.json['caption']['text'] if 'caption' in self.json and self.json['caption'] and 'text' in self.json['caption'] else None

  def get_photo(self):
    return self.json['images']['low_resolution']['url']

  def get_location(self):
    location = None
    if 'location' in self.json:
      location = (self.json['location']['latitude'], self.json['location']['longitude'])
    return location
