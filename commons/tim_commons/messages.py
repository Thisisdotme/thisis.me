# standard state arguments used in the event messages
CURRENT_STATE = 'current'
NOT_FOUND_STATE = 'not_found'


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
  message_type = 'collection.refresh.user.{0}'.format(service_name)

  json_dict = _create_tim_message(VERSION, message_type)
  json_dict['message'] = {
      'service_author_id': service_author_id,
      'service_name': service_name}
  return json_dict


def create_event_link(service_id, service_event_id):
  '''
    Utility function for creating an event message link element
  '''
  return {'service_id': service_id, 'service_event_id': service_event_id}


def create_event_message(
    service_name,
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links):
  ''' Raw service event message.

  Holds messages containing raw service events that need to be added or updated
  in the system.
  '''
  def action(message_state):
    if message_state == CURRENT_STATE:
      return 'update'
    elif message_state == NOT_FOUND_STATE:
      return 'delete'
    else:
      raise ValueError('Not a valid state: {0}'.format(message_state))

  VERSION = 1
  message_type = 'process.{0}.post.{1}'.format(action(state), service_name)

  json_dict = _create_tim_message(VERSION, message_type)
  json_dict['message'] = {'tim_author_id': tim_author_id,
                          'service_author_id': service_author_id,
                          'service_event_id': service_event_id,
                          'service_event_json': json_event_dict,
                          'service_name': service_name,
                          'state': state,
                          'links': links}
  return json_dict


def create_facebook_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'facebook',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_twitter_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'twitter',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_instagram_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'instagram',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_foursquare_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'foursquare',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_linkedin_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'linkedin',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_googleplus_event(
    tim_author_id,
    state,
    service_author_id,
    service_event_id,
    json_event_dict,
    links=None):
  return create_event_message(
      'googleplus',
      tim_author_id,
      state,
      service_author_id,
      service_event_id,
      json_event_dict,
      links)


def create_event_update_message(service_name, service_author_id, service_event_id):
  ''' Update event message.

  Stores messages containing event identifiers that need to be checked for
  updates.
  '''
  VERSION = 1
  message_type = 'collection.refresh.post.{0}'.format(service_name)

  json_dict = _create_tim_message(VERSION, message_type)
  json_dict['message'] = {'service_author_id': service_author_id,
                          'service_event_id': service_event_id,
                          'service_name': service_name}
  return json_dict
