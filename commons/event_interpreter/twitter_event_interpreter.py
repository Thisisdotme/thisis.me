from datetime import datetime
from mi_schema.models import ServiceObjectType
from service_event_interpreter import ServiceEventInterpreter
from tim_commons import normalize_uri


class TwitterEventInterpreter(ServiceEventInterpreter):
  DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

  def get_type(self):
    return ServiceObjectType.STATUS_TYPE

  def get_id(self):
    return self.json['id_str']

  def get_create_time(self):
    return datetime.strptime(self.json['created_at'], self.DATETIME_STRING_FORMAT)

  def get_tagline(self):
    return self.json.get('text', '')

  def get_content(self):
    return self.get_tagline()

  def get_origin(self):
    source = self.json.get('source')
    return source if source else None

  def get_photo(self):
    for media in self.json['entities'].get('media', []):
      if media.get('type') == "photo":
        return media.get('media_url')

  def original_content_uri(self):
    entities = self.json.get('entities')
    if entities:
      urls = entities.get('urls')
      if urls:
        return normalize_uri(urls[0].get('expanded_url'))

    return None

  def service_author_id(self):
    return self.json['user']['id_str']
