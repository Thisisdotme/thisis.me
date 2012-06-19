import fcntl
import os


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
