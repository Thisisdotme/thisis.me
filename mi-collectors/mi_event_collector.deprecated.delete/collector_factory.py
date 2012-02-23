'''
Created on Dec 14, 2011

@author: howard
'''

from instagram_collector import InstagramCollector
from facebook_collector import FacebookCollector
from twitter_collector import TwitterCollector
from linkedin_collector import LinkedInCollector
from googleplus_collector import GooglePlusCollector
from foursquare_collector import FoursquareCollector

class EventCollectorFactory(object):

  @classmethod
  def get_collector_for(cls,feature_name):

    collector = None
    
    if feature_name == 'twitter':
      collector = TwitterCollector()
    elif feature_name == 'facebook':
      collector = FacebookCollector()
    elif feature_name == 'instagram':
      collector = InstagramCollector()
    elif feature_name == 'linkedin':
      collector = LinkedInCollector()
    elif feature_name == 'googleplus':
      collector = GooglePlusCollector()
    elif feature_name == 'foursquare':
      collector = FoursquareCollector()
    
    return collector
