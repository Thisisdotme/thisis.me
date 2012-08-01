from event_interpreter.facebook_event_interpreter import (
    FacebookPhotoAlbumEventInterpreter,
    FacebookPhotoEventInterpreter,
    FacebookCheckinInterpreter,
    FacebookStatusEventInterpreter)
from event_interpreter.twitter_event_interpreter import (
    TwitterEventInterpreter,
    _TwitterDeleteEventInterpreter)
from event_interpreter.foursquare_event_interpreter import FoursquareEventInterpreter
from event_interpreter.googleplus_event_interpreter import GoogleplusStatusEventInterpreter
from event_interpreter.instagram_event_interpreter import InstagramEventInterpreter
from event_interpreter.linkedin_event_interpreter import LinkedinEventInterpreter


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
  if 'delete' in json_object:
    return _TwitterDeleteEventInterpreter(json_object)
  else:
    return _TwitterEventInterpreter(json_object, author_service_map, oauth_config)


def _create_foursquare_event_interpreter(json_object, author_service_map, oauth_config):
  return _FoursquareEventInterpreter(json_object, author_service_map, oauth_config)


def _create_googleplus_event_interpreter(json_object, author_service_map, oauth_config):
  return _GoogleplusStatusEventInterpreter(json_object, author_service_map, oauth_config)


def _create_instagram_event_interpreter(json_object, author_service_map, oauth_config):
  return _InstagramEventInterpreter(json_object, author_service_map, oauth_config)


def _create_linkedin_event_interpreter(json_object, author_service_map, oauth_config):
  return _LinkedinEventInterpreter(json_object, author_service_map, oauth_config)

_FacebookPhotoAlbumEventInterpreter = FacebookPhotoAlbumEventInterpreter
_FacebookPhotoEventInterpreter = FacebookPhotoEventInterpreter
_FacebookCheckinInterpreter = FacebookCheckinInterpreter
_FacebookStatusEventInterpreter = FacebookStatusEventInterpreter
_TwitterEventInterpreter = TwitterEventInterpreter
_FoursquareEventInterpreter = FoursquareEventInterpreter
_GoogleplusStatusEventInterpreter = GoogleplusStatusEventInterpreter
_InstagramEventInterpreter = InstagramEventInterpreter
_LinkedinEventInterpreter = LinkedinEventInterpreter
