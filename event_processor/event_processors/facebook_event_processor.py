'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.facebook_event_interpreter import FacebookStatusEventInterpreter
from event_interpreter.facebook_event_interpreter import FacebookPhotoAlbumEventInterpreter
from event_interpreter.facebook_event_interpreter import FacebookPhotoEventInterpreter
from event_interpreter.facebook_event_interpreter import FacebookCheckinInterpreter

from event_processor import EventProcessor


class FacebookEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json, author_service_map, oauth_config):
    event_type = service_event_json.get('type', None)
    if event_type == 'album':
      return FacebookPhotoAlbumEventInterpreter(service_event_json, author_service_map, oauth_config)
    elif event_type == 'photo':
      return FacebookPhotoEventInterpreter(service_event_json, author_service_map, oauth_config)
    elif event_type == 'checkin':
      return FacebookCheckinInterpreter(service_event_json, author_service_map, oauth_config)
    else:
      return FacebookStatusEventInterpreter(service_event_json, author_service_map, oauth_config)
