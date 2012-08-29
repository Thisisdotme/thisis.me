import fcntl
import os
import re


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
