from abc import ABCMeta

from datetime import datetime
from mi_schema.models import ServiceObjectType
from service_event_interpreter import ServiceEventInterpreter
from tim_commons import normalize_uri


class FacebookEventInterpreter(ServiceEventInterpreter):

  __metaclass__ = ABCMeta

  DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

  def get_id(self):
    # allow the object_id to have precedence if it exists
    return self.json['object_id'] if 'object_id' in self.json else self.json.get('id', None)

  def get_create_time(self):
    return datetime.strptime(self.json['created_time'], self.DATETIME_FORMAT)

  def get_update_time(self):
    date = self.json.get('updated_time')
    if date:
      return datetime.strptime(date, self.DATETIME_FORMAT)

    return None

  def get_type(self):
    return self.json.get('type', None)


class FacebookStatusEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return ServiceObjectType.STATUS_TYPE

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

  def original_content_uri(self):
    uri = self.json.get('link')
    if uri:
      return normalize_uri(uri)

    return None


class FacebookPhotoAlbumEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return ServiceObjectType.PHOTO_ALBUM_TYPE

  def get_headline(self):
    return self.json.get('name', None)

  def get_photo(self):
    pass


class FacebookPhotoEventInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return ServiceObjectType.PHOTO_TYPE

  def get_headline(self):
    return self.json.get('name', None)

  def get_photo(self):
    photo = None
    images = self.json.get('images', None)
    if images and len(images) > 0:
      photo = images[0].get('source', None)
    return photo


class FacebookCheckinInterpreter(FacebookEventInterpreter):

  def get_type(self):
    return ServiceObjectType.CHECKIN_TYPE

  def get_headline(self):
    return self.json.get('message', None)

  def get_tagline(self):
    return self.json['place'].get('name', None) if 'place' in self.json else None

  def get_content(self):
    return self.get_tagline()
