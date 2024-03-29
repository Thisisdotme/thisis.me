'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from mi_schema.models import ServiceObjectType
from service_event_interpreter import ServiceEventInterpreter


class FoursquareEventInterpreter(ServiceEventInterpreter):

  def get_type(self):
    return ServiceObjectType.CHECKIN_TYPE

  def get_id(self):
    return self.json['id']

  def get_create_time(self):
    return datetime.utcfromtimestamp(int(self.json['createdAt']))

  def get_headline(self):
    return self.json.get('shout', None)

  def get_content(self):

    content = None

    if 'venue' in self.json:

      address = self.json['venue']['location'].get('address')
      city = self.json['venue']['location'].get('city')

      # define location
      location = None
      if address and city:
        location = '%s, %s' % (address, city)
      elif address:
        location = address
      else:
        location = city
      location = ' (%s)' % location if location else ''

      content = unicode('{0}{1}').format(self.json['venue'].get('name', ''), location)

    return content

  def get_photo(self):
    return self.json['photos']['items'][0]['url'] if int(self.json['photos']['count']) > 0 else None

  def get_origin(self):
    return unicode('{0}#{1}').format(self.json['source'].get('name', ''), self.json['source'].get('url', ''))
