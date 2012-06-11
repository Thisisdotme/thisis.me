import os
import sys
import logging
import optparse
import socket
import pwd
import datetime
from abc import abstractmethod

from tim_commons.config import load_configuration


class AppBase:

  STATUS_OK = 0
  STATUS_ERROR = 1
  STATUS_WARNING = 75

  def __init__(self, program_name, argsNums=None, config_file='{TIM_CONFIG}/config.ini'):
    self.program_name = program_name
    self.name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    self._init_logger()
    self.option_parser = optparse.OptionParser(usage=self.display_usage())
    self.init_args()
    if(argsNums == None):
      argsNums = 0
    self.parse_args(argsNums)
    self._load_config(config_file)

  @abstractmethod
  def display_usage(self):
    assert 0, "Usage must be defined"

  def init_args(self):
      pass

  def parse_args(self, argsNums):

    (options, args) = self.option_parser.parse_args()
    self.options = options
    self.args = args
    numSuppliedArgs = len(args)

    # Here we check the type of the parameter in order to decide how to run this
    # method
    if isinstance(argsNums, int):

      if(numSuppliedArgs != argsNums):
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)

    elif isinstance(argsNums, list):

      # if argsNums is a list then we are expecting a min and max args numbers [min,max]
      if(len(argsNums) != 2):
        logging.error("Invalid number of elements in argsNums parameter. Two required")
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)

      minArgsNum = argsNums[0]
      maxArgsNum = argsNums[1]
      if(numSuppliedArgs < minArgsNum):
        logging.error("Minimum of %s arguments required, only %s supplied",
                       minArgsNum,
                       numSuppliedArgs)
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)

      if(maxArgsNum != None and numSuppliedArgs > maxArgsNum):
        logging.error("Maximum of %s arguments required, %s supplied",
                       maxArgsNum,
                       numSuppliedArgs)
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)

    else:
        logging.error("Unrecognized argsNums parameter")
        self.option_parser.print_help()
        sys.exit(self.STATUS_ERROR)

  def _init_logger(self):
    message = '%(levelname)s %(asctime)s %(thread)d %(pathname)s:%(lineno)d] %(message)s'
    root_logger = logging.getLogger()
    root_logger.addHandler(self._create_stderr_handler(message))
    root_logger.addHandler(self._create_file_handler(message))
    root_logger.setLevel(logging.DEBUG)

    # Configure the sqlalchemy logger
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    self.log = root_logger

  def _load_config(self, config_file):
    self.config = load_configuration(config_file)

  def _create_stderr_handler(self, message_format):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(message_format))

    return handler

  def _create_file_handler(self, message_format):
    filename_args = {'program': self.program_name,
                     'hostname': socket.gethostname(),
                     'user': pwd.getpwuid(os.getuid())[0],
                     'date': datetime.datetime.utcnow().date().isoformat(),
                     'time': datetime.datetime.utcnow().time().isoformat(),
                     'pid': os.getpid()}
    filename = '/tmp/{program}.{hostname}.{user}.log.{date}.{time}.{pid}'.format(**filename_args)

    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(message_format))

    return handler

  @abstractmethod
  def main(self):
    assert 0, "Usage must be defined"
