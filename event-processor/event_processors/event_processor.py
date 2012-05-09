'''
Created on May 8, 2012

@author: howard
'''

from abc import abstractmethod


class EventProcessor(object):

  def __init__(self, service_name, db_session, log):

    self.service_name = service_name
    self.db_session = db_session
    self.log = log

  '''
    Handler method to process service events
  '''
  @abstractmethod
  def process(self, tim_author_id, service_author_id, service_event_json):
    pass
