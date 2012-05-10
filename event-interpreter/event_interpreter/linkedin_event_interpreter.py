'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class LinkedinConnectEventInterpreter(ServiceEventInterpreter):

  def get_id(self):
    raise Exception('not implemented')

  def get_time(self):
    return datetime.utcfromtimestamp(int(self.json['timestamp'] / 1000))
