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

EVENT_KEY = 'twitter-events'
SUMMARY_KEY = 'twitter-highlights'

SIGNAL_KEY = '_SUCCESS'

HIGHLIGHT_TYPE = 'twitter_retweet_30d'

'''
Temporary tables for processing highlights

'''

class TmpTwitterSummary(Base):
  __table__ = Table('tmp_twitter_summary', Base.metadata,
                  Column('author_id', Integer),
                  Column('feature_event_id', Integer, primary_key=True),
                  Column('weight', Integer),
                  Column('count', Integer),
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
    return False

  # initialize the db engine & session
  engine = create_engine(config.get('DBConfig','sqlalchemy.url'), encoding='utf-8', echo=False)
  DBSession.configure(bind=engine)

  dbSession = DBSession();

  highlightTypeId, = dbSession.query(HighlightType.id).filter(HighlightType.label==HIGHLIGHT_TYPE).one()

  # get a connection from the DB
  dbConn = dbSession.connection()

  # drop any existing temp tables
  dbSession.execute('DROP TEMPORARY TABLE IF EXISTS %s' % TmpTwitterSummary.__table__.name)

  # create the temp tables
  dbSession.execute(CreateTable(TmpTwitterSummary.__table__).compile(engine).string)


  # transfer all venue files to local machine and transform the JSON to tab delimited for loading
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

        writer.writerow([jsonObj['author_id'],jsonObj['id'],weight,jsonObj['retweet_count']])
        
      infile.close()
      outfile.close()

      trans = dbConn.begin() 
      dbConn.execute('LOAD DATA LOCAL INFILE \'%s\' INTO TABLE %s' % (outFilename,TmpTwitterSummary.__table__.name)) 
      trans.commit()

  dbSession.commit()
  
  transform_to_highlight(dbSession,highlightTypeId)

  # drop the temp tables used for
  dbSession.execute('DROP TEMPORARY TABLE %s' % TmpTwitterSummary.__table__.name)

  # delete the signal file so we don't process these files again
  bucket.delete_key(summarySignalKey)

  return True

def transform_to_highlight(dbSession,highlightTypeId):
  
  # select all events
  for summary,featureEvent,authorName in dbSession.query(TmpTwitterSummary,FeatureEvent,Author.full_name).outerjoin(Highlight,and_(TmpTwitterSummary.feature_event_id==Highlight.feature_event_id,Highlight.highlight_type_id == highlightTypeId)).join(FeatureEvent,TmpTwitterSummary.feature_event_id==FeatureEvent.id).join(Author,TmpTwitterSummary.author_id==Author.id).filter(Highlight.feature_event_id == None):
  
    print make_highlight_content(authorName,summary,featureEvent)

    # Insert the highlight....
    highlight = Highlight(highlightTypeId, featureEvent.id, summary.weight, featureEvent.caption, make_highlight_content(authorName,summary,featureEvent),json.dumps({"count":summary.count}))
    dbSession.add(highlight)
    dbSession.flush()
    
    # ...and the single event mapping.
    highlightMap = HighlightFeatureEventMap(highlight.id,featureEvent.id)
    dbSession.add(highlightMap)
    dbSession.flush()

  # delete anything that no longer exists as a highlight  
  result = dbSession.execute('DELETE h FROM highlight h left outer join %s tmp on h.feature_event_id = tmp.feature_event_id WHERE tmp.feature_event_id IS NULL AND h.highlight_type_id = %d' % (TmpTwitterSummary.__table__.name,highlightTypeId))

  # update anything that has a different weight
  result = dbSession.execute('UPDATE highlight h INNER JOIN %s tmp ON tmp.feature_event_id = h.feature_event_id INNER JOIN feature_event fe ON h.feature_event_id = fe.id INNER JOIN author_feature_map afm ON fe.author_feature_map_id = afm.id  INNER JOIN author a ON afm.author_id = a.id SET h.content = CONCAT(a.full_name,\'\'\'s post has a recency & retweet weight of \',tmp.weight), h.weight = tmp.weight, h.auxillary_content = CONCAT(\'{"count":\',tmp.count,\'}\') WHERE tmp.weight != h.weight AND h.highlight_type_id = %d' % (TmpTwitterSummary.__table__.name,highlightTypeId))

  dbSession.commit()

def make_highlight_content(authorName,summary,featureEvent):
  # !!!! The following string also appears in the SQL UPDATE clause above
  return '%s\'s post has a recency & retweet weight of %d' % (authorName,summary.weight)
  
if __name__ == '__main__':
  if main(sys.argv):
    print 'Successfully transferred and loaded twitter highlight data'
    sys.exit(0)
  else:
    sys.exit(1)
  
