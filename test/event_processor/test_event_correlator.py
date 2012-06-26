import unittest

import event_correlator
import event_interpreter
from tim_commons import json_serializer


class EventCorrelatorTestCase(unittest.TestCase):
  def test_normalize_uri(self):
    uri = 'http://t.co/YFT32DLX'
    normalized_uri = event_correlator._normalize_uri(uri)
    self.assertEqual(normalized_uri, 'http://www.nytimes.com/2012/06/25/us/politics/second-time-around-hope-for-gay-marriage-in-maine.html')

  def test_correlate_facebook_event(self):
    event = {"id": "155415011259998",
             "from": {"name": "Jose Garcia",
                      "id": "100003801487232"},
             "message": "Some article.",
             "picture": "http://external.ak.fbcdn.net/safe_image.php?d=AQDqHqqj4yY9__hr&w=90&h=90&url=http\u00253A\u00252F\u00252Fgraphics8.nytimes.com\u00252Fimages\u00252F2012\u00252F06\u00252F20\u00252Fus\u00252Fpolitics\u00252F0620holder\u00252F0620holder-thumbLarge.jpg",
             "privacy": {"description": "Friends",
                         "value": "ALL_FRIENDS"},
             "link": "http://www.nytimes.com/2012/06/21/us/obama-claims-executive-privilege-in-gun-case.html?fake=query",
             "name": "Obama Claims Executive Privilege in Gun Case",
             "description": "The Obama administration asserted executive privilege in response to a planned Congressional vote to hold the attorney general in contempt for withholding documents about a failed gun-running investigation.",
             "icon": "http://static.ak.fbcdn.net/rsrc.php/v2/yD/r/aS8ecmYRys0.gif",
             "created_time": "2012-06-20T21:26:57+0000"}
    interpreter = event_interpreter.create_event_interpreter('facebook', event, None, None)
    hash_id, uri = event_correlator.correlate_event(interpreter)
    self.assertEqual(hash_id, 'fP_KpE-4IUDfd7yE9ENZk7wfXqXKYr8jjBICjBhzD3o')
    self.assertEqual(uri, 'http://www.nytimes.com/2012/06/21/us/obama-claims-executive-privilege-in-gun-case.html')

  def test_correlate_twitter_event(self):
    event = '{"created_at":"Mon Jun 25 02:00:33 +0000 2012","id":217074771807059968,"id_str":"217074771807059968","text":"Second Time Around, Hope for Gay Marriage in Maine http:\/\/t.co\/YFT32DLX","source":"web","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":807095,"id_str":"807095","name":"The New York Times","screen_name":"nytimes","location":"New York, NY","description":"Where the Conversation Begins. Follow for breaking news, NYTimes.com home page articles, special features and RTs of our journalists. ","url":"http:\/\/www.nytimes.com\/","protected":false,"followers_count":5414039,"friends_count":637,"listed_count":104350,"created_at":"Fri Mar 02 20:41:42 +0000 2007","favourites_count":3,"utc_offset":-18000,"time_zone":"Eastern Time (US & Canada)","geo_enabled":false,"verified":true,"statuses_count":85325,"lang":"en","contributors_enabled":true,"is_translator":false,"profile_background_color":"FFFFFF","profile_background_image_url":"http:\/\/a0.twimg.com\/profile_background_images\/4432187\/twitter_post.png","profile_background_image_url_https":"https:\/\/si0.twimg.com\/profile_background_images\/4432187\/twitter_post.png","profile_background_tile":true,"profile_image_url":"http:\/\/a0.twimg.com\/profile_images\/2044921128\/finals_normal.png","profile_image_url_https":"https:\/\/si0.twimg.com\/profile_images\/2044921128\/finals_normal.png","profile_link_color":"004276","profile_sidebar_border_color":"323232","profile_sidebar_fill_color":"E7EFF8","profile_text_color":"000000","profile_use_background_image":true,"show_all_inline_media":false,"default_profile":false,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":92,"entities":{"hashtags":[],"urls":[{"url":"http:\/\/t.co\/YFT32DLX","expanded_url":"http:\/\/nyti.ms\/KHpcpD","display_url":"nyti.ms\/KHpcpD","indices":[51,71]}],"user_mentions":[]},"favorited":false,"retweeted":false,"possibly_sensitive":false}'
    event = json_serializer.load_string(event)
    interpreter = event_interpreter.create_event_interpreter('twitter', event, None, None)
    hash_id, uri = event_correlator.correlate_event(interpreter)
    self.assertEqual(hash_id, 'UaMGQijlLKVWm-7OBQwUWv7pyakgAoHwvvTUvgtz7is')
    self.assertEqual(uri, 'http://www.nytimes.com/2012/06/25/us/politics/second-time-around-hope-for-gay-marriage-in-maine.html')
