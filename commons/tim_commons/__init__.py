import fcntl
import socket
import pwd
import os
import re
import logging
import datetime


def total_seconds(td):
  return float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6


def prune_dictionary(source_dict, prune_dict):
  for prune_key, prune_value in prune_dict.iteritems():
    if not prune_key in source_dict:
      continue
    if prune_value:
      prune_dictionary(source_dict[prune_key], prune_value)
    else:
      del source_dict[prune_key]


def to_bool(string):
  if string in ['True', 'true']:
    return True
  elif string in ['False', 'false']:
    return False
  else:
    raise ValueError('invalid literal for to_bool(): {0}'.format(string))


class PidFileContext():
  def __init__(self, path):
    self._path = path

  def __enter__(self):
    self._pidfile = open(self._path, "a+")

    try:
      fcntl.flock(self._pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
      raise SystemExit("Already running according to " + self._path)

    self._pidfile.seek(0)
    self._pidfile.truncate()
    self._pidfile.write(str(os.getpid()))
    self._pidfile.flush()
    self._pidfile.seek(0)

  def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
    try:
      self._pidfile.close()
    except IOError as err:
      # ok if file was just closed elsewhere
      if err.errno != 9:
        raise
    os.remove(self._path)


def extract_uri_from_text(text):
  """Given a text string, returns all the urls we can find in it."""
  return url_re.findall(text)


# Compile the regular expression
urls = '(?: {0})'.format('|'.join("""http https""".split()))
ltrs = r'\w'
gunk = r'/#~:.?+=&%@!\-'
punc = r'.:?\-'
any_char = '{ltrs}{gunk}{punc}'.format(ltrs=ltrs, gunk=gunk, punc=punc)

url = r"""
    \b                           # start at word boundary
        {urls}    :              # need resource and a colon
        [{any_char}]  +?         # followed by one or more
                                 #  of any valid character, but
                                 #  be conservative and take only
                                 #  what you need to....
    (?=                          # look-ahead non-consumptive assertion
            [{punc}]*            # either 0 or more punctuation
            (?:   [^{any_char}]  #  followed by a non-url char
                |                #   or end of the string
                  $
            )
    )
    """.format(urls=urls, any_char=any_char, punc=punc)

url_re = re.compile(url, re.VERBOSE | re.MULTILINE)


def normalize_uri(uri):
  # Before we were removing the query parameters from the URI but that is not correct
  # for some websites that use query paramters to identify pages
  return uri


def init_logger(program_name, is_daemon=False):
  message = '%(levelname)s %(asctime)s %(thread)d %(pathname)s:%(lineno)d] %(message)s'
  root_logger = logging.getLogger()
  if not is_daemon:
    root_logger.addHandler(_create_stderr_handler(message))
  root_logger.addHandler(_create_file_handler(program_name, message))
  root_logger.setLevel(logging.DEBUG)

  # Configure the sqlalchemy logger
  logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def _create_stderr_handler(message_format):
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(logging.Formatter(message_format))

  return handler


def _create_file_handler(program_name, message_format):
  filename_args = {'program': program_name,
                   'hostname': socket.gethostname(),
                   'user': pwd.getpwuid(os.getuid()).pw_name,
                   'date': datetime.datetime.utcnow().date().isoformat(),
                   'time': datetime.datetime.utcnow().time().isoformat(),
                   'pid': os.getpid()}
  filename = '/tmp/{program}.{hostname}.{user}.log.{date}.{time}.{pid}'.format(**filename_args)

  handler = logging.FileHandler(filename)
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(logging.Formatter(message_format))

  return handler
