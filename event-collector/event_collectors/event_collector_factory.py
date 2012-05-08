'''
Created on May 4, 2012

@author: howard
'''

import sys


class EventCollectorFactory(object):

  '''
    Loads the module and instantiates the class for the specified collector.
    Works on convention.
    The module name must be <<service_name>>_event_collector and the class name
    must be <<Servicename>>EventCollector
  '''

  @classmethod
  def from_service_name(cls, service_name, db_session, oauth_config, log):

    # load the desired module from the event_collectors package
    name = 'event_collectors.' + service_name + '_event_collector'
    __import__(name)
    mod = sys.modules[name]

    # retrieve the desired class and instantiate a new instance
    cls = getattr(mod, service_name.capitalize() + "EventCollector")
    collector = cls(db_session, oauth_config, log)

    # confirm things are properly aligned and as we expect
    if collector.SERVICE_NAME != service_name:
      raise Exception('Service collector class out of sync with service name')

    return collector
