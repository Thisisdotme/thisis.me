import json


def dump(value, fp):
  json.dump(value, fp, separators=(',', ':'))


def dump_string(value):
  return json.dumps(value, separators=(',', ':'))


load = json.load

load_string = json.loads
