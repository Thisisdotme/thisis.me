'''
Created on Feb 13, 2012

@author: howard
'''

import json
from datetime import datetime
from time import mktime
from abc import abstractmethod
import urllib2
import copy

from tim_commons.oauth import make_request

'''
'''


class Event(object):
  '''
  classdocs
  '''

  raw_json = None
  event_id = None
  user_id = None

  def __init__(self, userId, eventId=None):
    '''
    Constructor
    '''
    self.user_id = userId
    self.event_id = eventId

  def fromJSON(self, json, auxData=None):
    self.raw_json = json
    self.fromJSONFields(json, auxData)
    return self

  @abstractmethod
  def fromJSONFields(self, json, auxData=None):
    pass

  def toNormalizedObj(self):
    propertyDict = {}
    return self.toJSONFields(propertyDict)

  def toJSON(self):
    return json.dumps(self.toNormalizedObj(), sort_keys=True)

  @abstractmethod
  def toJSONFields(self, json):

    self.toMetadataObjFields(json)

    json["origin"] = self.getEventOrigin()

    caption = self.getEventCaption()
    if caption:
      json["caption"] = caption

    content = self.getEventContent()
    if content:
      json["content"] = content

    photo = self.getEventPhoto()
    if photo:
      json["photo"] = photo

    rawJSON = self.getRawJSON()
    if rawJSON:
      json['_raw_json'] = rawJSON

    return json

  def toMetadataObj(self):
    propertyDict = {}
    return self.toMetadataObjFields(propertyDict)

  @abstractmethod
  def toMetadataObjFields(self, json):

    '''
      standard properties
    '''
    json["event_id"] = self.event_id
    json["author_id"] = self.user_id
    json["create_time"] = int(str(mktime(self.getEventTime().timetuple()))[:-2])
    json["type"] = self.getType()

    return json

  def getEventId(self):
    return self.event_id

  def getUserId(self):
    return self.user_id

  @abstractmethod
  def getType(self):
    pass

  @abstractmethod
  def getEventTime(self):
    pass

  @abstractmethod
  def getEventCaption(self):
    pass

  def getEventPhoto(self):
    return None

  def getEventContent(self):
    return None

  def getAuxillaryContent(self):
    return None

  def getEventOrigin(self):
    return self.getType()

  def getEventURL(self):
    return None

  def getRawJSON(self):
    return self.raw_json

  def getNativePropertiesObj(self):
    return self.raw_json

  def getProfileImageUrl(self):
    return None

'''
'''


class StatusEvent(Event):
  '''
  classdocs
  '''

  def toJSONFields(self, json):
    super(StatusEvent, self).toJSONFields(json)
    ''' customization
    '''
    return json

'''
'''


class TwitterEvent(StatusEvent):
  '''
  classdocs
  '''
  DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

  def fromJSONFields(self, json, auxData=None):
    super(TwitterEvent, self).fromJSONFields(json, auxData)
    ''' Customization
    '''
    self.event_id = self.raw_json['id_str']

    return self

  def toJSONFields(self, json):

    super(TwitterEvent, self).toJSONFields(json)

    ''' customization
    '''
    json['retweet_count'] = int(self.raw_json.get('retweet_count', 0))
    json['favorited'] = bool(self.raw_json.get('favorited', False))

    return json

  def getType(self):
    return "twitter"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['created_at'], self.DATETIME_STRING_FORMAT)

  def getEventContent(self):
    return self.raw_json.get('text', '')

  def getEventOrigin(self):
    source = self.raw_json.get('source')
    return source if source else super(TwitterEvent, self).getEventOrigin()

  def getEventPhoto(self):
    for media in self.raw_json['entities'].get('media', []):
      if media.get('type') == "photo":
        return media.get('media_url')

'''
'''


class FacebookEvent(StatusEvent):
  '''
  classdocs
  '''

  facebookUserId = None

  def __init__(self, userId, facebookUserId):
    '''
    Constructor
    '''
    super(FacebookEvent, self).__init__(userId)
    self.facebookUserId = facebookUserId

  def fromJSONFields(self, json, auxData=None):

    super(FacebookEvent, self).fromJSONFields(json, auxData)

    ''' Customization
    '''
    self.event_id = self.raw_json['id']

    return self

  def toJSONFields(self, json):

    super(FacebookEvent, self).toJSONFields(json)
    ''' customization
    '''
    likes = self.raw_json.get('likes')
    if likes:
      json['likes_count'] = likes.get('count', 0)
    else:
      json['likes_count'] = 0

    return json

  def getType(self):
    return "facebook"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['created_time'], '%Y-%m-%dT%H:%M:%S+0000')

  def getEventCaption(self):
    # this handles events from Nike which is a repetition event
    other = self.raw_json.get('name') + ".  " + self.raw_json.get('caption') if self.raw_json.get('caption') and self.raw_json.get('name') else None

    return self.raw_json.get('story') or self.raw_json.get('message') or other

  def getEventOrigin(self):
    application = self.raw_json.get('application')
    if application:
      origin = '%s,%s,%s' % (application.get('name', ''), application.get('namespace'), application.get('id'))
    else:
      origin = super(FacebookEvent, self).getEventOrigin()

    return origin

  def getEventURL(self):
    return 'https://graph.facebook.com/%s' % (self.event_id)

  def getEventPhoto(self):
    return self.raw_json['picture'] if 'picture' in self.raw_json else None


'''
'''


class GooglePlusEvent(StatusEvent):
  '''
  classdocs
  '''

  def fromJSONFields(self, json, auxData=None):

    super(GooglePlusEvent, self).fromJSONFields(json, auxData)

    ''' Customization
    '''
    self.event_id = self.raw_json['id']

    return self

  def toJSONFields(self, json):
    super(GooglePlusEvent, self).toJSONFields(json)
    ''' customization
    '''
    return json

  def getType(self):
    return "googleplus"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['published'], '%Y-%m-%dT%H:%M:%S.%fZ')

  def getEventCaption(self):
    return self.raw_json.get('title')

  def getEventOrigin(self):
    return self.raw_json['provider']['title'] if 'provider' in self.raw_json and 'title' in self.raw_json['provider'] else super(GooglePlusEvent, self).getEventOrigin()

  def getEventURL(self):
    return self.raw_json.get('url')


'''
'''


class LinkedInEvent(StatusEvent):
  '''
  classdocs
  '''
  @classmethod
  def eventsFromJSON(cls, collector, rawJSON, state, timId, userId, oAuthClient):

    for post in rawJSON.get('values', []):

      updateType = post['updateType']
      supportedTypes = ['SHAR', 'JOBP', 'CONN', 'MSFC', 'PREC', 'SVPR']
      ignoredTypes = ['PROF', 'PICU', 'APPM']
      if updateType in supportedTypes:

        if updateType == 'CONN' and post['updateContent']['person']['id'] == userId:
#          print json.dumps(post, sort_keys=True, indent=2)
          for connection in post['updateContent']['person']['connections']['values']:
            eventId = '%s-%s' % (updateType, connection["id"])
            postClone = copy.deepcopy(post)
            postClone['updateContent']['person']['connections'] = {"_total": 1, "values": [copy.deepcopy(connection)]}
            event = LinkedInConnectEvent(timId, eventId).fromJSON(postClone, oAuthClient)
            collector.writeEvent(event, state)

        elif updateType == 'SHAR':
#          print json.dumps(post, sort_keys=True, indent=2)
          eventId = post['updateKey']
          event = LinkedInShareEvent(timId, eventId).fromJSON(post)
          collector.writeEvent(event, state)

        elif updateType == 'MSFC':
          print json.dumps(post, sort_keys=True, indent=2)
          if post['updateContent']['companyPersonUpdate']['person']['id'] != userId:
            continue
          eventId = post['updateKey']
          event = LinkedInCompanyFollowEvent(timId, eventId).fromJSON(post)
          collector.writeEvent(event, state)

        elif updateType == 'PREC' or updateType == 'SVPR':
          print json.dumps(post, sort_keys=True, indent=2)
          if post['updateContent']['person']['id'] != userId:
            continue
          eventId = post['updateKey']
          event = LinkedInRecommendationEvent(timId, eventId).fromJSON(post)
          collector.writeEvent(event, state)

        elif updateType == 'JOBP':
          print json.dumps(post, sort_keys=True, indent=2)
          if post['updateContent']['job']['jobPoster']['id'] != userId:
            continue
          eventId = post['updateKey']
          event = LinkedInJobPostingEvent(timId, eventId).fromJSON(post)
          collector.writeEvent(event, state)

      else:
        if not updateType in ignoredTypes:
          print '???? skipping linkedIn event: %s' % updateType

  def toJSONFields(self, json):
    super(LinkedInEvent, self).toJSONFields(json)
    ''' customization
    '''
    return json

  def getType(self):
    return "linkedin"

  def getEventTime(self):
    return datetime.utcfromtimestamp(int(self.raw_json['timestamp'] / 1000))

  def getEventContent(self):
    caption = ''
    updateType = self.raw_json['updateType']
    if updateType == 'JOBP':
      caption = "Job Posting"

    return caption

  def getEventURL(self):
    return None


'''
'''


class LinkedInConnectEvent(LinkedInEvent):

  def __init__(self, userId, eventId=None):
    '''
    Constructor
    '''
    super(LinkedInConnectEvent, self).__init__(userId, eventId)

    self.headline = None
    self.summary = None
    self.photo = None

  def fromJSONFields(self, fromJSON, auxData=None):

    super(LinkedInConnectEvent, self).fromJSONFields(fromJSON, auxData)

    # query for the connection's profile image and bio
    connection = self.raw_json['updateContent']['person']['connections']['values'][0]

    if connection['id'] != 'private':

      url = 'http://api.linkedin.com/v1/people/id=%s:(headline,summary,picture-url)' % connection['id']

      try:
        # request the user's updates
        contentJSON = make_request(auxData, url, {'x-li-format': 'json'})
        contentObj = json.loads(contentJSON)

        self.headline = contentObj.get('headline')
        self.summary = contentObj.get('summary')
        self.photo = contentObj.get('pictureUrl')

      except urllib2.URLError:
        self.log.error('***ERROR*** parse error')
        self.log.error(contentJSON)
        pass

    return self

  def getEventContent(self):
    connection = self.raw_json['updateContent']['person']['connections']['values'][0]
    content = '%s is now connected to %s %s.' % (self.raw_json['updateContent']['person']['firstName'], connection['firstName'], connection['lastName'])
    if self.headline:
      content = '%s  %s' % (content, self.headline)
    return content

  def getEventPhoto(self):
    return self.photo


'''
'''


class LinkedInShareEvent(LinkedInEvent):

  def getEventCaption(self):
    return self.raw_json['updateContent']['person']['currentShare'].get('comment')

  def getEventContent(self):

    currShare = self.raw_json['updateContent']['person']['currentShare']

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


'''
'''


class LinkedInCompanyFollowEvent(LinkedInEvent):

  def getEventContent(self):
    person = self.raw_json['updateContent']['companyPersonUpdate']['person']
    action = self.raw_json['updateContent']['companyPersonUpdate']['action']
    return '%s %s %s' % (person['firstName'], action['code'], self.raw_json['updateContent']['company']['name'])


'''
'''


class LinkedInRecommendationEvent(LinkedInEvent):

  def getEventContent(self):
    person = self.raw_json['updateContent']['person']
    recommendation = person['recommendationsGiven']['recommendation']
    return '%s recommends %s %s %s' % (person['firstName'], recommendation['recommendationType']['code'], recommendation['recommendee']['firstName'], recommendation['recommendee']['lastName'])


'''
'''


class LinkedInJobPostingEvent(LinkedInEvent):

  def getEventContent(self):
    job = self.raw_json['updateContent']['job']
    person = self.raw_json['updateContent']['job']['jobPoster']
    return '%s posted the job: %s at %s' % (person['firstName'], job['position'], job['company'])


'''
'''


class PlaceEvent(Event):
  pass


'''
'''


class FoursquareEvent(PlaceEvent):

  caption = None
  content = None
  source = None

  def fromJSONFields(self, fromJSON, auxData=None):

    super(FoursquareEvent, self).fromJSONFields(fromJSON, auxData)

    self.event_id = self.raw_json['id']

#    print json.dumps(fromJSON, sort_keys=True, indent=2)

    ''' Customization
    '''
    caption = fromJSON['venue'].get('name', '')
    shout = fromJSON.get('shout', None)
    address = fromJSON['venue']['location'].get('address')
    city = fromJSON['venue']['location'].get('city')

    # define location
    location = None
    if (address and city):
      location = '%s, %s' % (address, city)
    elif address:
      location = address
    else:
      location = city

    location = ' (%s)' % location if location else ''

    self.source = location

    source_name = fromJSON['source'].get('name', '')
    source_url = fromJSON['source'].get('url', '')

    self.source = {"name": source_name, "url": source_url}

    self.caption = shout
    self.content = '%s%s' % (caption, location)

    return self

  def getType(self):
    return "foursquare"

  def getEventTime(self):
    return datetime.utcfromtimestamp(int(self.raw_json['createdAt']))

  def getEventCaption(self):
    return self.caption

  def getEventContent(self):
    return self.content

  def getEventOrigin(self):
    return '%s#%s' % (self.source['name'], self.source['url'])

  def getEventURL(self):
    return None

  def getEventPhoto(self):
    return self.raw_json['photos']['items'][0]['url'] if int(self.raw_json['photos']['count']) > 0 else None

  def getAuxillaryContent(self):
    auxData = {}

    venueURL = self.raw_json['venue'].get('url')
    auxData['venue_url'] = venueURL

    photoSizes = self.raw_json['photos']['items'][0]['sizes'] if int(self.raw_json['photos']['count']) > 0 else None
    if photoSizes:
      auxData['photo_sizes'] = photoSizes

    return json.dumps(auxData, sort_keys=True) if venueURL else None


'''
'''


class PhotoEvent(Event):
  pass


class InstagramEvent(PhotoEvent):

  caption = None
  content = None
  source = None

  def fromJSONFields(self, fromJSON, auxData=None):

    super(InstagramEvent, self).fromJSONFields(fromJSON, auxData)

    ''' Customization
    '''
    self.event_id = self.raw_json['id']

    return self

  def getType(self):
    return "instagram"

  def getEventTime(self):
    return datetime.utcfromtimestamp(float(self.raw_json['created_time']))

  def getEventCaption(self):
    return self.raw_json['caption']['text'] if 'caption' in self.raw_json and self.raw_json['caption'] and 'text' in self.raw_json['caption'] else None

  def getEventPhoto(self):
    return self.raw_json['images']['low_resolution']['url']

  def getAuxillaryContent(self):
    auxData = {}
    if 'location' in self.raw_json:
      auxData['location'] = self.raw_json['location']
    if 'images' in self.raw_json:
      auxData['images'] = self.raw_json['images']
    return json.dumps(auxData, sort_keys=True)

'''
'''


class FlickrEvent(PhotoEvent):
  pass

'''
'''


class SocialEvent(Event):
  pass
