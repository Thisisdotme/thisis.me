'''
Created on Jan 14, 2012

@author: howard
'''

from datetime import datetime
import urllib
import urllib2
import json

from mi_schema.models import FeatureEvent


from collector import Collector

class GooglePlusCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'googleplus'

  def __init__(self):
    '''
    Constructor
    '''
    super(GooglePlusCollector,self).__init__()
    

  def update_author(self, afm, dbSession, oAuthConfig):

    currUpdateTime = datetime.utcnow()

    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = prevRecentEventTimestamp = afm.most_recent_event_timestamp

    # we need to exchange the refresh token for an access token 
    apiKey = oAuthConfig['key']
    apiSecret = oAuthConfig['secret']
    queryArgs = urllib.urlencode([('client_id',apiKey),
                                  ('client_secret',apiSecret),
                                  ('refresh_token',afm.access_token),
                                  ('grant_type','refresh_token')])
    req = urllib2.Request(oAuthConfig['oauth_exchange_url'],queryArgs) 
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())

    accessToken = resJSON['access_token']

    # get some activities from the plus activity stream
    req = urllib2.Request('https://www.googleapis.com/plus/v1/people/me/activities/public?access_token=%s' % accessToken)
    res = urllib2.urlopen(req)
    activitiesJSON = json.loads(res.read())
  
    for activity in activitiesJSON['items']:

      if activity['kind'] == 'plus#activity':

        eventId = activity['id']
        eventTimestamp = datetime.strptime(activity['published'],'%Y-%m-%dT%H:%M:%S.%fZ')

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

        eventURL = activity['url']

        caption = activity['title']

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
