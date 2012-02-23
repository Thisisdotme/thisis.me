'''
Created on Feb 13, 2012

@author: howard
'''

import json
from datetime import datetime
from abc import abstractmethod


'''
'''
class Event(object):
  '''
  classdocs
  '''
  
  raw_json = None
  event_id = None
  user_id = None
  
  def __init__(self,userId,eventId):
    '''
    Constructor
    '''
    self.user_id = userId
    self.event_id = eventId
  
  def fromJSON(self,json):
    self.raw_json = json
    self.fromJSONFields(json)
    return self

  @abstractmethod
  def fromJSONFields(self,json):
    pass


  def toJSON(self):
    propertyDict = {}
    self.toJSONFields(propertyDict)
    return json.dumps(propertyDict,sort_keys=True)

  @abstractmethod
  def toJSONFields(self,json):
    '''
      output type, create_time
    '''
    json["event_id"] = self.event_id
    json["user_id"] = self.user_id
    json["create_time"] = self.getEventTime().isoformat()
    json["type"] = self.getType()
    json["source"] = self.getEventSource()
    json["message"] = self.getEventCaption()
  

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
  
  def getEventContent(self):
    return None
  
  def getEventPhoto(self):
    return None

  def getEventSource(self):
    return self.getType() 

  def getEventURL(self):
    return None

  def getAuxillaryContent(self):
    return None

'''
'''
class StatusEvent(Event):
  '''
  classdocs
  '''
  
  
  def fromJSONFields(self,json):
    super(StatusEvent, self).fromJSONFields(json)
    ''' Customization
    '''
    return self
  
  def toJSONFields(self,json):
    super(StatusEvent, self).toJSONFields(json)
    ''' customization
    '''

  
'''
'''
class TwitterEvent(StatusEvent):
  '''
  classdocs
  '''
  DATETIME_STRING_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'


  def fromJSONFields(self,json):
    super(TwitterEvent, self).fromJSONFields(json)
    ''' Customization
    '''
    return self
  
  def toJSONFields(self,json):
    
    super(TwitterEvent, self).toJSONFields(json)

    ''' customization
    '''
    json['retweet_count'] = int(self.raw_json.get('retweet_count',0))
    json['favorited'] = bool(self.raw_json.get('favorited',False))




  def getType(self):
    return "twitter"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['created_at'], self.DATETIME_STRING_FORMAT)

  def getEventCaption(self):
    return self.raw_json.get('text','')

  def getEventSource(self):
    return self.raw_json.get('source','')


'''
'''
class FacebookEvent(StatusEvent):
  '''
  classdocs
  '''
  
  foreignUserId = None

  def __init__(self,userId,eventId,foreignUserId):
    '''
    Constructor
    '''
    super(FacebookEvent, self).__init__(userId,eventId)
    self.foreignUserId = foreignUserId
    

  def fromJSONFields(self,json):
    super(FacebookEvent, self).fromJSONFields(json)
    ''' Customization
    '''
    return self
  
  def toJSONFields(self,json):
    super(FacebookEvent, self).toJSONFields(json)
    ''' customization
    '''
    likes = self.raw_json.get('likes')
    if likes:
      json['likes_count'] = likes.get('count',0)
    else:
      json['likes_count'] = 0
  

  def getType(self):
    return "facebook"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['created_time'],'%Y-%m-%dT%H:%M:%S+0000')

  def getEventCaption(self):
    return self.raw_json.get('story') or self.raw_json.get('message')

  def getEventSource(self):
    application = self.raw_json.get('application')
    if application:
      source = '%s,%s,%s' % (application.get('name',''),application.get('namespace'),application.get('id'))
    else:
      source = 'facebook'

    return source

  def getEventURL(self):
    return 'https://graph.facebook.com/%s' % (self.event_id)

'''
'''
class GooglePlusEvent(StatusEvent):
  '''
  classdocs
  '''
  

  def fromJSONFields(self,json):
    super(GooglePlusEvent, self).fromJSONFields(json)
    ''' Customization
    '''
    return self
  
  def toJSONFields(self,json):
    super(GooglePlusEvent, self).toJSONFields(json)
    ''' customization
    '''  

  def getType(self):
    return "googleplus"

  def getEventTime(self):
    return datetime.strptime(self.raw_json['published'],'%Y-%m-%dT%H:%M:%S.%fZ')

  def getEventCaption(self):
    return self.raw_json.get('title')

  def getEventSource(self):
    return self.raw_json['provider']['title'] if 'provider' in self.raw_json and 'title' in self.raw_json['provider'] else None

  def getEventURL(self):
    return self.raw_json.get('url')



'''
'''
class LinkedInEvent(StatusEvent):
  '''
  classdocs
  '''
  @classmethod
  def eventsFromJSON(cls,collector,rawJSON,state,timId,userId):
    
    for post in rawJSON.get('values',[]):

      updateType = post['updateType']
      supportedTypes = ['SHAR','JOBS','CONN']
      if updateType in supportedTypes:

        if updateType == 'CONN' and post['updateContent']['person']['id'] == userId:
#          print json.dumps(post, sort_keys=True, indent=2)
          for connection in post['updateContent']['person']['connections']['values']:
            eventId = '%s-%s' % (updateType,connection["id"])
            event = LinkedInEvent(timId,eventId).fromJSON(post)
            collector.writeEvent(event,state)

        elif updateType == 'SHAR':
#          print json.dumps(post, sort_keys=True, indent=2)
          eventId = post['updateKey']
          event = LinkedInEvent(timId,eventId).fromJSON(post)      
          collector.writeEvent(event,state)


  def fromJSONFields(self,json):
    super(LinkedInEvent, self).fromJSONFields(json)
    ''' Customization
    '''
    return self
  
  def toJSONFields(self,json):
    super(LinkedInEvent, self).toJSONFields(json)
    ''' customization
    '''

  def getType(self):
    return "linkedin"

  def getEventTime(self):
    return datetime.utcfromtimestamp(int(self.raw_json['timestamp'] / 1000))

  def getEventCaption(self):
    caption = ''
    if self.raw_json['updateType'] == 'SHAR':
      caption = self.raw_json['updateContent']['person']['currentShare'].get('comment')
    elif self.raw_json['updateType'] == 'CONN':
      connection = self.raw_json['updateContent']['person']['connections']['values']
      caption = '%s is now connected to %s %s' % (self.raw_json['updateContent']['person']['firstName'],connection[0]['firstName'],connection[0]['lastName'])
    elif self.raw_json['updateType'] == 'JOBS':
      caption = None
    return caption

  def getEventSource(self):
    return None

  def getEventURL(self):
    return None

  def getEventPhoto(self):
    return None

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

  def fromJSONFields(self,fromJSON):

    super(FoursquareEvent, self).fromJSONFields(fromJSON)

#    print json.dumps(fromJSON, sort_keys=True, indent=2)

    ''' Customization
    '''
    caption = fromJSON['venue'].get('name','')
    shout = fromJSON.get('shout','')
    address = fromJSON['venue']['location'].get('address')
    city = fromJSON['venue']['location'].get('city')

    # define location
    location = None
    if (address and city):
      location = '%s, %s' % (address,city)
    elif address:
      location = address
    else:
      location = city
    
    location = ' (%s)' % location if location else ''

    self.source = location

    source_name = fromJSON['source'].get('name','')
    source_url = fromJSON['source'].get('url','')
    
    self.source = {"name":source_name,"url":source_url}

    self.caption = '%s%s' % (caption,location)
    self.content = shout
  
    return self


  def getType(self):
    return "foursquare"

  def getEventTime(self):
    return datetime.utcfromtimestamp(int(self.raw_json['createdAt']))

  def getEventCaption(self):
    return self.caption

  def getEventSource(self):
    return '%s#%s' % (self.source['name'],self.source['url']) 


'''
'''
class PhotoEvent(Event):
  pass


class InstagramEvent(PhotoEvent):

  caption = None
  content = None
  source = None

  def fromJSONFields(self,fromJSON):

    super(InstagramEvent, self).fromJSONFields(fromJSON)

#    print json.dumps(fromJSON, sort_keys=True, indent=2)

    ''' Customization
    '''
 
    return self


  def getType(self):
    return "instagram"

  def getEventTime(self):
    return datetime.utcfromtimestamp(float(self.raw_json['created_time']))

  def getEventCaption(self):
    return self.raw_json['caption']['text'] if 'caption' in self.raw_json and self.raw_json['caption'] and 'text' in self.raw_json['caption'] else None

  def getAuxillaryContent(self):
    auxData = {}
    if 'location' in self.raw_json:
      auxData['location'] = self.raw_json['location']
    if 'images' in self.raw_json:
      auxData['images'] = self.raw_json['images']
    return json.dumps(auxData,sort_keys=True,)

'''
'''
class FlickrEvent(PhotoEvent):
  pass

'''
'''
class SocialEvent(Event):
  pass