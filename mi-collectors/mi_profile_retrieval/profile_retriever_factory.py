'''
Created on Jan 16, 2011

@author: howard
'''

from linkedin_profile_retriever import LinkedInProfileRetriever
from googleplus_profile_retriever import GooglePlusProfileRetriever
from twitter_profile_retriever import TwitterProfileRetriever

class ProfileRetrievalFactory(object):

  @classmethod
  def get_retriever_for(cls,serviceName):
  
    retriever = None
    
    if serviceName == 'linkedin':
      retriever = LinkedInProfileRetriever()
    elif serviceName == 'googleplus':
      retriever = GooglePlusProfileRetriever()
    elif serviceName == 'twitter':
      retriever = TwitterProfileRetriever()    
  #  elif serviceName == 'facebook':
  #    retriever = FacebookCollector()
  #  elif serviceName == 'instagram':
  #    retriever = InstagramCollector()
    return retriever
