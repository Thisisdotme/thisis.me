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

BUCKET_KEY = 'linkedin-deduped'

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
  for key in bucket.get_all_keys(prefix=BUCKET_KEY):
    bucket.delete_key(key)

  step = StreamingStep(name='Linkedin event deduper',
                      mapper='s3://%s/dedup_mapper.py linkedin' % script_bucket,
                      reducer='s3://%s/dedup_reducer.py' % script_bucket,
                      input='s3://%s/normalized' % event_bucket,
                      output='s3://%s/%s' % (output_bucket,BUCKET_KEY),
                      action_on_failure='CONTINUE')

  emrConnection.add_jobflow_steps(jobId, step)

  print 'Successfully started streaming steps'

  
if __name__ == '__main__':
  main(sys.argv)
