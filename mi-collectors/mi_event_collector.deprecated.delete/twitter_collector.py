'''
Created on Dec 14, 2011

@author: howard
'''

from datetime import datetime

import tweepy
import oauth2 as oauth
import time
import urllib
import urllib2
import json

from mi_schema.models import FeatureEvent

from collector import Collector

class TwitterCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'twitter'

  def __init__(self):
    '''
    Constructor
    '''
    super(TwitterCollector,self).__init__()
    

  def update_author(self, afm, dbSession, oauthConfig):

    currUpdateTime = datetime.utcnow()

    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = prevRecentEventTimestamp = afm.most_recent_event_timestamp

    # transition to using tweepy at this point
    #
    auth = tweepy.OAuthHandler(oauthConfig['key'], oauthConfig['secret'])
    auth.set_access_token(afm.access_token, afm.access_token_secret)
  
    api = tweepy.API(auth)
  
    # If the authentication was successful, you should
    # see the name of the account print out
    print 'twitter username %s' % api.me().name
    
    params = {
      'include_rts':'1',
      'include_entities':'1',
      'count':'200',
    }
    
    # Set the API endpoint 
    url = "http://api.twitter.com/1/statuses/user_timeline.json?%"

    consumer = oauth.Consumer(oauthConfig['key'], oauthConfig['secret'])
    token = oauth.Token(afm.access_token, afm.access_token_secret)
    
    client = oauth.Client(consumer, token)

    resp, content = client.request(url)
    
    timelineJSON = json.loads(content)
    
    #for post in timelineJSON:
      
  
    response = api.user_timeline()
  
    # for element in the feed
    for post in response:

      eventTimestamp = post.created_at
      eventId = post.id

      # if prevRecentEventTimestamp exists (i.e. we've updated before) make a few extra checks
      # to weed out duplicate events
      if prevRecentEventTimestamp:

        # check if the create time of this post is before our most-recent timestamp
        if eventTimestamp < prevRecentEventTimestamp:
          continue

        # check if we already have this event and skip it if so
        count = dbSession.query(FeatureEvent.id).filter_by(author_feature_map_id=afm.id,event_id=eventId).count()
        if count > 0:
          continue

      # determine if this is the "most-recent" event and update the most-recent variables
      # if so
      if mostRecentEventTimestamp is None or eventTimestamp > mostRecentEventTimestamp:
        mostRecentEventTimestamp = eventTimestamp
        mostRecentEventId = eventId
      
      # add the event to the db
      featureEvent = FeatureEvent(afm.id,eventId,eventTimestamp,None,post.text,None,None)
      dbSession.add(featureEvent)
      dbSession.flush()

    afm.last_update_time = currUpdateTime

    # update the most_recent_event_id and most_recent_event_timestamp if changed    
    if mostRecentEventId != afm.most_recent_event_id or mostRecentEventTimestamp != afm.most_recent_event_timestamp:
      # update the authorFeatureMap table
      afm.most_recent_event_id = mostRecentEventId
      afm.most_recent_event_timestamp = mostRecentEventTimestamp

    dbSession.flush()
    dbSession.commit()

    return
