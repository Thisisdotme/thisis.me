import requests
import hashlib
import base64
import urlparse
import datetime
import logging

from tim_commons import normalize_uri, db, json_serializer
from mi_schema import models
from data_access import service, author_service_map, service_event
import event_interpreter


def correlate_event(event_json):
  # Extract the origin url
  uri = event_json.original_content_uri()

  if uri:
    # Normalize the URL: follow redirect
    normalized_uri = _normalize_uri(uri)
    # Generate id for this
    correlation_id = _generate_id(normalized_uri)
    return (correlation_id, normalized_uri)

  return (None, None)


def _normalize_uri(uri):
  # We should be using GET instead of HEAD because some servers don't redirect them the same.
  response = requests.get(uri, allow_redirects=True)
  return normalize_uri(response.url)


def _generate_id(url):
  encrypt = hashlib.sha256()
  encrypt.update(url)
  return base64.urlsafe_b64encode(encrypt.digest())[:-1]


def correlate_and_update_event(url, correlation_id, author_id, me_service_id):
  if correlation_id:
    # Get the ASM for this user
    asm = author_service_map.query_asm_by_author_and_service(author_id, me_service_id)

    # We have a correlation
    correlation_event = service_event.query_correlation_event(
        me_service_id,
        correlation_id,
        author_id)

    correlated_events = service_event.query_correlated_events(author_id, correlation_id)

    (correlation_json,
     source_event,
     created_time,
     modified_time) = _analyze_correlated_events(url, correlated_events)

    json_string = json_serializer.dump_string(correlation_json)

    if correlation_event:
      correlation_event.modify_time = modified_time
      correlation_event.create_time = created_time
      correlation_event.headline = source_event.headline
      correlation_event.caption = source_event.caption
      correlation_event.tagline = source_event.tagline
      correlation_event.content = source_event.content
      correlation_event.photo_url = source_event.photo_url
      correlation_event.json = json_string
    else:
      # create a new row with this id
      correlation_event = models.ServiceEvent(
          asm.id,
          models.ServiceObjectType.CORRELATION_TYPE,
          author_id,
          me_service_id,
          correlation_id,
          created_time,
          modified_time,
          headline=source_event.headline,
          caption=source_event.caption,
          tagline=source_event.tagline,
          content=source_event.content,
          photo_url=source_event.photo_url,
          json=json_string)
      db.Session().add(correlation_event)
    db.Session().flush()


def _analyze_correlated_events(uri, correlated_events):
  source_service_name = _service_name_from_uri(uri)
  source_service_object = service.name_to_service.get(source_service_name)

  shares = _create_shared_services(correlated_events)

  # for now lets use the "source" event to generate the json
  event = None
  source_event = None
  created_time = datetime.datetime.utcnow()
  modified_time = datetime.datetime(2000, 1, 1)

  # Lets see if we can find the original source
  found_source = False
  for service_event in correlated_events:
    # figure out the source event
    if source_service_object and service_event.service_id == source_service_object.id:
      source_event = service_event
      found_source = True
    elif not found_source:
      if source_event:
        source_priority = _priority[source_service_name]
        event_priority = _priority[service.id_to_service[service_event.service_id].service_name]
        if event_priority > source_priority:
          source_event = service_event
          source_service_name = service.id_to_service[service_event.service_id].service_name
      else:
          source_event = service_event
          source_service_name = service.id_to_service[service_event.service_id].service_name

    created_time = min(created_time, service_event.create_time)
    modified_time = max(modified_time, service_event.modify_time)

  if source_event:
    source_event_interpreter = event_interpreter.create_event_interpreter(
      source_service_name,
      json_serializer.load_string(source_event.json),
      None,
      None)

    if found_source:
      origin = {'type': 'known',
                'known': {'event_id': source_event.id,
                          'service_event_id': source_event.event_id,
                          'service_event_url': source_event_interpreter.url(),
                          'service_name': source_service_name}}
    else:
      parsed_uri = urlparse.urlparse(uri)
      favicon_uri = urlparse.urlunparse((
            parsed_uri[0],
            parsed_uri[1],
            'favicon.ico',
            '',
            '',
            ''))
      origin = {'type': 'unknown',
                'unknown': {'event_id': source_event.id,
                            'service_event_id': source_event.event_id,
                            'service_event_url': source_event_interpreter.url(),
                            'service_name': source_service_name,
                            'domain': parsed_uri.netloc,
                            'small_icon': favicon_uri,
                            'url': uri}}
    event = {'origin': origin,
             'shares': shares}
  else:
    logging.error(
        'Could not create correlation event for url: %s with: %s',
        uri,
        correlated_events)

  return (event, source_event, created_time, modified_time)


_priority = {
  'instagram': 100,
  'foursquare': 99,
  'youtube': 98,
  'wordpress': 97,
  'flickr': 96,
  'googleplus': 95,
  'facebook': 94,
  'linkedin': 93,
  'twitter': 92}


def _create_shared_services(correlated_events):
  sources = []
  for service_event in correlated_events:
    service_event_interpreter = event_interpreter.create_event_interpreter(
        service.id_to_service[service_event.service_id].service_name,
        json_serializer.load_string(service_event.json),
        None,
        None)
    sources.append(
        {'service_name': service.id_to_service[service_event.service_id].service_name,
         'event_id': service_event.id,
         'service_event_id': service_event.event_id,
         'service_event_url': service_event_interpreter.url(),
         'author_id': service_event.author_id,
         'service_id': service_event.service_id})
  return sources


def _service_name_from_uri(uri):
  parsed_uri = urlparse.urlparse(uri)

  return _hostname_to_service_map.get(parsed_uri.hostname)

_hostname_to_service_map = {'www.facebook.com': 'facebook',
                            'instagr.am': 'instagram',
                            'instagram.com': 'instagram'}
