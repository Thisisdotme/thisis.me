#!/usr/bin/env python
'''
Created on Mar 7, 2012

@author: howard
'''

import sys, os

from ConfigParser import ConfigParser

from boto.emr.connection import EmrConnection
from boto.emr.step import StreamingStep

from boto.s3.connection import S3Connection

DEDUPED_EVENTS_KEY = 'foursquare-deduped'
EVENTS_KEY = 'foursquare-author-venue'
AGGREGATED_KEY = 'foursquare-aggregated'
MINMAX_KEY = 'foursquare-minmax'
SUMMARY_KEY = 'foursquare-highlights'

def main(argv):

  # load the config
  config = ConfigParser()
  config.read(os.path.join(os.path.split(argv[0])[0] if not None else '','config.ini'))

  # load AWS config
  awsConfig = ConfigParser()
  awsConfig.read(config.get('Common','aws'))

  aws_access_key = awsConfig.get('AWS','aws_access_key')
  aws_secret_key = awsConfig.get('AWS','aws_secret_key')
  event_bucket = awsConfig.get('AWS','event_bucket')
  output_bucket = awsConfig.get('AWS','emr_output_bucket')
  script_bucket = awsConfig.get('AWS','script_bucket')
  
  jobId = argv[1]

  emrConnection = EmrConnection(aws_access_key, aws_secret_key)

  s3Connection = S3Connection(aws_access_key, aws_secret_key)

  # clean s3 output
  bucket = s3Connection.get_bucket(output_bucket)
  for key in bucket.get_all_keys(prefix=DEDUPED_EVENTS_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Foursquare event deduper',
                      mapper='s3://%s/dedup_mapper.py foursquare' % script_bucket,
                      reducer='s3://%s/dedup_reducer.py' % script_bucket,
                      input='s3://%s/normalized' % event_bucket,
                      output='s3://%s/%s' % (output_bucket,DEDUPED_EVENTS_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  # clean s3 output
  bucket = s3Connection.get_bucket(output_bucket)
  for key in bucket.get_all_keys(prefix=AGGREGATED_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Foursquare 30-day Collector',
                      mapper='s3://%s/foursquare_30d_mapper.py' % script_bucket,
                      reducer='s3://%s/identity_reducer.py' % script_bucket,
                      input='s3://%s/%s' % (output_bucket,DEDUPED_EVENTS_KEY),
                      output='s3://%s/%s' % (output_bucket,EVENTS_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  # clean s3 output
  bucket = s3Connection.get_bucket(output_bucket)
  for key in bucket.get_all_keys(prefix=EVENTS_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Foursquare Venue Aggregator',
                      mapper='s3://%s/identity_mapper.py' % script_bucket,
                      reducer='s3://%s/foursquare_checkin_aggregator_reducer.py' % script_bucket,
                      input='s3://%s/%s' % (output_bucket,EVENTS_KEY),
                      output='s3://%s/%s' % (output_bucket,AGGREGATED_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  # clean s3 output
  bucket = s3Connection.get_bucket(output_bucket)
  for key in bucket.get_all_keys(prefix=MINMAX_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Foursquare Min/Max Analyzer',
                      mapper='s3://%s/identity_mapper.py' % script_bucket,
                      reducer='s3://%s/foursquare_minmax_reducer.py' % script_bucket,
                      input='s3://%s/%s' % (output_bucket,AGGREGATED_KEY),
                      output='s3://%s/%s' % (output_bucket,MINMAX_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  # clean s3 output
  bucket = s3Connection.get_bucket(output_bucket)
  for key in bucket.get_all_keys(prefix=SUMMARY_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Foursquare Highlighter',
                      mapper='s3://%s/identity_mapper.py' % script_bucket,
                      reducer='s3://%s/foursquare_highlight_reducer.py' % script_bucket,
                      input='s3://%s/%s' % (output_bucket,MINMAX_KEY),
                      output='s3://%s/%s' % (output_bucket,SUMMARY_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  print 'Successfully started foursquare streaming steps'

  
if __name__ == '__main__':
  main(sys.argv)
