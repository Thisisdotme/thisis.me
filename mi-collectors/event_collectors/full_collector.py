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
  
  # profile image
  defaultProfileImageUrl = None

  def __init__(self,dbSession,afm,now,filename,mapper,writer,rawFilename,rawMapper,rawWriter,lastUpdateTime,mostRecentEventId,mostRecentEventTimestamp,defaultProfileImageUrl):
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
    
    self.defaultProfileImageUrl = defaultProfileImageUrl


'''
This is the superclass for all collectors.  It provides a common infrastructure for all collectors
'''
class FullCollector(object):
  '''
  classdocs
  '''
  lookbackWindow = datetime.now () - timedelta (days = 365)
  incremental = True

  @classmethod
  def eventsFromJSON(cls,collector,rawJSON):
    pass

  '''
  Constructor
  '''
  def __init__(self,s3Bucket, aws_access_key,aws_secret_key):
    #self.init_logger()
    self.log = logging.getLogger('driver')
    self.s3Bucket = s3Bucket
    self.awsAccessKey = aws_access_key
    self.awsSecretKey = aws_secret_key
    self.incremental = True
    self.s3Connection = S3Connection(self.awsAccessKey, self.awsSecretKey)


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
      bucket = self.s3Connection.get_bucket(self.s3Bucket)
      # refined
      for jsonType in ['refined','raw']:
        for key in bucket.get_all_keys(prefix='%s/%s.%s.' % (jsonType,afm.author_id,self.getFeatureName())):
          bucket.delete_key(key)

  @abstractmethod
  def getFeatureName(self):
    pass

  '''
  Utility functions
  '''
  def getLookbackWindow(self):
    return self.lookbackWindow

  def makeFilename(self,authorId,now,varient):
    return '%s.%s.%d.%s.csv' % (authorId, self.getFeatureName(), mktime(now.timetuple()), varient)


  def beginTraversal(self,dbSession,afm,defaultProfileImageUrl):
    now = datetime.now()
    filename = self.makeFilename(afm.author_id,now,"refined")
    mapper = open(filename,'wb')
    writer = csv.writer(mapper)
    rawFilename = self.makeFilename(afm.author_id,now,"raw")
    rawMapper = open(rawFilename,'wb')
    rawWriter = csv.writer(rawMapper)
    mostRecentEventId = afm.most_recent_event_id if self.incremental else None
    mostRecentEventTimestamp = afm.most_recent_event_timestamp if self.incremental else None
    lastUpdateTime = afm.last_update_time if self.incremental else None

    return FullCollectorState(dbSession,afm,now,filename,mapper,writer,rawFilename,rawMapper,rawWriter,lastUpdateTime,mostRecentEventId,mostRecentEventTimestamp,defaultProfileImageUrl)


  def endTraversal(self,state,authorName):

    # before uploading to s3 it's important to close the files to flush the buffers 
    state.mapper.close()

    # copy new mapper file to s3 if the file exists and has a non-zero size
    #
    if os.path.exists(state.filename):

      # only if the file-size is greater than 0 do we want to upload to s3
      if os.path.getsize(state.filename) > 0:
        bucket = self.s3Connection.get_bucket(self.s3Bucket)
        k = Key(bucket)
        
        # output refined JSON
        k.key = 'normalized/%s.%s.%d.csv' % (state.authorId,self.getFeatureName(),mktime(state.now.timetuple()))
        k.set_contents_from_filename(state.filename)
        
      # remove the file from the local file-system
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
        # output to MySQL
        #
        url = event.getEventURL()
        caption = event.getEventCaption()
        content = event.getEventContent()
        photo = event.getEventPhoto();
        auxillaryContent = event.getAuxillaryContent()
        profileImageUrl = event.getProfileImageUrl() if event.getProfileImageUrl() else state.defaultProfileImageUrl

        featureEvent = FeatureEvent(state.afm.id,event.getEventId(),eventTime,url,caption,content,photo,auxillaryContent,profileImageUrl,json.dumps(event.getNativePropertiesObj()))
        state.dbSession.add(featureEvent)
        state.dbSession.flush()

        #
        # output to s3
        #
        # normalized
        normalizedDict = event.toNormalizedObj()
        normalizedDict['id'] = featureEvent.id
        state.writer.writerow([state.authorId,json.dumps(normalizedDict,sort_keys=True)])
        
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
