def _create_tim_message(version, message_type):
  ''' Root for all messages.  Encapsulates standard header and message
  definition.  Message are just dictionaries so only the control
  of their creation is enforced.
  '''
  return {'header': {'version': version, 'type': message_type},
          'message': None}


def create_notification_message(service_name, service_author_id):
  ''' Notification message format.

  Represents messages requesting retrieval of new events for the specified user
  '''
  VERSION = 1

  json_dict = _create_tim_message(VERSION, service_name + '.notification')
  json_dict['message'] = {'service_author_id': service_author_id}
  return json_dict


def create_facebook_notification(facebook_user_id):
  return create_notification_message('facebook', facebook_user_id)


def create_twitter_notification(twitter_user_id):
  return create_notification_message('twitter', twitter_user_id)


def create_instagram_notification(instagram_user_id):
  return create_notification_message('instagram', instagram_user_id)


def create_foursquare_notification(foursquare_user_id):
  return create_notification_message('foursquare', foursquare_user_id)


def create_linkedin_notification(linkedin_user_id):
  return create_notification_message('linkedin', linkedin_user_id)


def create_googleplus_notification(googleplus_user_id):
  return create_notification_message('googleplus', googleplus_user_id)


def create_event_message(service_id, tim_author_id, service_author_id, json_event_dict):
  ''' Raw service event message.

  Holds messages containing raw service events that need to be added or updated
  in the system.
  '''
  VERSION = 1

  json_dict = _create_tim_message(VERSION, service_id + '.event')
  json_dict['message'] = {'tim_author_id': tim_author_id,
                          'service_author_id': service_author_id,
                          'service_event_json': json_event_dict}
  return json_dict


def create_facebook_event(facebook_user_id, tim_author_id, json_event_dict):
  return create_event_message('facebook', tim_author_id, facebook_user_id, json_event_dict)


def create_twitter_event(twitter_user_id, tim_author_id, json_event_dict):
  return create_event_message('twitter', tim_author_id, twitter_user_id, json_event_dict)


def create_instagram_event(instagram_user_id, tim_author_id, json_event_dict):
  return create_event_message('instagram', tim_author_id, instagram_user_id, json_event_dict)


def create_foursquare_event(foursquare_user_id, tim_author_id, json_event_dict):
  return create_event_message('foursquare', tim_author_id, foursquare_user_id, json_event_dict)


def create_linkedin_event(linkedin_user_id, tim_author_id, json_event_dict):
  return create_event_message('linkedin', tim_author_id, linkedin_user_id, json_event_dict)


def create_googleplus_event(googleplus_user_id, tim_author_id, json_event_dict):
  return create_event_message('googleplus', tim_author_id, googleplus_user_id, json_event_dict)


def create_event_update_message(service_id, service_author_id, service_event_id):
  '''Update event message.

  Stores messages containing event identifiers that need to be checked for
  updates.
  '''
  VERSION = 1

  json_dict = _create_tim_message(VERSION, service_id + '.update')
  json_dict['message'] = {'service_author_id': service_author_id,
                          'service_event_id': service_event_id,
                          'service_id': service_id}
  return json_dict
