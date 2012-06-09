'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class FacebookEventInterpreter(ServiceEventInterpreter):

  DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

  def get_id(self):
    return self.json.get('id', None)

  def get_create_time(self):
    return datetime.strptime(self.json['created_time'], self.DATETIME_FORMAT)

  def get_update_time(self):
    return datetime.strptime(self.json['updated_time'], self.DATETIME_FORMAT)

  def get_type(self):
    return self.json.get('type', None)


class FacebookStatusEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return self.STATUS_TYPE

  def get_headline(self):
    # this handles events from Nike which is a repetition event
    other = self.json.get('name') + ".  " + self.json.get('caption') if self.json.get('caption') and self.json.get('name') else None

    return self.json.get('story') or self.json.get('message') or other

  def get_origin(self):
    application = self.json.get('application')
    if application:
      origin = '%s,%s,%s' % (application.get('name', ''), application.get('namespace'), application.get('id'))
    else:
      origin = super(FacebookStatusEventInterpreter, self).get_origin()

    return origin

  def get_url(self):
    return 'https://graph.facebook.com/%s' % (self.get_id())

  def get_photo(self):
    return self.json['picture'] if 'picture' in self.json else None


class FacebookPhotoAlbumEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return self.PHOTOALBUM_TYPE


class FacebookPhotoEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return self.PHOTO_TYPE