'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class GooglePlusStatusEventInterpreter(ServiceEventInterpreter):

  def get_id(self):
    return self.json['id']

  def get_time(self):
    return datetime.strptime(self.json['published'], '%Y-%m-%dT%H:%M:%S.%fZ')
