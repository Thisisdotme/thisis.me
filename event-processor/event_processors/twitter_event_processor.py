'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.twitter_event_interpreter import TwitterEventInterpreter
from event_processor import EventProcessor


class TwitterEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json):
    return TwitterEventInterpreter(service_event_json)
