'''
Created on May 7, 2012

@author: howard
'''

'''
  Root for all messages.  Encapsulates standard header and message 
  functionality
'''
class TIMMessage(object):

  def __init__(self):
    '''
    Constructor
    '''

'''
  Notification message format.  Represents messages requesting retrieval 
  of new events for the specified user
'''
class NotificationMessage(TIMMessage):
  pass

class FacebookNotification(NotificationMessage):
  pass


'''
  Raw service event message.  Holds messages containing raw service 
  events that need to be added or updated in the system.
'''
class ServiceEventMessage(TIMMessage):
  pass

class FacebookEventMessage(ServiceEventMessage):
  pass


'''
  Update event message.  Stores messages containing event identifiers 
  that need to be checked for updates
'''
class UpdateEventMessage(TIMMessage):
  pass

class FacebookUpdateEventMessage(UpdateEventMessage):
  pass