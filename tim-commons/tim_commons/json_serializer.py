import json


def dump(value, fp):
  json.dump(value, fp, separators=(',', ':'), sort_keys=True)


def dump_string(value):
  return json.dumps(value, separators=(',', ':'), sort_keys=True)


def normalize_string(value):
  return dump_string(load_string(value))


load = json.load


load_string = json.loads
