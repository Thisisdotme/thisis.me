#!/usr/bin/env python
'''
Created on Mar 7, 2012

@author: howard
'''

import sys, os, csv, json

from ConfigParser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from sqlalchemy import and_;


from boto.s3.connection import S3Connection

from sqlalchemy import Column, Integer
from sqlalchemy.schema import Table

from mi_schema.models import Base, Highlight, HighlightFeatureEventMap, HighlightType, FeatureEvent, Author

DBSession = sessionmaker()

EVENT_KEY = 'linkedin-events'
SUMMARY_KEY = 'linkedin-highlights'

SIGNAL_KEY = '_SUCCESS'

HIGHLIGHT_TYPE = 'linkedin_30d'

'''
Temporary tables for processing Foursquare highlights
'''

class TmpLinkedInConnects(Base):
  __table__ = Table('tmp_linkedin_connect', Base.metadata,
                    Column('author_id', Integer),
                    Column('feature_event_id', Integer, primary_key=True),
                    prefixes=['TEMPORARY'])


class TmpLinkedInSummary(Base):
  __table__ = Table('tmp_linkedin_summary', Base.metadata,
                  Column('author_id', Integer),
                  Column('time',Integer),
                  Column('feature_event_id', Integer, primary_key=True),
                  Column('count', Integer),
                  Column('weight', Integer),
                  prefixes=['TEMPORARY'])
  

def main(argv):

  # load the config
  config = ConfigParser()
  config.read(os.path.join(os.path.split(argv[0])[0] if not None else '','config.ini'))

  # load AWS config
  awsConfig = ConfigParser()
  awsConfig.read(config.get('Common','aws'))
  
  aws_access_key = awsConfig.get('AWS','aws_access_key')
  aws_secret_key = awsConfig.get('AWS','aws_secret_key')
  output_bucket = awsConfig.get('AWS','emr_output_bucket')
  
  s3Connection = S3Connection(aws_access_key, aws_secret_key)

  # check if output is ready for processing
  bucket = s3Connection.get_bucket(output_bucket)

  summarySignalKeyName = '%s/%s' % (SUMMARY_KEY,SIGNAL_KEY)
  
  # turn the bucket references into connection keys
  summarySignalKey = bucket.get_key(summarySignalKeyName)
 
  # if either are none then there's nothing to process
  if summarySignalKey is None:
    print 'No data available (missing %s)' % SIGNAL_KEY
    return False

  # initialize the db engine & session
  engine = create_engine(config.get('DBConfig','sqlalchemy.url'), encoding='utf-8', echo=False)
  DBSession.configure(bind=engine)

  dbSession = DBSession();

  highlightTypeId, = dbSession.query(HighlightType.id).filter(HighlightType.label==HIGHLIGHT_TYPE).one()

  # get a connection from the DB
  dbConn = dbSession.connection()

  # drop the tables used for
  dbSession.execute('DROP TEMPORARY TABLE IF EXISTS %s' % TmpLinkedInConnects.__table__.name)
  dbSession.execute('DROP TEMPORARY TABLE IF EXISTS %s' % TmpLinkedInSummary.__table__.name)

  # create the temp tables
  dbSession.execute(CreateTable(TmpLinkedInConnects.__table__).compile(engine).string)
  dbSession.execute(CreateTable(TmpLinkedInSummary.__table__).compile(engine).string)

  # transfer all connect files to local machine and transform the JSON into tab delimited for loading
  # into MySQL
  for key in bucket.get_all_keys(prefix=EVENT_KEY):
    
    basename = os.path.basename(key.name)
    
    if basename != SIGNAL_KEY:

      if os.path.exists(basename):
        os.remove(basename)

      key.get_contents_to_filename(basename)

      # read through the file and transform to tab delimited
      infile = open(basename, "rb")
      reader = csv.reader(infile,delimiter='\t')
      
      outFilename = '%s.%s.txt' % (EVENT_KEY,basename)
      outfile = open(outFilename,'wb')
      writer = csv.writer(outfile,delimiter='\t')
      
      for row in reader:

        jsonStr = row[0]
        
        jsonObj = json.loads(jsonStr)

        writer.writerow([jsonObj['0.author_id'],jsonObj['2.id']])
        
      infile.close()
      outfile.close()

      trans = dbConn.begin() 
      dbConn.execute('LOAD DATA LOCAL INFILE \'%s\' INTO TABLE %s' % (outFilename,TmpLinkedInConnects.__table__.name)) 
      trans.commit()


  # transfer all highlight files to local machine and transform the JSON to tab delimited for loading
  # into MySQL
  for key in bucket.get_all_keys(prefix=SUMMARY_KEY):
    
    basename = os.path.basename(key.name)
    
    if basename != SIGNAL_KEY:

      if os.path.exists(basename):
        os.remove(basename)

      key.get_contents_to_filename(basename)

      # read through the file and transform to tab delimited
      infile = open(basename, "rb")
      reader = csv.reader(infile,delimiter='\t')
      
      outFilename = '%s.%s.txt' % (SUMMARY_KEY,basename)
      outfile = open(outFilename,'wb')
      writer = csv.writer(outfile,delimiter='\t')
      
      for row in reader:

        jsonStr = row[0]
        weight = int(row[1])
        
        jsonObj = json.loads(jsonStr)

        writer.writerow([jsonObj['0.author_id'],jsonObj['1.time'],jsonObj['2.id'],jsonObj['3.count'],weight])
        
      infile.close()
      outfile.close()

      trans = dbConn.begin() 
      dbConn.execute('LOAD DATA LOCAL INFILE \'%s\' INTO TABLE %s' % (outFilename,TmpLinkedInSummary.__table__.name)) 
      trans.commit()

  dbSession.commit()
  
  transform_to_highlight(dbSession,highlightTypeId)

  # drop the temp tables used for
  dbSession.execute('DROP TEMPORARY TABLE %s' % TmpLinkedInConnects.__table__.name)
  dbSession.execute('DROP TEMPORARY TABLE %s' % TmpLinkedInSummary.__table__.name)

  # delete the signal file so we don't process these files again
  bucket.delete_key(summarySignalKey)

  return True

def transform_to_highlight(dbSession,highlightTypeId):
  
  # select all events
  for summary,featureEvent,authorName in dbSession.query(TmpLinkedInSummary,FeatureEvent,Author.full_name).outerjoin(Highlight,and_(TmpLinkedInSummary.feature_event_id==Highlight.feature_event_id,Highlight.highlight_type_id == highlightTypeId)).join(FeatureEvent,TmpLinkedInSummary.feature_event_id==FeatureEvent.id).join(Author,TmpLinkedInSummary.author_id==Author.id).filter(Highlight.feature_event_id == None):
  
    highlight = Highlight(highlightTypeId, featureEvent.id, summary.weight, featureEvent.caption, make_highlight_content(authorName,summary),json.dumps({"count":summary.count}))
    dbSession.add(highlight)
    dbSession.flush()
    
    for venue in dbSession.query(TmpLinkedInConnects).filter(TmpLinkedInConnects.author_id==summary.author_id):
      highlightMap = HighlightFeatureEventMap(highlight.id,venue.feature_event_id)
      dbSession.add(highlightMap)
      dbSession.flush()

  # delete anything that no longer exists as a highlight  
  result = dbSession.execute('DELETE h FROM highlight h left outer join %s tfs on h.feature_event_id = tfs.feature_event_id WHERE tfs.feature_event_id IS NULL AND h.highlight_type_id = %d' % (TmpLinkedInSummary.__table__.name,highlightTypeId))

  # update anything that has a different weight
  result = dbSession.execute('UPDATE highlight h INNER JOIN %s tmp ON tmp.feature_event_id = h.feature_event_id INNER JOIN feature_event fe ON h.feature_event_id = fe.id INNER JOIN author_feature_map afm ON fe.author_feature_map_id = afm.id  INNER JOIN author a ON afm.author_id = a.id SET h.content = CONCAT(tmp.count, \' recent new connections\'), h.weight = tmp.weight, h.auxillary_content = CONCAT(\'{"count":\',tmp.count,\'}\') WHERE tmp.weight != h.weight AND h.highlight_type_id = %d' % (TmpLinkedInSummary.__table__.name,highlightTypeId))

  dbSession.commit()

def make_highlight_content(authorName,summary):
  # !!!! The following string also appears in the SQL UPDATE clause above
  return '%s recent new connections' % (summary.count)
  
if __name__ == '__main__':
  if main(sys.argv):
    print 'Successfully transferred and loaded linkedin highlight data'
    sys.exit(0)
  else:
    sys.exit(1)
  
