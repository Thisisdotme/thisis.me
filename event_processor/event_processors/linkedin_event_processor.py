'''
Created on May 8, 2012

@author: howard
'''


from event_interpreter.linkedin_event_interpreter import LinkedinEventInterpreter
from event_processor import EventProcessor


class LinkedinEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json, author_service_map, oauth_config):
    return LinkedinEventInterpreter(service_event_json, author_service_map, oauth_config)
