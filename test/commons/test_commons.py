import unittest
import datetime

from tim_commons import total_seconds, prune_dictionary, extract_uri_from_text


class CommonTestCase(unittest.TestCase):
  def test_total_seconds(self):
    time_delta = datetime.timedelta(1, 5, 40)
    self.assertEqual(total_seconds(time_delta), 86405.00004)

  def test_prune_dictionary(self):
    source_dict = {'keep_value': 1,
                   'keep_dict': {'keep_value': 2,
                                 'remove_value': 5,
                                 'remove_dict': {}},
                   'remove_value': 10,
                   'remove_dict': 11}

    prune_dict = {'keep_dict': {'remove_dict': None,
                                'remove_value': None},
                  'remove_value': None,
                  'remove_dict': None}

    prune_dictionary(source_dict, prune_dict)

    self.assertEqual(source_dict['keep_value'], 1)
    self.assertEqual(source_dict['keep_dict']['keep_value'], 2)
    self.assertFalse('remove_value' in source_dict)
    self.assertFalse('remove_dict' in source_dict)
    self.assertFalse('remove_value' in source_dict['keep_dict'])
    self.assertFalse('remove_dict' in source_dict['keep_dict'])

  def test_extract_uri_from_text(self):
    text = "cool http://www.thisis.me. url. better than https://www.example.com/hello?q=world"
    urls = extract_uri_from_text(text)

    self.assertEqual(urls[0], 'http://www.thisis.me')
    self.assertEqual(urls[1], 'https://www.example.com/hello?q=world')
