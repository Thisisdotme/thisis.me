'''
Created on May 8, 2012

@author: howard
'''

import sys


class EventProcessorFactory(object):

  '''
    Loads the module and instantiates the class for the specified collector.
    Works on convention.
    The module name must be <<service_name>>_event_processor and the class name
    must be <<Servicename>>EventProcessor
  '''

  @classmethod
  def from_service_name(cls, service_name, db_session, log):

    # load the desired module from the event_collectors package
    name = 'event_processors.' + service_name + '_event_processor'
    __import__(name)
    mod = sys.modules[name]

    # retrieve the desired class and instantiate a new instance
    cls = getattr(mod, service_name.capitalize() + "EventProcessor")
    collector = cls(service_name, db_session, log)

    return collector
