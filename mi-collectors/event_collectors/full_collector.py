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

from mi_schema.models import Service, AuthorServiceMap, ServiceEvent

INCREMENTAL_OVERLAP = timedelta(hours=1)


class FullCollectorState(object):

  dbSession = None
  asm = None
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

  def __init__(self, dbSession, asm, now, filename, mapper, writer, lastUpdateTime, mostRecentEventId, mostRecentEventTimestamp, defaultProfileImageUrl):
    self.dbSession = dbSession
    self.asm = asm
    self.authorId = asm.author_id
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
  lookbackWindow = datetime.now() - timedelta(days=365)
  incremental = True

  @classmethod
  def eventsFromJSON(cls, collector, rawJSON):
    pass

  '''
  Constructor
  '''
  def __init__(self, s3Bucket, aws_access_key, aws_secret_key):
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
    queries DB for all users that have services installed and call build_one for each
  '''
  def build_all(self,dbSession,oauthConfig,incremental):

    self.log.info('%s build all models for %s beginning...' % ('incremental' if incremental else 'full', self.getServiceName()))

    # get the id for this service
    serviceId, = dbSession.query(Service.id).filter_by(service_name=self.getServiceName()).first()

    # query the db for all users that have the service installed
    for asm in dbSession.query(AuthorServiceMap).filter_by(service_id=serviceId).all():
      self.build_one(asm, dbSession, oauthConfig, incremental)

  '''
  update_one
  '''
  @abstractmethod
  def build_one(self, asm, dbSession, authConfig, incremental):

    # if this is a full rebuild clean on MySQL and s3
    if not incremental:

      # clean MySQL
      asm.last_update_time = None
      asm.most_recent_event_id = None
      asm.most_recent_event_timestamp = None

      dbSession.query(ServiceEvent).filter(ServiceEvent.author_service_map_id == asm.id).delete()

      dbSession.flush()
      dbSession.commit()

      # clean s3
      bucket = self.s3Connection.get_bucket(self.s3Bucket)
      # refined
      for jsonType in ['normalized']:
        for key in bucket.get_all_keys(prefix='%s/%s.%s.' % (jsonType, asm.author_id, self.getServiceName())):
          bucket.delete_key(key)

  @abstractmethod
  def getServiceName(self):
    pass

  '''
  Utility functions
  '''
  def getLookbackWindow(self):
    return self.lookbackWindow

  def makeFilename(self, authorId, now, varient):
    return '%s.%s.%d.%s.csv' % (authorId, self.getServiceName(), mktime(now.timetuple()), varient)

  def beginTraversal(self, dbSession, asm, defaultProfileImageUrl):
    now = datetime.now()
    filename = self.makeFilename(asm.author_id, now, "refined")
    mapper = open(filename, 'wb')
    writer = csv.writer(mapper)
    mostRecentEventId = asm.most_recent_event_id if self.incremental else None
    mostRecentEventTimestamp = asm.most_recent_event_timestamp if self.incremental else None
    lastUpdateTime = asm.last_update_time if self.incremental else None

    return FullCollectorState(dbSession,asm,now,filename,mapper,writer,lastUpdateTime,mostRecentEventId,mostRecentEventTimestamp,defaultProfileImageUrl)

  def endTraversal(self, state, authorName):

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
        k.key = 'normalized/%s.%s.%d.csv' % (state.authorId, self.getServiceName(), mktime(state.now.timetuple()))
        k.set_contents_from_filename(state.filename)

      # remove the file from the local file-system
      os.remove(state.filename)

    # terminate the transaction
    #
    # set the author/service map's last update time
    state.asm.last_update_time = state.now

    # update the most_recent_event_id and most_recent_event_timestamp if changed    
    if state.mostRecentEventId != state.asm.most_recent_event_id or state.mostRecentEventTimestamp != state.asm.most_recent_event_timestamp:
      # update the authorFeatureMap table
      state.asm.most_recent_event_id = state.mostRecentEventId
      state.asm.most_recent_event_timestamp = state.mostRecentEventTimestamp

    state.dbSession.flush()
    state.dbSession.commit()

    self.log.info(json.dumps({'service':self.getServiceName(),
                              'author_name':authorName[0],
                              'total_accepted':state.totalAccepted,
                              'stale_rejected':state.staleRejected,
                              'duplicate_rejected':state.duplicateRejected,
                              'total_requested':state.totalRequested},
                             sort_keys=True))

  def writeEvent(self, event, state):

    def flushIfUnique():
      # check if this is a duplicate of something already in the DB
      #
      count = state.dbSession.query(ServiceEvent.id).filter_by(author_service_map_id=state.asm.id, event_id=event.getEventId()).count()
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
        photo = event.getEventPhoto()
        auxillaryContent = event.getAuxillaryContent()
        profileImageUrl = event.getProfileImageUrl() if event.getProfileImageUrl() else state.defaultProfileImageUrl

        serviceEvent = ServiceEvent(state.asm.id, event.getEventId(), eventTime, url, caption, content, photo, auxillaryContent, profileImageUrl, json.dumps(event.getNativePropertiesObj()))
        state.dbSession.add(serviceEvent)
        state.dbSession.flush()

        #
        # output to s3
        #
        # normalized
        normalizedDict = event.toNormalizedObj()
        normalizedDict['id'] = serviceEvent.id
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
