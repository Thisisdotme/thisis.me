'''
Created on Dec 14, 2011

@author: howard
'''

import json

from datetime import datetime

from mi_schema.models import FeatureEvent

from collector import Collector

from instagram.client import InstagramAPI
from instagram.models import Point

class InstagramCollector(Collector):
  '''
  classdocs
  '''
  featureName = 'instagram'
  
  def __init__(self):
    '''
    Constructor
    '''
    super(InstagramCollector,self).__init__()
    
  
  def update_author(self, afm, dbSession, oauthConfig):

    api = InstagramAPI(access_token=afm.access_token)
    
    user = api.user()
    
    print 'instagram user %s' % user
    
    currUpdateTime = datetime.utcnow()

    # instagram ids are a combination of media-id and user-id.  For comparison purposes we
    # want just the media-id as a long.  We'll maintain the max. for both the full id and just
    # the media id (as a long).
    mostRecentEventId = afm.most_recent_event_id
    mostRecentEventTimestamp = afm.most_recent_event_timestamp
    if afm.most_recent_event_id:
      highestMediaId = long(afm.most_recent_event_id[:afm.most_recent_event_id.index('_')])
    else:
      highestMediaId = None 

    recent_media, next = api.user_recent_media(min_id=afm.most_recent_event_id)
    
    for media in recent_media:
      
      instagramId = media.id
      
      # get the actual id part
      mediaId = long(instagramId[:instagramId.index('_')])

      # check if we already have this
      count = dbSession.query(FeatureEvent.id).filter_by(author_feature_map_id=afm.id,event_id=instagramId).count()
      if count > 0:
        continue
      
      # store the highest event id
      if highestMediaId == None or mediaId > highestMediaId:
        highestMediaId = mediaId
        mostRecentEventTimestamp = media.created_time
        mostRecentEventId = instagramId
 
      createTime = media.created_time

      if hasattr(media, 'caption'):
        caption = media.caption
      else:
        caption = None

      url = media.link
      
      lowRes = media.images['low_resolution']
      thumbnail = media.images['thumbnail']
      stdRes = media.images['standard_resolution']
      
      # if location information exists collect the attributes into a dict for conversion to JSON
      if media.location and media.location.id:
        
        location = {}

        for loc_property, loc_value in vars(media.location).iteritems():

          # special handling for points
          if isinstance (loc_value,Point):
            point = {}
            for obj_property, obj_value in vars(loc_value).iteritems():
              point[obj_property] = obj_value
            loc_value = point

          location[loc_property] = loc_value
      else:
        location = None
      
      auxData = {'location': location,
                 'images':{'low_resolution':{'url':lowRes.url,'width':lowRes.width,'height':lowRes.height},
                           'thumbnail':{'url':thumbnail.url,'width':thumbnail.width,'height':thumbnail.height},
                           'standard_resolution':{'url':stdRes.url,'width':stdRes.width,'height':stdRes.height}
                          }
                 }
      auxDataStr = json.dumps(auxData)

      featureEvent = FeatureEvent(afm.id,instagramId,createTime,url,caption,lowRes.url,auxDataStr)

      dbSession.add(featureEvent)
      dbSession.flush()

    # set the author/feature map's last update time
    afm.last_update_time = currUpdateTime

    # update the most_recent_event_id if changed    
    if mostRecentEventId != afm.most_recent_event_id:
      # update the authorFeatureMap table
      afm.most_recent_event_id = mostRecentEventId
      afm.most_recent_event_timestamp = mostRecentEventTimestamp

    dbSession.flush()
    dbSession.commit()
    
    return
      