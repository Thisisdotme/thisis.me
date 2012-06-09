'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class TwitterEventInterpreter(ServiceEventInterpreter):

  DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

  def get_type(self):
    return self.STATUS_TYPE

  def get_id(self):
    return self.json['id_str']

  def get_create_time(self):
    return datetime.strptime(self.json['created_at'], self.DATETIME_STRING_FORMAT)
