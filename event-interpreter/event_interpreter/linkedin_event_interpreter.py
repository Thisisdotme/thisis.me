'''
Created on May 9, 2012

@author: howard
'''

from datetime import datetime
from service_event_interpreter import ServiceEventInterpreter


class LinkedinEventInterpreter(ServiceEventInterpreter):

  def get_id(self):
    return self.json['updateKey']

  def get_time(self):
    return datetime.utcfromtimestamp(int(self.json['timestamp'] / 1000))

  def get_headline(self):
    # connection update
    if self.json['updateType'] == 'CONN':
      return self.json['updateContent']['person']['connections']['values'][0]['???']
    # joined group update
    elif self.json['updateType'] == 'JGRP':
      return self.json['updateContent']['person']['memberGroups']['values'][0]['name']
    # status updates
    elif self.json['updateType'] == 'STAT':
      return self.json['updateContent']['person']['currentStatus']
    return None

