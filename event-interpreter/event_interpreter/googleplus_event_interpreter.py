'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class GoogleplusStatusEventInterpreter(ServiceEventInterpreter):

  DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

  def get_id(self):
    return self.json['id']

  def get_create_time(self):
    return datetime.strptime(self.json['published'], self.DATETIME_FORMAT)

  def get_update_time(self):
    return datetime.strptime(self.json['updated'], self.DATETIME_FORMAT)
