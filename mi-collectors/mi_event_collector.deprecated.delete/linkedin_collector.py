'''
Created on Jan 13, 2012

@author: howard
'''

from datetime import datetime

import json
import oauth2 as oauth

from mi_schema.models import FeatureEvent

from mi_utils.oauth import make_request

from collector import Collector

class LinkedInCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'linkedin'

  def __init__(self):
    '''
    Constructor
    '''
    super(LinkedInCollector,self).__init__()
    

  def update_author(self, afm, dbSession, oAuthConfig):

    currUpdateTime = datetime.utcnow()

    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = prevRecentEventTimestamp = afm.most_recent_event_timestamp

    # Create our OAuth consumer instance
    consumer = oauth.Consumer(oAuthConfig['key'], oAuthConfig['secret'])
    token = oauth.Token(key=afm.access_token,secret=afm.access_token_secret)
    client = oauth.Client(consumer, token)

    # request the user's updates 
    response = make_request(client,'http://api.linkedin.com/v1/people/~/network/updates?scope=self&type=APPS&type=CMPY&type=CONN&type=JOBS&type=JGRP&type=PICT&type=PRFX&type=RECU&type=PRFU&type=QSTN&type=SHAR&type=VIRL',{'x-li-format':'json'})
    respJSON = json.loads(response)
  
    for update in respJSON.get('values',[]):

      if update['updateType'] == 'SHAR':
        
        currentShare = update['updateContent']['person']['currentShare']

        eventId = currentShare['id']
        eventTimestamp = datetime.utcfromtimestamp(int(currentShare['timestamp'] / 1000))

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

        caption = currentShare['comment']

        # add the event to the db
        featureEvent = FeatureEvent(afm.id,eventId,eventTimestamp,None,caption,None,None)
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
