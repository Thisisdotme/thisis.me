'''
Created on Dec 14, 2011

@author: howard
'''

import json
from datetime import datetime
import urllib2

from mi_schema.models import FeatureEvent

from collector import Collector


class FoursquareCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'foursquare'

  def __init__(self):
    '''
    Constructor
    '''
    super(FoursquareCollector,self).__init__()

 
  def update_author(self, afm, dbSession, oauthConfig):

    currUpdateTime = datetime.utcnow()

    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = prevRecentEventTimestamp = afm.most_recent_event_timestamp

    auxData = json.loads(afm.auxillary_data)
    userId = auxData['id']
    
    url = oauthConfig['url'] % ('users/self/checkins',afm.access_token)

    # users/self/checkins
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    postsJSON = json.loads(res.read())

    if postsJSON['meta']['code'] != 200:
      raise Exception('Foursquare error response: %s' % postsJSON['meta']['code'])

    # for element in the feed
    for post in postsJSON['response']['checkins']['items']:

      eventTimestamp = datetime.utcfromtimestamp(int(post['createdAt']))
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

      eventURL = None

      caption = post['venue'].get('name','')
      shout = post.get('shout','')
      address = post['venue']['location'].get('address')
      city = post['venue']['location'].get('city')

      # define location
      location = None
      if (address and city):
        location = '%s, %s' % (address,city)
      elif address:
        location = address
      else:
        location = city
      
      location = ' (%s)' % location if location else ''
      
      source = post['source'].get('name','')
      source = ' (Source: %s)' % source if source else ''
      
      caption = '%s%s' % (caption,location)
      content = '%s%s' % (shout, source)
      
      # add the event to the db
      featureEvent = FeatureEvent(afm.id,eventId,eventTimestamp,eventURL,caption,content,None)
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
      