'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.facebook_event_interpreter import FacebookStatusEventInterpreter
from event_processor import EventProcessor


class FacebookEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json):
    return FacebookStatusEventInterpreter(service_event_json)
