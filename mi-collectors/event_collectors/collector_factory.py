'''
Created on Dec 14, 2011

@author: howard
'''

from event_collectors.facebook import FacebookFullCollector
from event_collectors.twitter import TwitterFullCollector
from event_collectors.foursquare import FoursquareFullCollector
from event_collectors.linkedin import LinkedInFullCollector
from event_collectors.instagram import InstagramFullCollector
from event_collectors.googleplus import GooglePlusFullCollector

class EventCollectorFactory(object):

  @classmethod
  def get_collector_for(cls,feature_name,aws_access_key, aws_secret_key):

    collector = None
    
    if feature_name == 'facebook':
      collector = FacebookFullCollector(aws_access_key, aws_secret_key)
    elif feature_name == 'twitter':
      collector = TwitterFullCollector(aws_access_key, aws_secret_key)
    elif feature_name == 'foursquare':
      collector = FoursquareFullCollector(aws_access_key, aws_secret_key)
    elif feature_name == 'linkedin':
      collector = LinkedInFullCollector(aws_access_key, aws_secret_key)
    elif feature_name == 'instagram':
      collector = InstagramFullCollector(aws_access_key, aws_secret_key)
    elif feature_name == 'googleplus':
      collector = GooglePlusFullCollector(aws_access_key, aws_secret_key)
    
    return collector
