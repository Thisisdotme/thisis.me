import unittest

from tim_commons.serializer import load_string, dump_string, normalize_string


class JsonTestCase(unittest.TestCase):
  string = '{"hello":"world","int":1234}'

  def test_json(self):
    obj = load_string(self.string)
    self.assertEqual(obj['hello'], 'world')
    self.assertEqual(obj['int'], 1234)

    result = dump_string(obj)
    self.assertEqual(self.string, result)

  def test_normalize(self):
    normal_string = normalize_string(self.string)
    self.assertEqual(normal_string, self.string)
