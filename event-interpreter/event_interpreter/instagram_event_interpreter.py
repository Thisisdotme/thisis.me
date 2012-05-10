'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class InstagramEventInterpreter(ServiceEventInterpreter):

  def get_id(self):
    return self.service_event_json['id']

  def get_time(self):
    return datetime.utcfromtimestamp(float(self.service_event_json['created_time']))
