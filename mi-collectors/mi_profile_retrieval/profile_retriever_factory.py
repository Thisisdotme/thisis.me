'''
Created on Jan 16, 2011

@author: howard
'''

from linkedin_profile_retriever import LinkedInProfileRetriever
from googleplus_profile_retriever import GooglePlusProfileRetriever
from twitter_profile_retriever import TwitterProfileRetriever

class ProfileRetrievalFactory(object):

  @classmethod
  def get_retriever_for(cls,featureName):
  
    retriever = None
    
    if featureName == 'linkedin':
      retriever = LinkedInProfileRetriever()
    elif featureName == 'googleplus':
      retriever = GooglePlusProfileRetriever()
    elif featureName == 'twitter':
      retriever = TwitterProfileRetriever()    
  #  elif featureName == 'facebook':
  #    retriever = FacebookCollector()
  #  elif featureName == 'instagram':
  #    retriever = InstagramCollector()
    return retriever
