import unittest

from tim_commons import json_serializer


class JsonTestCase(unittest.TestCase):
  string = '{"hello":"world","int":1234}'

  def test_json(self):
    obj = json_serializer.load_string(self.string)
    self.assertEqual(obj['hello'], 'world')
    self.assertEqual(obj['int'], 1234)

    result = json_serializer.dump_string(obj)
    self.assertEqual(self.string, result)

  def test_normalize(self):
    normal_string = json_serializer.normalize_string(self.string)
    self.assertEqual(normal_string, self.string)
