'''
Created on Feb 15, 2012

@author: howard
'''
import logging, sys, os, json, csv

from abc import abstractmethod
from datetime import datetime, timedelta
from time import mktime

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from mi_schema.models import Feature, AuthorFeatureMap, FeatureEvent

INCREMENTAL_OVERLAP = timedelta (hours = 1)
S3_BUCKET = 'events.v1.mobileidentity.me'


class FullCollectorState(object):
  dbSession = None
  afm = None
  authorId = None
  now = None
  filename = None
  mapper = None
  writer = None
  
  # counters for various metrics
  totalRequested = 0
  totalAccepted = 0
  staleRejected = 0
  duplicateRejected = 0
  
  # state from the last traversal
  lastUpdateTime = None
  mostRecentEventId = 0
  mostRecentEventTimestamp = None
  baselineLastUpdateTime = None

  def __init__(self,dbSession,afm,now,filename,mapper,writer,lastUpdateTime,mostRecentEventId,mostRecentEventTimestamp):
    self.dbSession = dbSession
    self.afm = afm
    self.authorId = afm.author_id
    self.now = now
    self.filename = filename
    self.mapper = mapper
    self.writer = writer
    self.lastUpdateTime = lastUpdateTime
    self.mostRecentEventId = mostRecentEventId
    self.mostRecentEventTimestamp = mostRecentEventTimestamp
    self.baselineLastUpdateTime = lastUpdateTime - INCREMENTAL_OVERLAP if mostRecentEventTimestamp else None


'''
This is the superclass for all collectors.  It provides a common infrastructure for all collectors
'''
class FullCollector(object):
  '''
  classdocs
  '''
  log = None
  s3Connection = None
  writer = None
  lookbackWindow = datetime.now () - timedelta (days = 365)
  incremental = True

  @classmethod
  def eventsFromJSON(cls,collector,rawJSON):
    pass

  '''
  Constructor
  '''
  def __init__(self,aws_access_key,aws_secret_key):
    #self.init_logger()
    self.log = logging.getLogger('driver')
    self.s3Connection = S3Connection(aws_access_key, aws_secret_key)


  def init_logger(self):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    #create console handler and set level to debug                                                                                                                                       
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    #create formatter                                                                                                                                                                    
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] - %(message)s")

    #add formatter to ch                                                                                                                                                                 
    ch.setFormatter(formatter)

    #add ch to logger                                                                                                                                                                    
    logger.addHandler(ch)

    self.log = logger

  '''
  build_all
    queries DB for all users that have feature installed and call updateAuthor for each
  '''
  def build_all(self,dbSession,oauthConfig,incremental):
    
    self.log.info('%s build all models for %s beginning...' % ('incremental' if incremental else 'full', self.getFeatureName()))

    # get the feature-id for this feature
    featureId, = dbSession.query(Feature.id).filter_by(feature_name=self.getFeatureName()).first()

    # query the db for all users that have the feature installed
    for afm in dbSession.query(AuthorFeatureMap).filter_by(feature_id=featureId).all():

#      # get the name of the author  
#      authorName, = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()
#      self.log.info('querying %s for author "%s"' % (self.getFeatureName(),authorName))
  
      self.build_one(afm,dbSession,oauthConfig,incremental)

  '''
  update_one
  '''
  @abstractmethod
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    # if this is a full rebuild clean on MySQL and s3 
    if not incremental:

      # clean MySQL
      afm.last_update_time = None
      afm.most_recent_event_id = None
      afm.most_recent_event_timestamp = None

      dbSession.query(FeatureEvent).filter(FeatureEvent.author_feature_map_id==afm.id).delete()
      
      dbSession.flush()
      dbSession.commit()

      # clean s3
      bucket = self.s3Connection.get_bucket(S3_BUCKET)
      for key in bucket.get_all_keys(prefix='%s/%s/' % (afm.author_id,self.getFeatureName())):
        bucket.delete_key(key)

  @abstractmethod
  def getFeatureName(self):
    pass

  '''
  Utility functions
  '''
  def getLookbackWindow(self):
    return self.lookbackWindow

  def makeFilename(self,authorId,now):
    return '%s.%s.%d.csv' % (authorId, self.getFeatureName(), mktime(now.timetuple()))


  def beginTraversal(self,dbSession,afm):
    now = datetime.now()
    filename = self.makeFilename(afm.author_id,now)
    mapper = open(filename,'wb')
    writer = csv.writer(mapper)
    mostRecentEventId = afm.most_recent_event_id if self.incremental else None
    mostRecentEventTimestamp = afm.most_recent_event_timestamp if self.incremental else None
    lastUpdateTime = afm.last_update_time if self.incremental else None

    return FullCollectorState(dbSession,afm,now,filename,mapper,writer,lastUpdateTime,mostRecentEventId,mostRecentEventTimestamp)


  def endTraversal(self,state,authorName):

    state.mapper.close()

    # copy new mapper file to s3 if the file exists and has a non-zero size
    #
    if (os.path.exists(state.filename) and os.path.getsize(state.filename) > 0):
      bucket = self.s3Connection.get_bucket(S3_BUCKET)
      k = Key(bucket)
      k.key = '%s/%s/%d.csv' % (state.authorId,self.getFeatureName(),mktime(state.now.timetuple()))
      k.set_contents_from_filename(state.filename)
      os.remove(state.filename)

    # terminate the transaction
    #
    # set the author/feature map's last update time
    state.afm.last_update_time = state.now

    # update the most_recent_event_id and most_recent_event_timestamp if changed    
    if state.mostRecentEventId != state.afm.most_recent_event_id or state.mostRecentEventTimestamp != state.afm.most_recent_event_timestamp:
      # update the authorFeatureMap table
      state.afm.most_recent_event_id = state.mostRecentEventId
      state.afm.most_recent_event_timestamp = state.mostRecentEventTimestamp

    state.dbSession.flush()
    state.dbSession.commit()

    self.log.info(json.dumps({'feature':self.getFeatureName(),
                              'author_name':authorName[0],
                              'total_accepted':state.totalAccepted,
                              'stale_rejected':state.staleRejected,
                              'duplicate_rejected':state.duplicateRejected,
                              'total_requested':state.totalRequested},
                             sort_keys=True))

  def writeEvent(self,event,state):

    def flushIfUnique():
      # check if this is a duplicate of something already in the DB
      #
      count = state.dbSession.query(FeatureEvent.id).filter_by(author_feature_map_id=state.afm.id,event_id=event.getEventId()).count()
      if count > 0:
        state.duplicateRejected = state.duplicateRejected + 1
      else:

        #
        # update the most-recent event timestamp state if appropriate
        #
        eventTimestamp = event.getEventTime()
        if not state.mostRecentEventTimestamp or eventTimestamp > state.mostRecentEventTimestamp:
          state.mostRecentEventId = event.getEventId()
          state.mostRecentEventTimestamp = eventTimestamp

        #
        # output to s3
        #
        state.writer.writerow([state.authorId,json.dumps(event.toJSON(),sort_keys=True)])
        
        #
        # output to MySQL
        #
        url = event.getEventURL()
        caption = event.getEventCaption()
        content = event.getEventContent()
        photo = event.getEventPhoto();
        auxillaryContent = event.getAuxillaryContent()

        featureEvent = FeatureEvent(state.afm.id,event.getEventId(),eventTime,url,caption,content,photo,auxillaryContent)
        state.dbSession.add(featureEvent)
        state.dbSession.flush()

        state.totalAccepted = state.totalAccepted + 1
     
    # check if we're within the lookback window
    #
    state.totalRequested = state.totalRequested + 1

    eventTime = event.getEventTime()
    if eventTime >= self.getLookbackWindow():

      # check if the event is more recent that our baseline
      # 
      if state.baselineLastUpdateTime:
        if eventTime >= state.baselineLastUpdateTime:
          flushIfUnique()
        else:
          state.staleRejected = state.staleRejected + 1
      else:
        # continue with add
        flushIfUnique()

    else:
      state.staleRejected = state.staleRejected + 1
