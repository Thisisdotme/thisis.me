'''
Created on May 7, 2012

@author: howard
'''

import json


'''
  Root for all messages.  Encapsulates standard header and message 
  functionality
'''

class TIMMessage(object):

  def __init__(self):
    self.jsonDict = None

  # Formats the message dictionary.  All messages must have a header component and
  # a message component
  def create(self,version,message_type):
    self.jsonDict['header'] = { 'version': version, 'type': message_type }
    self.jsonDict['message'] = None
    return self

  # Get the message as a JSON dictionary
  def getJSONDict(self):
    if self.jsonDict:
      raise Exception('Improper usage. Message not yet initialized')
    return self.jsonDict

  # Get the message as a JSON formatted string
  def toJSON(self):
    if self.jsonDict:
      raise Exception('Improper usage. Message not yet initialized')
    return json.dumps(self.jsonDict,sort_keys=True, indent=2)


'''
  Notification message format.
  
  Represents messages requesting retrieval of new events for the specified user
'''
  
class NotificationMessage(TIMMessage):
  
  def create(self, version, message_type, tim_author_id, service_author_id, oauth_access_token, oauth_access_token_secret):
    super(NotificationMessage, self).create(version,message_type)
    self.jsonDict['message'] = { 'tim_author_id':tim_author_id,
                                 'service_author_id':service_author_id,
                                 'oauth_access_token':oauth_access_token,
                                 'oauth_access_token_secret':oauth_access_token_secret }
    return self


class FacebookNotification(NotificationMessage):

  VERSION = 1
  TYPE = 'facebook.notification'

  def create(self,facebook_user_id, tim_author_id=None, oauth_access_token=None, auth_access_token_secret=None):
    super(FacebookNotification, self).create(self.VERSION,self.TYPE,tim_author_id, facebook_user_id, oauth_access_token, auth_access_token_secret)
    return self



'''
  Raw service event message.
  
  Holds messages containing raw service events that need to be added or updated in the system.
'''

class ServiceEventMessage(TIMMessage):

  def create(self, version, message_type, tim_author_id, service_author_id, json_dict):
    super(ServiceEventMessage, self).create(version, message_type)
    self.jsonDict['message'] = { 'tim_author_id':tim_author_id,
                                 'service_author_id':service_author_id,
                                 'service_event_json':json_dict }


class FacebookEventMessage(ServiceEventMessage):

  VERSION = 1
  TYPE = 'facebook.event'

  def create(self, tim_author_id, facebook_user_id, json_dict):
    super(FacebookEventMessage, self).create(self.VERSION,self.TYPE,tim_author_id, facebook_user_id, json_dict)
    return self



'''
  Update event message.
  
  Stores messages containing event identifiers that need to be checked for updates
'''

class UpdateEventMessage(TIMMessage):

  def create(self, version, message_type, tim_author_id, service_author_id, service_event_id):
    super(ServiceEventMessage, self).create(version, message_type)
    self.jsonDict['message'] = { 'tim_author_id':tim_author_id,
                                 'service_author_id':service_author_id,
                                 'service_event_id':service_event_id }

class FacebookUpdateEventMessage(UpdateEventMessage):

  VERSION = 1
  TYPE = 'facebook.update'

  def create(self, tim_author_id, facebook_user_id, facebook_event_id):
    super(FacebookEventMessage, self).create(self.VERSION,self.TYPE,tim_author_id, facebook_user_id, facebook_event_id)
    return self

