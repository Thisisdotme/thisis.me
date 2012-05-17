'''
Created on May 8, 2012

@author: howard
'''

from event_interpreter.foursquare_event_interpreter import FoursquareEventInterpreter

from event_processor import EventProcessor


class FoursquareEventProcessor(EventProcessor):

  def get_event_interpreter(self, service_event_json):
    return FoursquareEventInterpreter(service_event_json)
