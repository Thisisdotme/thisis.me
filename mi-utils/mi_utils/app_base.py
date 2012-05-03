#! /usr/bin/env python

'''
Created on Feb 19, 2012

@author: howard
'''

import os,sys,logging,optparse
from configobj import ConfigObj
from abc import abstractmethod

class AppBase(object):
  '''
  classdocs
  '''

  CONFIG_FILE = 'config.ini'

  STATUS_OK = 0
  STATUS_ERROR = 1 
  STATUS_WARNING = 75
  
  def __init__(self,argsNums):
    '''
    Constructor
    '''
    self.name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    self.init_logger()    
    self.option_parser = optparse.OptionParser(usage=self.display_usage())
    self.init_args()
    if(argsNums==None):
      argsNums=0
    self.parse_args(argsNums)
    self.load_config()

  @abstractmethod
  def display_usage(self):
    assert 0, "Usage must be defined"
    
  def init_args(self):
      pass
    
  def parse_args(self,argsNums):
      
    (options, args) = self.option_parser.parse_args()
    self.options = options
    self.args = args
    numSuppliedArgs = len(args)
    
    # Here we check the type of the parameter in order to decide how to run this method
    if isinstance(argsNums, int):
      
      if(numSuppliedArgs != argsNums):
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)
        
    elif isinstance(argsNums, list):
      
      # if argsNums is a list then we are expecting a min and max args numbers [min,max]
      if(len(argsNums) != 2):
        self.log.error("Invalid number of elements in argsNums parameter.  Two required")
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)
      
      minArgsNum = argsNums[0]
      maxArgsNum = argsNums[1]
      if(numSuppliedArgs < minArgsNum):
        self.log.error("Minimum of %s arguments required, only %s supplied" % (minArgsNum,numSuppliedArgs))
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)
        
      if(maxArgsNum != None and numSuppliedArgs > maxArgsNum):
        self.log.error("Maximum of %s arguments required, %s supplied" % (maxArgsNum,numSuppliedArgs))
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)
      
    else:
        self.log.error("Unrecognized argsNums parameter")
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)
      

  def init_logger(self):
    #create logger
    logger = logging.getLogger(self.name)
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


  def load_config(self):

    if not os.path.exists(self.CONFIG_FILE):
      self.config = None
      return

    self.config = ConfigObj()

    baseConfig = ConfigObj(self.CONFIG_FILE, interpolation=False)

    # after walking all key/values in the include section this list will hold
    # the ConfigObj for each included config 
    mergeConfigs = []

    def walk_include_callback(section, key):
      includeFile = section[key] % {'TIM_CONFIG': os.environ['TIM_CONFIG']}
      if not os.path.exists(includeFile):
        self.log.warn('Config file reference in include section does not exist: %s' % section[key])
      else:
        mergeConfigs.append(ConfigObj(includeFile))

    # load the configs for the include section
    common = baseConfig['include']
    common.walk(walk_include_callback)
    
    # remove the include section
    baseConfig.pop('include',None)
    
    for config in mergeConfigs:
      self.config.merge(config)
    self.config.merge(baseConfig)
      
  @abstractmethod
  def main(self): 
    assert 0, "Usage must be defined"
        