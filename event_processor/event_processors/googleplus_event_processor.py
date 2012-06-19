'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.googleplus_event_interpreter import GoogleplusStatusEventInterpreter
from event_processor import EventProcessor


class GoogleplusEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json, author_service_map, oauth_config):
    return GoogleplusStatusEventInterpreter(service_event_json, author_service_map, oauth_config)
