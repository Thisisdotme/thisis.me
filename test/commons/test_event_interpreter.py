import unittest
import datetime

from tim_commons import event_interpreter, json_serializer
from mi_schema import models


class EventInterpreterTest(unittest.TestCase):
  def setUp(self):
    self.author_service_map = None
    self.oauth_config = None

  def test_facebook_photo_album_event(self):
    event = {"id": "138817786254937",
             "from": {"name": "Jose Garcia",
                      "id": "100003801487232"},
            "name": "First album",
            "description": "Cool Album",
            "location": "New York, New York",
            "link": "http://www.facebook.com/album.php?fbid=138817786254937&id=100003801487232&aid=28253",
            "cover_photo": "138817806254935",
            "privacy": "friends",
            "count": 1,
            "type": "album",
            "created_time": "2012-06-21T00:48:23+0000",
            "updated_time": "2012-06-21T00:49:41+0000",
            "can_upload": True}

    interpreted = event_interpreter.create_event_interpreter('facebook',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.PHOTO_ALBUM_TYPE)
    self.assertEqual(interpreted.event_id(), '138817786254937')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 21, 0, 48, 23))
    self.assertEqual(interpreted.updated_time(), datetime.datetime(2012, 6, 21, 0, 49, 41))
    self.assertEqual(interpreted.headline(), 'First album')
    self.assertEqual(interpreted.tagline(), None)
    self.assertEqual(interpreted.content(), None)
    self.assertEqual(interpreted.photo(), None)
    self.assertEqual(interpreted.url(), None)
    self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), None)
    self.assertEqual(interpreted.original_content_uri(), None)

  def test_facebook_photo_event(self):
    event = {"id": "138817806254935",
             "from": {"name": "Jose Garcia",
                      "id": "100003801487232"},
             "name": "Cool photo",
             "picture": "http://photos-d.ak.fbcdn.net/hphotos-ak-ash4/282373_138817806254935_883467905_s.jpg",
             "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/s720x720/282373_138817806254935_883467905_n.jpg",
             "height": 477,
             "width": 720,
             "images": [{"height": 1356,
                         "width": 2048,
                         "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/s2048x2048/282373_138817806254935_883467905_n.jpg"},
                        {"height": 636,
                         "width": 960,
                         "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/282373_138817806254935_883467905_n.jpg"},
                        {"height": 477,
                         "width": 720,
                         "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/s720x720/282373_138817806254935_883467905_n.jpg"},
                        {"height": 318,
                         "width": 480,
                         "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/s480x480/282373_138817806254935_883467905_n.jpg"},
                        {"height": 212,
                         "width": 320,
                         "source": "http://sphotos.xx.fbcdn.net/hphotos-ash4/s320x320/282373_138817806254935_883467905_n.jpg"},
                        {"height": 119,
                         "width": 180,
                         "source": "http://photos-d.ak.fbcdn.net/hphotos-ak-ash4/282373_138817806254935_883467905_a.jpg"},
                        {"height": 86,
                         "width": 130,
                         "source": "http://photos-d.ak.fbcdn.net/hphotos-ak-ash4/282373_138817806254935_883467905_s.jpg"},
                        {"height": 86,
                         "width": 130,
                         "source": "http://photos-d.ak.fbcdn.net/hphotos-ak-ash4/s75x225/282373_138817806254935_883467905_s.jpg"}],
             "link": "http://www.facebook.com/photo.php?fbid=138817806254935&set=a.138817786254937.28253.100003801487232&type=1",
             "icon": "http://static.ak.fbcdn.net/rsrc.php/v2/yz/r/StEh3RhPvjk.gif",
             "place": {"id": "108424279189115",
                       "name": "New York, New York",
                       "location": {"city": "New York",
                                    "state": "NY",
                                    "country": "United States",
                                    "latitude": 40.7167,
                                    "longitude": -74}},
             "created_time": "2012-06-21T00:48:25+0000",
             "position": 1,
             "updated_time": "2012-06-21T00:49:40+0000",
             "type": "photo"}

    interpreted = event_interpreter.create_event_interpreter('facebook',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.PHOTO_TYPE)
    self.assertEqual(interpreted.event_id(), '138817806254935')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 21, 0, 48, 25))
    self.assertEqual(interpreted.updated_time(), datetime.datetime(2012, 6, 21, 0, 49, 40))
    self.assertEqual(interpreted.headline(), 'Cool photo')
    self.assertEqual(interpreted.tagline(), None)
    self.assertEqual(interpreted.content(), None)
    self.assertEqual(interpreted.photo(), 'http://sphotos.xx.fbcdn.net/hphotos-ash4/s2048x2048/282373_138817806254935_883467905_n.jpg')
    self.assertEqual(interpreted.url(), None)
    self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), None)
    self.assertEqual(interpreted.original_content_uri(), None)

  def test_facebook_checkin_event(self):
    event = {"id": "139187866217929",
             "from": {"name": "Jose Garcia",
                      "id": "100003801487232"},
             "message": "Testing checkin",
             "place": {"id": "77012221220",
                       "name": "21st Amendment Brewery",
                       "location": {"street": "563 2nd Street",
                                    "city": "San Francisco",
                                    "state": "CA",
                                    "country": "United States",
                                    "zip": "94107",
                                    "latitude": 37.78233902813,
                                    "longitude": -122.39256287195}},
             "application": {"name": "Facebook for iPhone",
                             "namespace": "fbiphone",
                             "id": "6628568379"},
             "created_time": "2012-06-21T18:22:05+0000",
             "type": "checkin"}

    interpreted = event_interpreter.create_event_interpreter('facebook',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.CHECKIN_TYPE)
    self.assertEqual(interpreted.event_id(), '139187866217929')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 21, 18, 22, 5))
    self.assertEqual(interpreted.updated_time(), None)
    self.assertEqual(interpreted.headline(), 'Testing checkin')
    self.assertEqual(interpreted.tagline(), '21st Amendment Brewery')
    self.assertEqual(interpreted.content(), '21st Amendment Brewery')
    self.assertEqual(interpreted.photo(), None)
    self.assertEqual(interpreted.url(), None)
    self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), None)
    self.assertEqual(interpreted.original_content_uri(), None)

  def test_facebook_status_event(self):
    event = {"id": "155415011259998",
             "from": {"name": "Jose Garcia",
                      "id": "100003801487232"},
             "message": "Some article.",
             "picture": "http://external.ak.fbcdn.net/safe_image.php?d=AQDqHqqj4yY9__hr&w=90&h=90&url=http\u00253A\u00252F\u00252Fgraphics8.nytimes.com\u00252Fimages\u00252F2012\u00252F06\u00252F20\u00252Fus\u00252Fpolitics\u00252F0620holder\u00252F0620holder-thumbLarge.jpg",
             "privacy": {"description": "Friends",
                         "value": "ALL_FRIENDS"},
             "link": "http://www.nytimes.com/2012/06/21/us/obama-claims-executive-privilege-in-gun-case.html",
             "name": "Obama Claims Executive Privilege in Gun Case",
             "description": "The Obama administration asserted executive privilege in response to a planned Congressional vote to hold the attorney general in contempt for withholding documents about a failed gun-running investigation.",
             "icon": "http://static.ak.fbcdn.net/rsrc.php/v2/yD/r/aS8ecmYRys0.gif",
             "created_time": "2012-06-20T21:26:57+0000"}

    interpreted = event_interpreter.create_event_interpreter('facebook',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.STATUS_TYPE)
    self.assertEqual(interpreted.event_id(), '155415011259998')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 20, 21, 26, 57))
    self.assertEqual(interpreted.updated_time(), None)
    self.assertEqual(interpreted.headline(), 'Some article.')
    self.assertEqual(interpreted.tagline(), None)
    self.assertEqual(interpreted.content(), None)
    self.assertEqual(interpreted.photo(), 'http://external.ak.fbcdn.net/safe_image.php?d=AQDqHqqj4yY9__hr&w=90&h=90&url=http\u00253A\u00252F\u00252Fgraphics8.nytimes.com\u00252Fimages\u00252F2012\u00252F06\u00252F20\u00252Fus\u00252Fpolitics\u00252F0620holder\u00252F0620holder-thumbLarge.jpg')
    self.assertEqual(interpreted.url(), 'https://graph.facebook.com/155415011259998')
    self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), None)
    self.assertEqual(interpreted.original_content_uri(), "http://www.nytimes.com/2012/06/21/us/obama-claims-executive-privilege-in-gun-case.html")

  def test_twitter_event(self):
    event = '{"created_at":"Fri Jun 22 22:44:42 +0000 2012","id":216300709476433920,"id_str":"216300709476433920","text":"And a link: http:\/\/t.co\/6fgHbu70 http:\/\/t.co\/OVJDl4UA","source":"web","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":569626455,"id_str":"569626455","name":"Jos\u00e9 Garc\u00eda Sancio","screen_name":"jagsancio","location":"","description":"","url":null,"protected":false,"followers_count":1,"friends_count":8,"listed_count":0,"created_at":"Thu May 03 00:26:13 +0000 2012","favourites_count":0,"utc_offset":null,"time_zone":null,"geo_enabled":false,"verified":false,"statuses_count":5,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/a0.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/si0.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":false,"profile_image_url":"http:\/\/a0.twimg.com\/sticky\/default_profile_images\/default_profile_6_normal.png","profile_image_url_https":"https:\/\/si0.twimg.com\/sticky\/default_profile_images\/default_profile_6_normal.png","profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"show_all_inline_media":false,"default_profile":true,"default_profile_image":true,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"entities":{"hashtags":[],"urls":[{"url":"http:\/\/t.co\/6fgHbu70","expanded_url":"http:\/\/en.wikipedia.org\/wiki\/World","display_url":"en.wikipedia.org\/wiki\/World","indices":[12,32]}],"user_mentions":[],"media":[{"id":216300709480628224,"id_str":"216300709480628224","indices":[33,53],"media_url":"http:\/\/p.twimg.com\/AwB0WWlCAAAUkEj.jpg","media_url_https":"https:\/\/p.twimg.com\/AwB0WWlCAAAUkEj.jpg","url":"http:\/\/t.co\/OVJDl4UA","display_url":"pic.twitter.com\/OVJDl4UA","expanded_url":"http:\/\/twitter.com\/jagsancio\/status\/216300709476433920\/photo\/1","type":"photo","sizes":{"large":{"w":800,"h":450,"resize":"fit"},"small":{"w":340,"h":191,"resize":"fit"},"thumb":{"w":150,"h":150,"resize":"crop"},"medium":{"w":600,"h":337,"resize":"fit"}}}]},"favorited":false,"retweeted":false,"possibly_sensitive":false}'
    event = json_serializer.load_string(event)
    interpreted = event_interpreter.create_event_interpreter('twitter',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.STATUS_TYPE)
    self.assertEqual(interpreted.event_id(), '216300709476433920')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 22, 22, 44, 42))
    self.assertEqual(interpreted.updated_time(), None)
    self.assertEqual(interpreted.headline(), None)
    self.assertEqual(interpreted.tagline(),
                     'And a link: http://t.co/6fgHbu70 http://t.co/OVJDl4UA')
    self.assertEqual(interpreted.content(),
                     'And a link: http://t.co/6fgHbu70 http://t.co/OVJDl4UA')
    self.assertEqual(interpreted.photo(), None)
    self.assertEqual(interpreted.url(), None)
    self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), 'web')
    self.assertEqual(interpreted.original_content_uri(), 'http://en.wikipedia.org/wiki/World')

  def test_foursquare_event(self):
    event = {"comments": {"count": 0,
                          "items": []},
             "createdAt": 1330990508,
             "id": "4f554dace4b0e7b8dd62bff5",
             "like": False,
             "likes": {"count": 0,
                       "groups": []},
             "photos": {"count": 1,
                        "items": [{"createdAt":1330990511,
                                  "id": "4f554dafe4b0a3a6d5d48355",
                                  "sizes": {"count":4,
                                           "items": [{"height":720,
                                                     "url": "https://is0.4sqi.net/pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0.jpg",
                                                     "width":540},
                                                    {"height":300,
                                                     "url": "https://is1.4sqi.net/derived_pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0_300x300.jpg",
                                                     "width":300},
                                                    {"height":100,
                                                     "url": "https://is1.4sqi.net/derived_pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0_100x100.jpg",
                                                     "width":100},
                                                    {"height":36,
                                                     "url": "https://is1.4sqi.net/derived_pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0_36x36.jpg",
                                                     "width":36}]},
                                  "source": {"name": "foursquare for iPhone",
                                             "url": "https://foursquare.com/download/#/iphone"},
                                  "url": "https://is0.4sqi.net/pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0.jpg",
                                  "user": {"bio": "",
                                           "contact": {"email": "andrew@grio.com"},
                                           "firstName": "Andrew",
                                           "gender": "female",
                                           "homeCity": "San Francisco",
                                           "id": "23225231",
                                           "lists": {"groups": [{"count":1,
                                                                "items": [],
                                                                "type": "created"}]},
                                           "photo": "https://foursquare.com/img/blank_girl.png",
                                           "relationship": "self",
                                           "tips": {"count":0}},
                                  "visibility": "private"}]},
             "private": True,
             "shout": "Still workin'",
             "source": {"name": "foursquare for iPhone",
                         "url": "https://foursquare.com/download/#/iphone"},
             "timeZone": "America/Los_Angeles",
             "timeZoneOffset": -480,
             "type": "checkin",
             "venue": {"beenHere": {"count": 1,
                                    "marked": False},
                       "categories": [{"icon": {"name": ".png",
                                               "prefix": "https://foursquare.com/img/categories/food/coffeeshop_",
                                               "sizes": [32, 44, 64, 88, 256]},
                                      "id": "4bf58dd8d48988d1e0931735",
                                      "name": "Coffee Shop",
                                      "pluralName": "Coffee Shops",
                                      "primary": True,
                                      "shortName": "Coffee Shop"}],
                       "contact": {"formattedPhone": "(415) 357-1514",
                                   "phone": "4153571514"},
                       "id": "4a4a3036f964a52092ab1fe3",
                       "like": False,
                       "likes": {"count": 0,
                                 "groups": []},
                       "location": {"address": "215 2nd St",
                                    "city": "San Francisco",
                                    "country": "United States",
                                    "crossStreet": "btwn Howard & Tehama St",
                                    "lat": 37.786515038891984,
                                    "lng": -122.39826347396233,
                                    "postalCode": "94105",
                                    "state": "CA"},
                       "name": "Chatz Coffee",
                       "url": "http://www.chatz.com",
                       "verified": False},
             "visibility": "private"}

    interpreted = event_interpreter.create_event_interpreter('foursquare',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.CHECKIN_TYPE)
    self.assertEqual(interpreted.event_id(), '4f554dace4b0e7b8dd62bff5')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 3, 5, 23, 35, 8))
    self.assertEqual(interpreted.updated_time(), None)
    self.assertEqual(interpreted.headline(), 'Still workin\'')
    self.assertEqual(interpreted.tagline(), None)
    self.assertEqual(interpreted.content(), 'Chatz Coffee (215 2nd St, San Francisco)')
    self.assertEqual(interpreted.photo(), 'https://is0.4sqi.net/pix/ODUYnUnoCTrN1zCKJQBixUrBczCuxSOwzvcse5Mznj0.jpg')
    self.assertEqual(interpreted.url(), None)
    # TODO: test this: self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), 'foursquare for iPhone#https://foursquare.com/download/#/iphone')
    self.assertEqual(interpreted.original_content_uri(), None)

  def test_googleplus_event(self):
    # TODO: implement this
    self.assertTrue(True)

  def test_instagram_event(self):
    event = {
      "attribution": None,
      "caption": {
        "created_time": "1339635993",
        "from": {
          "full_name": "Howard Burrows",
          "id": "12937196",
          "profile_picture": "http://images.instagram.com/profiles/profile_12937196_75sq_1328302146.jpg",
          "username": "howardburrows"},
        "id": "213204626628040190",
        "text": "Academia"},
      "comments": {
        "count": 1,
        "data": [{
          "created_time": "1339642197",
          "from": {
            "full_name": "Sara O'Keefe",
            "id": "25262451",
            "profile_picture": "http://images.instagram.com/profiles/profile_25262451_75sq_1335025822.jpg",
            "username": "sarabokeefe"},
          "id": "213256669736621389",
          "text": "Where you at bro?"}]},
      "created_time": "1339635948",
      "filter": "Earlybird",
      "id": "213204245072205177_12937196",
      "images": {
        "low_resolution": {
          "height": 306,
          "url": "http://distilleryimage9.s3.amazonaws.com/13c5e8f6b5bd11e188131231381b5c25_6.jpg",
          "width": 306},
        "standard_resolution": {
          "height": 612,
          "url": "http://distilleryimage9.s3.amazonaws.com/13c5e8f6b5bd11e188131231381b5c25_7.jpg",
          "width": 612},
        "thumbnail": {
          "height": 150,
          "url": "http://distilleryimage9.s3.amazonaws.com/13c5e8f6b5bd11e188131231381b5c25_5.jpg",
          "width": 150}},
      "likes": {
        "count": 0,
        "data": []},
      "link": "http://instagr.am/p/L1dCGcIlV5/",
      "location": {
        "id": 22336,
        "latitude": 37.872069207999999,
        "longitude": -122.257830799,
        "name": "Campanile (Sather Tower)"},
      "tags": [],
      "type": "image",
      "user": {
        "bio": "",
        "full_name": "Howard Burrows",
        "id": "12937196",
        "profile_picture": "http://images.instagram.com/profiles/profile_12937196_75sq_1328302146.jpg",
        "username": "howardburrows",
        "website": ""},
      "user_has_liked": False}

    interpreted = event_interpreter.create_event_interpreter('instagram',
                                                             event,
                                                             self.author_service_map,
                                                             self.oauth_config)

    self.assertEqual(interpreted.event_type(), models.ServiceObjectType.PHOTO_TYPE)
    self.assertEqual(interpreted.event_id(), '213204245072205177_12937196')
    self.assertEqual(interpreted.created_time(), datetime.datetime(2012, 6, 14, 1, 5, 48))
    self.assertEqual(interpreted.updated_time(), None)
    self.assertEqual(interpreted.headline(), 'Academia')
    self.assertEqual(interpreted.tagline(), None)
    self.assertEqual(interpreted.content(), None)
    self.assertEqual(interpreted.photo(), 'http://distilleryimage9.s3.amazonaws.com/13c5e8f6b5bd11e188131231381b5c25_6.jpg')
    self.assertEqual(interpreted.url(), None)
    # TODO: test this: self.assertEqual(interpreted.auxiliary_content(), None)
    self.assertEqual(interpreted.origin(), None)
    self.assertEqual(interpreted.original_content_uri(), None)

  def test_linkedin_event(self):
    # TODO: implement this
    self.assertTrue(True)

  def test_normalized_uri(self):
    normalized_uri = 'http://www.thisis.me/hello'
    uri = normalized_uri + '?q=world'

    result = event_interpreter.normalize_uri(uri)

    self.assertEqual(result, normalized_uri)
