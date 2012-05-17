'''
Created on May 10, 2012

@author: howard
'''

import sys


class EventUpdaterFactory(object):

  '''
    Loads the module and instantiates the class for the specified collector.
    Works on convention.
    The module name must be <<service_name>>_event_updater and the class name
    must be <<Servicename>>EventUpdater
  '''

  @classmethod
  def from_service_name(cls, service_name, db_session, oauth_config, log):

    # load the desired module from the event_collectors package
    name = 'event_updaters.' + service_name + '_event_updater'
    __import__(name)
    mod = sys.modules[name]

    # retrieve the desired class and instantiate a new instance
    cls = getattr(mod, service_name.capitalize() + "EventUpdater")
    collector = cls(service_name, db_session, oauth_config, log)

    return collector
