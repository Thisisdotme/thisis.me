'''
Created on Jan 16, 2012

@author: howard
'''

from abc import abstractmethod

'''
This is the superclass for all profile retrievers.  It provides a common infrastructure for all retrievers
'''
class ProfileRetriever(object):
  '''
  classdocs
  '''
  service_name = None
  
  '''
  Constructor
  '''
  def __init__(self):
    print '%s profile retriever executing...' % self.service_name 


  @abstractmethod
  def get_author_profile(self,service_map,db_session,oauth_config):
    pass