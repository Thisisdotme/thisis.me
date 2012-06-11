import os
import logging
import optparse
import socket
import pwd
import datetime

from tim_commons.config import load_configuration


class AppBase:

  STATUS_OK = 0
  STATUS_ERROR = 1
  STATUS_WARNING = 75

  def __init__(self, program_name, config_file='{TIM_CONFIG}/config.ini'):
    self._program_name = program_name
    self._config_file = config_file
    self._option_parser = optparse.OptionParser(usage=self.display_usage(),
                                                prog=program_name)

  def error(self, message):
    self._option_parser.error(message)

  def display_usage(self):
    return 'usage: %prog [options]'

  def init_args(self, ignore):
    pass

  def parse_args(self, args):
    if args:
      self.error('Positional parameters not supported')

  def _handle_args(self):
    self.init_args(self._option_parser)

    (options, args) = self._option_parser.parse_args()
    self.parse_args(args)

    return (options, args)

  def main(self):
    (options, args) = self._handle_args()

    _init_logger(self._program_name)
    config = _load_config(self._config_file)

    self.app_main(config, options, args)


def _init_logger(program_name):
  message = '%(levelname)s %(asctime)s %(thread)d %(pathname)s:%(lineno)d] %(message)s'
  root_logger = logging.getLogger()
  root_logger.addHandler(_create_stderr_handler(message))
  root_logger.addHandler(_create_file_handler(program_name, message))
  root_logger.setLevel(logging.DEBUG)

  # Configure the sqlalchemy logger
  logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def _load_config(config_file):
  return load_configuration(config_file)


def _create_stderr_handler(message_format):
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(logging.Formatter(message_format))

  return handler


def _create_file_handler(program_name, message_format):
  filename_args = {'program': program_name,
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
