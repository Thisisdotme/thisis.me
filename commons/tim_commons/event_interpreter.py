import datetime

from mi_schema import models
from tim_commons import json_serializer


def create_event_interpreter(service_name, json_object, author_service_map, oauth_config):
  # TODO: we should remove the requirement on author_service_map and oauth_config
  if service_name == 'facebook':
    return _create_facebook_event_interpreter(json_object, author_service_map, oauth_config)
  elif service_name == 'twitter':
    return _create_twitter_event_interpreter(json_object, author_service_map, oauth_config)
  elif service_name == 'foursquare':
    return _create_foursquare_event_interpreter(json_object, author_service_map, oauth_config)
  elif service_name == 'googleplus':
    return _create_googleplus_event_interpreter(json_object, author_service_map, oauth_config)
  elif service_name == 'instagram':
    return _create_instagram_event_interpreter(json_object, author_service_map, oauth_config)
  elif service_name == 'linkedin':
    return _create_linkedin_event_interpreter(json_object, author_service_map, oauth_config)
  else:
    raise Exception("Unable for construct interpreter for: {0}".format(service_name))


def _create_facebook_event_interpreter(json_object, author_service_map, oauth_config):
  event_type = json_object.get('type', None)
  if event_type == 'album':
    return _FacebookPhotoAlbumEventInterpreter(json_object, author_service_map, oauth_config)
  elif event_type == 'photo':
    return _FacebookPhotoEventInterpreter(json_object, author_service_map, oauth_config)
  elif event_type == 'checkin':
    return _FacebookCheckinInterpreter(json_object, author_service_map, oauth_config)

  return _FacebookStatusEventInterpreter(json_object, author_service_map, oauth_config)


def _create_twitter_event_interpreter(json_object, author_service_map, oauth_config):
  return _TwitterEventInterpreter(json_object, author_service_map, oauth_config)


def _create_foursquare_event_interpreter(json_object, author_service_map, oauth_config):
  return _FoursquareEventInterpreter(json_object, author_service_map, oauth_config)


def _create_googleplus_event_interpreter(json_object, author_service_map, oauth_config):
  return _GoogleplusStatusEventInterpreter(json_object, author_service_map, oauth_config)


def _create_instagram_event_interpreter(json_object, author_service_map, oauth_config):
  return _InstagramEventInterpreter(json_object, author_service_map, oauth_config)


def _create_linkedin_event_interpreter(json_object, author_service_map, oauth_config):
  return _LinkedinEventInterpreter(json_object, author_service_map, oauth_config)


#---- Event interpreters ----

class _ServiceEventInterpreter(object):
  def __init__(self, json, author_service_map, oauth_config):
    self.json = json
    self.author_service_map = author_service_map
    self.oauth_config = oauth_config

  '''
    get the type of the event (status, photo, album, checkin, etc.)
  '''
  def get_type(self):
    return self.event_type()

  def event_type(self):
    raise NotImplementedError('Implement get_type()')

  '''
    get the service's unique identifier for the event
  '''
  def get_id(self):
    return self.event_id()

  def event_id(self):
    raise NotImplementedError('Implement get_id()')

  '''
    get the time the event the created as a Python Time object
  '''
  def get_create_time(self):
    return self.created_time()

  def created_time(self):
    raise NotImplementedError('Implement get_create_time()')

  '''
    get the time the event was last updated as a Python Time object
  '''
  def get_update_time(self):
    return self.updated_time()

  def updated_time(self):
    return None

  '''
    get the events headline - a brief caption
  '''
  def get_headline(self):
    return self.headline()

  def headline(self):
    return None

  '''
    get the event's tagline or deck - a sentence or few sentences which summarizes
    # the post
  '''
  def get_tagline(self):
    return self.tagline()

  def tagline(self):
    return None

  '''
    get the event's content -- the full story or body of text
  '''
  def get_content(self):
    return self.content()

  def content(self):
    return None

  '''
    get the primary photo, if any, associated with the event
  '''
  def get_photo(self):
    return self.photo()

  def photo(self):
    return None

  '''
    get the url of the event's service page
  '''
  def get_url(self):
    return self.url()

  def url(self):
    return None

  '''
    get any auxiliary content for the event
  '''
  def get_auxiliary_content(self):
    return self.auxiliary_content()

  def auxiliary_content(self):
    return None

  '''
    get the origin for the event.  For events that get shared
    on multile platforms the origin identifies the originating
    service
  '''
  def get_origin(self):
    return self.origin()

  def origin(self):
    return None

  '''
    get the URI to the original content.
  '''
  def original_content_uri(self):
    return None


class _FacebookEventInterpreter(_ServiceEventInterpreter):
  DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

  def event_id(self):
    # allow the object_id to have precedence if it exists
    return self.json['object_id'] if 'object_id' in self.json else self.json.get('id', None)

  def created_time(self):
    return datetime.datetime.strptime(self.json['created_time'], self.DATETIME_FORMAT)

  def updated_time(self):
    date = self.json.get('updated_time')
    if date:
      return datetime.datetime.strptime(date, self.DATETIME_FORMAT)

    return None


class _FacebookStatusEventInterpreter(_FacebookEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.STATUS_TYPE

  def headline(self):
    # this handles events from Nike which is a repetition event
    result = self.json.get('story')
    if result is None:
      result = self.json.get('message')
      if result is None:
        name = self.json.get('name')
        caption = self.json.get('caption')
        if name and caption:
          result = self.json.get('name') + ".  " + self.json.get('caption')

    return result

  def origin(self):
    application = self.json.get('application')
    if application:
      origin = '{0},{1},{2}'.format(application.get('name', ''),
                                    application.get('namespace'),
                                    application.get('id'))
    else:
      origin = super(_FacebookStatusEventInterpreter, self).origin()

    return origin

  def url(self):
    return 'https://graph.facebook.com/{0}'.format(self.event_id())

  def photo(self):
    return self.json['picture'] if 'picture' in self.json else None


class _FacebookPhotoAlbumEventInterpreter(_FacebookEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.PHOTO_ALBUM_TYPE

  def headline(self):
    return self.json.get('name', None)

  def photo(self):
    pass


class _FacebookPhotoEventInterpreter(_FacebookEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.PHOTO_TYPE

  def headline(self):
    return self.json.get('name', None)

  def photo(self):
    photo = None
    images = self.json.get('images', None)
    if images and len(images) > 0:
      photo = images[0].get('source', None)
    return photo


class _FacebookCheckinInterpreter(_FacebookEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.CHECKIN_TYPE

  def headline(self):
    return self.json.get('message', None)

  def tagline(self):
    return self.json['place'].get('name', None) if 'place' in self.json else None

  def content(self):
    return self.tagline()


class _TwitterEventInterpreter(_ServiceEventInterpreter):
  DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

  def event_type(self):
    return models.ServiceObjectType.STATUS_TYPE

  def event_id(self):
    return self.json['id_str']

  def created_time(self):
    return datetime.datetime.strptime(self.json['created_at'], self.DATETIME_STRING_FORMAT)

  def tagline(self):
    return self.json.get('text', '')

  def content(self):
    return self.tagline()

  def origin(self):
    source = self.json.get('source')
    return source if source else None

  def photo(self):
    # TODO: investigate how to implement this correctly
    return None


class _FoursquareEventInterpreter(_ServiceEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.CHECKIN_TYPE

  def event_id(self):
    return self.json['id']

  def created_time(self):
    return datetime.datetime.utcfromtimestamp(int(self.json['createdAt']))

  def headline(self):
    return self.json.get('shout', None)

  def content(self):
    address = self.json['venue']['location'].get('address')
    city = self.json['venue']['location'].get('city')

    # define location
    location = None
    if address and city:
      location = '%s, %s' % (address, city)
    elif address:
      location = address
    else:
      location = city
    location = ' (%s)' % location if location else ''

    return '{0}{1}'.format(self.json['venue'].get('name', ''), location)

  def photo(self):
    if int(self.json['photos']['count']) > 0:
      return self.json['photos']['items'][0]['url']

    return None

  def origin(self):
    return '{0}#{1}'.format(self.json['source'].get('name', ''),
                            self.json['source'].get('url', ''))

  def auxiliary_content(self):
    auxData = {}

    venueURL = self.json['venue'].get('url')
    auxData['venue_url'] = venueURL

    photoSizes = None
    if int(self.json['photos']['count']) > 0:
      photoSizes = self.json['photos']['items'][0]['sizes']

    if photoSizes:
      auxData['photo_sizes'] = photoSizes

    return json_serializer.dump_string(auxData) if venueURL else None


class _GoogleplusStatusEventInterpreter(_ServiceEventInterpreter):
  DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

  def event_type(self):
    return models.ServiceObjectType.STATUS_TYPE

  def event_id(self):
    return self.json['id']

  def created_time(self):
    return datetime.datetime.strptime(self.json['published'], self.DATETIME_FORMAT)

  def updated_time(self):
    return datetime.datetime.strptime(self.json['updated'], self.DATETIME_FORMAT)

  def headline(self):
    return self.tagline()

  def tagline(self):
    return self.json.get('title')

  def origin(self):
    provider = self.json.get('provider')
    if provider:
      return provider.get('title')

    return None

  def url(self):
    return self.json.get('url')


class _InstagramEventInterpreter(_ServiceEventInterpreter):
  def event_type(self):
    return models.ServiceObjectType.PHOTO_TYPE

  def event_id(self):
    return self.json['id']

  def created_time(self):
    return datetime.datetime.utcfromtimestamp(float(self.json['created_time']))

  def headline(self):
    caption = self.json.get('caption')
    if caption:
      return caption.get('text')

    return None

  def photo(self):
    return self.json['images']['low_resolution']['url']

  def auxiliary_content(self):
    auxData = {}
    if 'location' in self.json:
      auxData['location'] = self.json['location']
    if 'images' in self.json:
      auxData['images'] = self.json['images']
    return json_serializer.dump_string(auxData)


class _LinkedinEventInterpreter(_ServiceEventInterpreter):
  def __init__(self, json, author_service_map, oauth_config):
    super(_LinkedinEventInterpreter, self).__init__(json, author_service_map, oauth_config)
    self._client = None

  def oauth_client(self):
    import oauth2
    # only create the client if it's requested
    if not self._client:
      consumer = oauth2.Consumer(self.oauth_config['key'], self.oauth_config['secret'])
      token = oauth2.Token(key=self.author_service_map.access_token,
                          secret=self.author_service_map.access_token_secret)
      self._client = oauth2.Client(consumer, token)

    return self._client

  def event_type(self):
    if self.json['updateType'] == 'CONN':
      return models.ServiceObjectType.FOLLOW_TYPE
    else:
      return models.ServiceObjectType.STATUS_TYPE

  def event_id(self):
    eventId = self.json['updateKey']
    if self.json['updateType'] == 'CONN':
      eventId = '{0}:{1}'.format(
          eventId,
          self.json['updateContent']['person']['connections']['values'][0]['id'])
    elif self.json['updateType'] == 'JGRP':
      eventId = '{0}:{1}'.format(
          eventId,
          self.json['updateContent']['person']['memberGroups']['values'][0]['id'])
    return eventId

  def create_time(self):
    return datetime.datetime.utcfromtimestamp(int(self.json['timestamp'] / 1000))

  def headline(self):
    headline = None

    # share updates
    if self.json['updateType'] == 'SHAR':
      headline = self.json['updateContent']['person']['currentShare'].get('comment')

    return headline

  def tagline(self):
    deck = None

    updateType = self.json['updateType']

    # connection updates
    if updateType == 'CONN':
      deck = self.connection_tagline()
    # share updates
    elif updateType == 'SHAR':
      deck = self.share_tagline()
    # company follow updates
    elif updateType == 'MSFC':
      deck = self.company_follow_tagline()
    # recommendation updates
    elif updateType == 'PREC' or updateType == 'SVPR':
      deck = self.recommendation_tagline()
    elif updateType == 'JOBP':
      deck = self.job_posting_tagline()
    # joined group update
    elif updateType == 'JGRP':
      deck = self.join_group_tagline()
    # status updates
    elif updateType == 'STAT':
      deck = self.status_tagline()

    return deck

  # TODO: need to remedy the headline, deck, content debate
  def content(self):
    return self.tagline()

  def photo(self):
    photo = None

    if self.json['updateType'] == 'CONN':
      self.init_connection()
      photo = self.photo

    return photo

  def connection_tagline(self):
    self.init_connection()
    connection = self.json['updateContent']['person']['connections']['values'][0]
    content = '%s is now connected to %s %s.' % (self.json['updateContent']['person']['firstName'],
                                                 connection['firstName'],
                                                 connection['lastName'])
    if self.headline:
      content = '%s  %s' % (content, self.headline)
    return content

  def share_tagline(self):

    currShare = self.json['updateContent']['person']['currentShare']

    phrase = None
    if 'content' in currShare:
      title = currShare['content'].get('title')
      description = currShare['content'].get('description')
      if title and description:
        phrase = '%s; %s' % (title, description)
      else:
        phrase = title if title else description

      shortenedUrl = currShare['content'].get('shortenedUrl')
      if shortenedUrl:
        phrase = '%s (%s)' % (phrase, shortenedUrl) if phrase else shortenedUrl

    return phrase

  def company_follow_tagline(self):

    person = self.json['updateContent']['companyPersonUpdate']['person']
    action = self.json['updateContent']['companyPersonUpdate']['action']
    return '%s %s %s' % (person['firstName'],
                         action['code'],
                         self.json['updateContent']['company']['name'])

  def recommendation_tagline(self):

    person = self.json['updateContent']['person']
    recommendation = person['recommendationsGiven']['recommendation']
    return '%s recommends %s %s %s' % (person['firstName'],
                                       recommendation['recommendationType']['code'],
                                       recommendation['recommendee']['firstName'],
                                       recommendation['recommendee']['lastName'])

  def job_posting_tagline(self):

    job = self.json['updateContent']['job']
    person = self.json['updateContent']['job']['jobPoster']
    return '%s posted the job: %s at %s' % (person['firstName'], job['position'], job['company'])

  def join_group_tagline(self):
    return self.json['updateContent']['person']['memberGroups']['values'][0]['name']

  def status_tagline(self):
    return self.json['updateContent']['person']['currentStatus']

  def init_connection(self):
    from tim_commons import oauth

    connection = self.json['updateContent']['person']['connections']['values'][0]

    if connection['id'] != 'private' and self._client is None:

      url = '%speople/id=%s:(headline,summary,picture-url)' % (self.oauth_config['endpoint'],
                                                               connection['id'])

      # request the user's updates
      json_str = oauth.make_request(self.oauth_client(), url, {'x-li-format': 'json'})
      json_obj = json_serializer.load_string(json_str)

      self.headline = json_obj.get('headline')
      self.summary = json_obj.get('summary')
      self.photo = json_obj.get('pictureUrl')
