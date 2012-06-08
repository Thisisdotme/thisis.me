'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class InstagramEventInterpreter(ServiceEventInterpreter):

  def get_type(self):
    return None

  def get_id(self):
    return self.json['id']

  def get_create_time(self):
    return datetime.utcfromtimestamp(float(self.json['created_time']))
