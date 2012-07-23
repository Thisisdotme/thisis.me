import requests
import hashlib
import base64
import urlparse
import calendar
import datetime
import logging

from tim_commons import normalize_uri, db, json_serializer
from mi_schema import models
from data_access import post_type, service, author_service_map, service_event, author

import pudb
pudb.set_trace()


def _correlate_event(event_json):
  # Extract the origin url
  uri = event_json.original_content_uri()

  if uri:
    # Normalize the URL: follow redirect
    normalized_uri = _normalize_uri(uri)
    # Generate id for this
    return (_generate_id(normalized_uri), normalized_uri)

  return (None, None)


def _normalize_uri(uri):
  response = requests.head(uri, allow_redirects=True)
  return normalize_uri(response.url)


def _generate_id(url):
  encrypt = hashlib.sha256()
  encrypt.update(url)
  return base64.urlsafe_b64encode(encrypt.digest())[:-1]


def correlate_and_update_event(event_json, service_event_object, me_service_id):
  service_event_object.correlation_id, url = _correlate_event(event_json)

  if service_event_object.correlation_id:
    # Get the ASM for this user
    asm = author_service_map.query_asm_by_author_and_service(
        service_event_object.author_id,
        me_service_id)

    # We have a correlation
    correlation_event = service_event.query_correlation_event(
        me_service_id,
        service_event_object.correlation_id,
        service_event_object.author_id)

    correlated_events = service_event.query_correlated_events(
        service_event_object.author_id,
        service_event_object.correlation_id)
    # Lets make sure that new event is at the front of the list
    correlated_events.insert(0, service_event_object)

    author_object = author.query_author(service_event_object.author_id)

    json_string = json_serializer.dump_string(_create_json_from_correlations(
          url,
          correlated_events,
          author_object))

    if correlation_event:
      correlation_event.modify_time = max(
          correlation_event.modify_time,
          service_event_object.modify_time)
      correlation_event.json = json_string
    else:
      # create a new row with this id
      correlation_event = models.ServiceEvent(
          asm.id,
          models.ServiceObjectType.CORRELATION_TYPE,
          service_event_object.author_id,
          me_service_id,
          service_event_object.correlation_id,
          service_event_object.create_time,
          service_event_object.modify_time,
          url=url,
          json=json_string)
      db.Session().add(correlation_event)


def _create_json_from_correlations(uri, correlated_events, author):
  source_service_name = _service_name_from_uri(uri)
  source_service_object = service.name_to_service.get(source_service_name)

  sources = _create_shared_services(correlated_events)

  # for now lets use the "source" event to generate the json
  source_event = None
  create_time = datetime.datetime.utcnow()
  modify_time = datetime.datetime(2000, 1, 1)

  # Lets see if we can find the original source
  for service_event in correlated_events:
    if source_service_object and service_event.service_id == source_service_object.id:
      source_event = service_event
    elif source_event is None:
      source_event = service_event
      service_name = service.id_to_service[service_event.service_id].service_name

    create_time = min(create_time, service_event.create_time)
    modify_time = max(modify_time, service_event.modify_time)

  if source_event:
    content = {}
    if source_event.caption:
      content['label'] = source_event.caption
    if source_event.content:
      content['data'] = source_event.content
    if source_event.auxillary_content:
      content['auxillary_data'] = json_serializer.load_string(source_event.auxillary_content)
    if source_event.url:
      content['url'] = source_event.url
    if source_event.photo_url:
      content['photo_url'] = source_event.photo_url

    author_info = _create_author_info(author)

    event = {'type': post_type.id_to_label(source_event.type_id),
             'service': service_name,
             'create_time': calendar.timegm(create_time.timetuple()),
             'modify_time': calendar.timegm(modify_time.timetuple()),
             'content': content,
             'author': author_info,
             'sources': {'count': len(sources), 'items': sources}}

    event['photo'], event['location'] = _create_photo_json(source_event)

    return event


def _create_photo_json(source_event):
  size_ordered_images = {}

  location = None
  images = []

  if source_event.service_id == service.name_to_id('facebook'):
    json_obj = json_serializer.load_string(source_event.json)

    # for some reason not all facebook photo events have an image property; if
    # it doesn't skip it
    if 'images' not in json_obj:
      logging.warning('Skipping Facebook event with no images')
      return [], None

    for candidate in json_obj.get('images', []):

      size = candidate.get('width', 0) * candidate.get('height', 0)

      image = {'url': candidate['source'],
               'width': candidate['width'],
               'height': candidate['height']}

      size_ordered_images[size] = image

  elif source_event.service_id == service.name_to_id('instagram'):
    json_obj = json_serializer.load_string(source_event.json)

    for candidate in json_obj['images'].itervalues():

      size = candidate.get('width', 0) * candidate.get('height', 0)

      image = {'url': candidate['url'],
              'width': candidate['width'],
              'height': candidate['height']}

      size_ordered_images[size] = image

    if 'location' in json_obj:
      location = json_obj['location']

  for size, image in sorted(size_ordered_images.iteritems(), key=lambda x: x[1]):
    images.append(image)

  return images, location


def _create_shared_services(correlated_events):
  sources = []
  for service_event in correlated_events:
    sources.append(
        {'service_name': service.id_to_service[service_event.service_id].service_name})

  return sources


def _service_name_from_uri(uri):
  parsed_uri = urlparse.urlparse(uri)

  return _hostname_to_service_map.get(parsed_uri.hostname)

_hostname_to_service_map = {'www.facebook.com': 'facebook',
                            'instagr.am': 'instagram',
                            'instagram.com': 'instagram'}


def _create_author_info(author):
  author_obj = {'profile_image_url': '',  # TODO: profile_image_url
                'name': author.author_name,
                'full_name': author.full_name}

  return author_obj
