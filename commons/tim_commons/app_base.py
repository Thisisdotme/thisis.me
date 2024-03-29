import os
import logging
import optparse
import pwd
import daemon
import setproctitle

import tim_commons.config


class AppBase:

  STATUS_OK = 0
  STATUS_ERROR = 1
  STATUS_WARNING = 75

  def __init__(self, program_name, config_file='{TIM_CONFIG}/config.ini', daemon_able=False):
    self._program_name = program_name
    self._config_file = config_file
    self._daemon_able = daemon_able
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

    # Add default option
    if self._daemon_able:
      self._option_parser.add_option('--daemon',
                                     dest='daemon',
                                     action='store_true',
                                     default=False,
                                     help='Start as a daemon')

    (options, args) = self._option_parser.parse_args()
    self.parse_args(args)

    return (options, args)

  def main(self):
    setproctitle.setproctitle(self._program_name)

    (options, args) = self._handle_args()
    is_daemon = _is_daemon(options)

    # NOTE: This return stuff doesn't work in a daemon. I don't think there is a way to make
    # this work..
    try:
      config = _load_config(self._config_file)
      if is_daemon:
        pwd_database = pwd.getpwnam(os.environ['TIM_USER'])
        with daemon.DaemonContext(
            working_directory='/',
            pidfile=tim_commons.PidFileContext('/var/run/tim/{0}.pid'.format(self._program_name)),
            umask=0o022,
            files_preserve=list(reversed(range(2048))),
            uid=pwd_database.pw_uid,
            gid=pwd_database.pw_gid,
            detach_process=True):
          self._main(is_daemon, config, options, args)
      else:
        self._main(is_daemon, config, options, args)
      return 0
    except:
      logging.exception('Unexpected error.')
      return 1

  def _main(self, is_daemon, config, options, args):
    tim_commons.init_logger(self._program_name, is_daemon)
    self.app_main(config, options, args)


def _is_daemon(options):
  try:
    is_daemon = options.daemon
  except AttributeError:
    is_daemon = False

  return is_daemon


def _load_config(config_file):
  return tim_commons.config.load_configuration(config_file)
