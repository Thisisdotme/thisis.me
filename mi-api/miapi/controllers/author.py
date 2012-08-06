import logging
import datetime

from sqlalchemy.exc import IntegrityError

import mi_schema.models
import data_access.service
import data_access.service_event
import data_access.author
import data_access.author_reservation
import data_access.author_group_map
import data_access.author_group
import data_access.author_service_map
import tim_commons.db

import miapi.resource
import miapi.controllers
import miapi.controllers.feature_utils
import miapi.controllers.author_utils


def add_views(configuration):
  # Authors
  configuration.add_view(
      list_authors,
      context=miapi.resource.Authors,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_author,
      context=miapi.resource.Authors,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # Author
  configuration.add_view(
      view_author,
      context=miapi.resource.Author,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      update_author,
      context=miapi.resource.Author,
      request_method='POST',
      permission='write',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_author,
      context=miapi.resource.Author,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)

  # Top Stories
  configuration.add_view(
      view_author_topstories,
      context=miapi.resource.Author,
      name='topstories',
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


#################### Authors ####################

def list_authors(request):
  author_list = []
  for author in data_access.author.query_authors():
    author_json = author.toJSONObject()
    author_list.append(author_json)

  return author_list


def add_author(request):
  author_info = request.json_body

  author_name = author_info.get('login')
  if author_name is None:
    # TODO: better error
    return {'error': 'Missing author'}

  password = author_info.get('password')
  if password == None:
    request.response.status_int = 400
    # TODO: better error
    return {'error': 'Missing required property: password'}

  fullname = author_info.get('fullname')
  if fullname == None:
    request.response.status_int = 400
    # TODO: better error
    return {'error': 'Missing required property: fullname'}

  email = author_info.get('email')
  if email == None:
    request.response.status_int = 400
    # TODO: better error
    return {'error': 'Missing required property: email'}

  template = author_info.get('template')

  try:
    # create and insert new author reservation
    data_access.author_reservation.add_author_reservation(
        mi_schema.models.AuthorReservation(author_name, email))
  except IntegrityError, e:
    logging.error(e.message)
    # TODO: better error
    request.response.status_int = 409
    return {'error': e.message}

  try:
    # create and insert new author
    author = mi_schema.models.Author(author_name, email, fullname, password, template)
    data_access.author.add_author(author)
  except IntegrityError, e:
    logging.error(e.message)
    # TODO: better error
    request.response.status_int = 409
    return {'error': e.message}

  # map the ME service to the new author
  asm = mi_schema.models.AuthorServiceMap(author.id, data_access.service.name_to_id('me'))
  data_access.author_service_map.add_author_service_map(asm)

  # insert the all, of-me, and liked photo albums
  data_access.service_event.add_service_event(mi_schema.models.ServiceEvent(
      asm.id,
      mi_schema.models.ServiceObjectType.PHOTO_ALBUM_TYPE,
      author.id,
      data_access.service.name_to_id('me'),
      mi_schema.models.ServiceEvent.make_well_known_service_event_id(
          mi_schema.models.ServiceEvent.ALL_PHOTOS_ID,
          author.id),
      datetime.datetime.now()))

  data_access.service_event.add_service_event(mi_schema.models.ServiceEvent(
      asm.id,
      mi_schema.models.ServiceObjectType.PHOTO_ALBUM_TYPE,
      author.id,
      data_access.service.name_to_id('me'),
      mi_schema.models.ServiceEvent.make_well_known_service_event_id(
          mi_schema.models.ServiceEvent.OFME_PHOTOS_ID,
          author.id),
      datetime.datetime.now()))

  data_access.service_event.add_service_event(mi_schema.models.ServiceEvent(
      asm.id,
      mi_schema.models.ServiceObjectType.PHOTO_ALBUM_TYPE,
      author.id,
      data_access.service.name_to_id('me'),
      mi_schema.models.ServiceEvent.make_well_known_service_event_id(
          mi_schema.models.ServiceEvent.LIKED_PHOTOS_ID,
          author.id),
      datetime.datetime.now()))

  ''' ??? this might only be temporary ???
      Create a default group (follow) and add the author to that group
      so that author is following themselves.
  '''

  author_group = mi_schema.models.AuthorGroup(author.id, 'follow')
  data_access.author_group.add_author_group(author_group)

  data_access.author_group_map.add_author_group_map(
      mi_schema.models.AuthorGroupMap(author_group.id, author.id))

  author_json = author.toJSONObject()
  logging.info("create author %s", author_name)

  # TODO: return the correct code
  return author_json


#################### Author ####################

def view_author(author_context, request):
  author_id = author_context.author_id

  author = data_access.author.query_author(author_id)
  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author %s' % author_id}

  author_json = author.toJSONObject()
  # TODO: replace getAuthorFeature with something better. should be passing sessions around
  author_json['features'] = miapi.controllers.feature_utils.getAuthorFeatures(
      tim_commons.db.Session(),
      author.id)

  return author_json


def update_author(author_context, request):
  author_id = author_context.author_id

  author = data_access.author.query_author(author_id)

  if author:
    author_info = request.json_body
    password = author_info.get('password')
    if password:
      author.password = password

    fullname = author_info.get('fullname')
    if fullname:
      author.full_name = fullname

    email = author_info.get('email')
    if email:
      author.email = email

    template = author_info.get('template')
    if template:
      author.template = template

    try:
      data_access.flush()
    except Exception, e:
      # TODO: better error
      logging.error(e.message)
      request.response.status_int = 500
      return {'error': e.message}

    # TODO: return the correct code
    return author.toJSONObject()

  # TODO: better error
  return {'error': 'user does not exist'}


def delete_author(author_context, request):
  author_id = author_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  data_access.author.delete_author(author)
  data_access.author_reservation.delete_author_reservation(author.author_name)

  logging.info("deleted author: %s" % author_id)

  # TODO: return correct code
  return {}


def view_author_topstories(author_context, request):
  author_id = author_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  author_object = miapi.controllers.get_tim_author_fragment(request, author.author_name)

  # TODO: story limit should be configurable
  story_limit = 5

  top_stories = data_access.service_event.query_service_events_descending_time(
      author_id,
      story_limit)
  events = []
  for event in top_stories:
    # filter well-known and instagram photo albums so they don't appear in the timeline
    if (event.type_id == data_access.post_type.label_to_id('photo-album') and
        (event.service_id == data_access.service.name_to_id('me') or
         event.service_id == data_access.service.name_to_id('instagram'))):
      continue

    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author_id,
        event.service_id)

    event_obj = miapi.controllers.author_utils.createServiceEvent(
        author_context['events'][str(event.id)],
        request,
        event,
        asm,
        author)
    if event_obj:
      events.append(event_obj)

  # TODO: implement the correct result for paging
  return {'author': author_object,
          'events': events,
          'paging': {'prev': None, 'next': None}}
