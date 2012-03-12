#!/usr/bin/env python
'''
Created on Dec 14, 2011

@author: howard
'''

import sys, json

from ConfigParser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mi_utils.app_base import AppBase

from event_collectors.collector_factory import EventCollectorFactory

DBSession = sessionmaker()

class CollectorDriver(AppBase):

  def display_usage(self):
    return "Usage: " + self.name + ".py [-incremental | -full]\nExample: " + self.name + ".py -incremental"

  def init_args(self):
    
    self.option_parser.add_option("-i", "--incremental" , action="store_true", dest="incremental")
    self.option_parser.add_option("-f", "--full", action="store_false", dest="incremental")
    
  def parse_args(self,argsNumber):
    
    (options, args) = self.option_parser.parse_args()
    self.options = options
    self.args = args
    
    if not (len(self.args) == (argsNumber-1) or len(self.args) == argsNumber):
      self.option_parser.print_help()
      sys.exit(self.STATUS_ERROR)  
  
  def main(self):

    # load the config
    config = ConfigParser()
    config.read('config.ini')
    
    # load the oauth config
    oauthfd=open(config.get('OAuthConfig','mi.oauthkey_file'))
    oauthConfig = json.load(oauthfd)
    oauthfd.close()
  
    # read the db url from the config
    dbUrl = config.get('DBConfig','sqlalchemy.url')
    
    # initialize the db engine & session
    engine = create_engine(dbUrl, encoding='utf-8', echo=False)
    DBSession.configure(bind=engine)
   
    dbSession = DBSession()
  
    # for controlling incremental vs. full builds
    incremental = self.options.incremental

    feature = "googleplus"
    collector = EventCollectorFactory.get_collector_for(feature,config.get('AWS','s3_bucket'), config.get('AWS','aws_access_key'), config.get('AWS','aws_secret_key'))
    if collector:
      collector.build_all(dbSession,oauthConfig[feature],incremental)
  
#    for feature, oauthConfig in oauthConfig.iteritems():
#      collector = EventCollectorFactory.get_collector_for(feature,config.get('AWS','s3_bucket'), config.get('AWS','aws_access_key'), config.get('AWS','aws_secret_key'))
#      if collector:
#        try:
#          collector.build_all(dbSession,oauthConfig,incremental)
#        except Exception, e:
#          self.log.error('Collector error: %s' % e)
    
    dbSession.close()
  
    self.log.info( 'Successfully Completed')
  
if __name__=="__main__":

  # Initialize with number of arguments script takes
  sys.exit(CollectorDriver(0).main())
    
  
