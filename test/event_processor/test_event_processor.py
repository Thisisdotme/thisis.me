import unittest
import datetime

import event_interpreter
from event_processors import event_processor
from mi_schema import models
from tim_commons import json_serializer, db


class EventProcessorTestCase(unittest.TestCase):
  def setUp(self):
    db.configure_mock_session()

  def test_correlate_and_update_event(self):
    event = '{"created_at":"Fri Jun 22 22:44:42 +0000 2012","id":216300709476433920,"id_str":"216300709476433920","text":"And a link: http:\/\/t.co\/6fgHbu70 http:\/\/t.co\/OVJDl4UA","source":"web","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":569626455,"id_str":"569626455","name":"Jos\u00e9 Garc\u00eda Sancio","screen_name":"jagsancio","location":"","description":"","url":null,"protected":false,"followers_count":1,"friends_count":8,"listed_count":0,"created_at":"Thu May 03 00:26:13 +0000 2012","favourites_count":0,"utc_offset":null,"time_zone":null,"geo_enabled":false,"verified":false,"statuses_count":5,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/a0.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/si0.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":false,"profile_image_url":"http:\/\/a0.twimg.com\/sticky\/default_profile_images\/default_profile_6_normal.png","profile_image_url_https":"https:\/\/si0.twimg.com\/sticky\/default_profile_images\/default_profile_6_normal.png","profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"show_all_inline_media":false,"default_profile":true,"default_profile_image":true,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"entities":{"hashtags":[],"urls":[{"url":"http:\/\/t.co\/6fgHbu70","expanded_url":"http:\/\/en.wikipedia.org\/wiki\/World","display_url":"en.wikipedia.org\/wiki\/World","indices":[12,32]}],"user_mentions":[],"media":[{"id":216300709480628224,"id_str":"216300709480628224","indices":[33,53],"media_url":"http:\/\/p.twimg.com\/AwB0WWlCAAAUkEj.jpg","media_url_https":"https:\/\/p.twimg.com\/AwB0WWlCAAAUkEj.jpg","url":"http:\/\/t.co\/OVJDl4UA","display_url":"pic.twitter.com\/OVJDl4UA","expanded_url":"http:\/\/twitter.com\/jagsancio\/status\/216300709476433920\/photo\/1","type":"photo","sizes":{"large":{"w":800,"h":450,"resize":"fit"},"small":{"w":340,"h":191,"resize":"fit"},"thumb":{"w":150,"h":150,"resize":"crop"},"medium":{"w":600,"h":337,"resize":"fit"}}}]},"favorited":false,"retweeted":false,"possibly_sensitive":false}'
    event = json_serializer.load_string(event)
    interpreted_event = event_interpreter.create_event_interpreter('twitter', event, None, None)

    author_service_map_id = 1
    me_service_id = 2

    asm_id = 10
    author_id = 5
    twitter_service_id = 3
    service_event = models.ServiceEvent(
        asm_id,
        interpreted_event.event_type(),
        author_id,
        twitter_service_id,
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow())

    event_processor.correlate_and_update_event(
        interpreted_event,
        service_event,
        author_service_map_id,
        me_service_id)

  def test_query_correlation_event(self):
    me_service_id = 2
    correlation_id = 'sha256_hash_id'
    author_id = 1

    event_processor.query_correlation_event(me_service_id, correlation_id, author_id)
