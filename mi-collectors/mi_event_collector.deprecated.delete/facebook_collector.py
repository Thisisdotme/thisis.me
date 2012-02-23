'''
Created on Dec 14, 2011

@author: howard
'''

import json
from datetime import datetime
import urllib2

from mi_schema.models import FeatureEvent

from collector import Collector


class FacebookCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'facebook'

  def __init__(self):
    '''
    Constructor
    '''
    super(FacebookCollector,self).__init__()

 
  def update_author(self, afm, dbSession, oauthConfig):

    currUpdateTime = datetime.utcnow()

    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = prevRecentEventTimestamp = afm.most_recent_event_timestamp

    fbAuxData = json.loads(afm.auxillary_data)
    fbUserId = fbAuxData['id']
    
    # ??? TODO ??? Need to query the other feeds -- post & event

    # /me/feed
    req = urllib2.Request(oauthConfig['url'] % ('me/feed',afm.access_token))
    res = urllib2.urlopen(req)
    postsJSON = json.loads(res.read())

    # for element in the feed
    for post in postsJSON['data']:

      # currently only interested in 'status' posts from the user
      if post['type'] == 'status' and post['from']['id'] == fbUserId: 

        eventTimestamp = datetime.strptime(post['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
        eventId = post['id']

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

        eventURL = oauthConfig['url'] % (eventId,afm.access_token)

        caption = post.get('story') or post.get('message')
        
        # ??? for debugging
        if not caption:
          print post
            
        # add the event to the db
        featureEvent = FeatureEvent(afm.id,eventId,eventTimestamp,eventURL,caption,None,None)
        dbSession.add(featureEvent)
        dbSession.flush()
 
    # set the author/feature map's last update time
    afm.last_update_time = currUpdateTime

    # update the most_recent_event_id and most_recent_event_timestamp if changed    
    if mostRecentEventId != afm.most_recent_event_id or mostRecentEventTimestamp != afm.most_recent_event_timestamp:
      # update the authorFeatureMap table
      afm.most_recent_event_id = mostRecentEventId
      afm.most_recent_event_timestamp = mostRecentEventTimestamp

    dbSession.flush()
    dbSession.commit()

    return
      