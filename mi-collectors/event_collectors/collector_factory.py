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
  '''
  classdocs
  '''
  
  
  def __init__(self):
    '''
    Constructor
    '''

  @classmethod
  def get_collector_for(cls,feature_name,s3Bucket, aws_access_key, aws_secret_key):

    collector = None
    
    if feature_name == 'facebook':
      collector = FacebookFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    elif feature_name == 'twitter':
      collector = TwitterFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    elif feature_name == 'foursquare':
      collector = FoursquareFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    elif feature_name == 'linkedin':
      collector = LinkedInFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    elif feature_name == 'instagram':
      collector = InstagramFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    elif feature_name == 'googleplus':
      collector = GooglePlusFullCollector(s3Bucket, aws_access_key, aws_secret_key)
    
    return collector
