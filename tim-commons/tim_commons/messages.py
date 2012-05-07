'''
Created on May 7, 2012

@author: howard
'''

'''
  Root for all messages.  Encapsulates standard header and message
  definition.  Message are just dictionaries so only the control
  of their creation is enforced.
'''


def _create_tim_message(version, message_type):
  return {'header': {'version': version, 'type': message_type},
          'message': None}


'''
  Notification message format.

  Represents messages requesting retrieval of new events for the specified user
'''


def _create_notification_message(message_type,
                                 tim_author_id,
                                 service_author_id,
                                 oauth_access_token, oauth_access_secret):

  VERSION = 1

  json_dict = _create_tim_message(VERSION, message_type)

  json_dict['message'] = {'tim_author_id': tim_author_id,
                          'service_author_id': service_author_id,
                          'oauth_access_token': oauth_access_token,
                          'oauth_access_secret': oauth_access_secret}

  return json_dict


def create_facebook_notification(facebook_user_id,
                                 tim_author_id=None,
                                 oauth_access_token=None,
                                 auth_access_secret=None):

  TYPE = 'facebook.notification'

  return _create_notification_message(TYPE,
                                      tim_author_id,
                                      facebook_user_id,
                                      oauth_access_token, auth_access_secret)

'''
  Raw service event message.

  Holds messages containing raw service events that need to be added or updated
  in the system.
'''


def _create_event_message(message_type,
                          tim_author_id,
                          service_author_id,
                          json_event_dict):

  VERSION = 1

  json_dict = _create_tim_message(VERSION, message_type)

  json_dict['message'] = {'tim_author_id': tim_author_id,
                          'service_author_id': service_author_id,
                          'service_event_json': json_event_dict}

  return json_dict


def create_facebook_event(facebook_user_id,
                          tim_author_id,
                          json_event_dict):

  TYPE = 'facebook.event'

  return _create_event_message(TYPE,
                               tim_author_id,
                               facebook_user_id,
                               json_event_dict)


'''
  Update event message.

  Stores messages containing event identifiers that need to be checked for
  updates.
'''


def _create_event_update_message(message_type,
                                 tim_author_id,
                                 service_author_id,
                                 service_event_id):

  VERSION = 1

  json_dict = _create_tim_message(VERSION, message_type)

  json_dict['message'] = {'tim_author_id': tim_author_id,
                          'service_author_id': service_author_id,
                          'service_event_id': service_event_id}

  return json_dict


def create_facebook_event_update(facebook_user_id,
                                 tim_author_id,
                                 facebook_event_id):

  TYPE = 'facebook.update'

  return _create_event_message(TYPE,
                               tim_author_id,
                               facebook_user_id,
                               facebook_event_id)
