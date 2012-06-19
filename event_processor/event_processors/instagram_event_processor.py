'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.instagram_event_interpreter import InstagramEventInterpreter
from event_processor import EventProcessor


class InstagramEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json, author_service_map, oauth_config):
    return InstagramEventInterpreter(service_event_json, author_service_map, oauth_config)
