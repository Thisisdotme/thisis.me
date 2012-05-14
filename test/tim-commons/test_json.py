import unittest

from tim_commons.serializer import load_string, dump_string


class JsonTestCase(unittest.TestCase):
  string = '{"int":1234,"hello":"world"}'

  def test_json(self):
    obj = load_string(self.string)
    self.assertEquals(obj['hello'], 'world')
    self.assertEquals(obj['int'], 1234)

    result = dump_string(obj)
    self.assertEquals(self.string, result)
