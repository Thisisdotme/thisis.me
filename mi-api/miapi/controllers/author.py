import logging
import datetime

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import passlib.hash

import pyramid.security

import mi_schema.models
import data_access.service
import data_access.service_event
import data_access.author
import data_access.author_reservation
import data_access.author_group_map
import data_access.author_group
import data_access.author_service_map

from tim_commons import db

import miapi.resource
import miapi.controllers.feature_utils
import miapi.controllers.author_utils
import miapi.json_renders.author


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
      request_method='PATCH',
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
  for author, asm in db.Session().query(mi_schema.models.Author, mi_schema.models.AuthorServiceMap). \
                                  join(mi_schema.models.AuthorServiceMap,
                                       and_(mi_schema.models.Author.id == mi_schema.models.AuthorServiceMap.author_id,
                                            mi_schema.models.AuthorServiceMap.service_id == data_access.service.name_to_id("me"))). \
                                       all():
    author_json = miapi.json_renders.author.to_JSON_dictionary(author, asm)
    author_list.append(author_json)

  return author_list


def add_author(request):
  author_info = request.json_body

  author_name = author_info.get('name')
  if author_name is None:
    # TODO: better error
    return {'error': 'Missing author'}

  plain_password = author_info.get('password')
  if plain_password == None:
    request.response.status_int = 400
    # TODO: better error
    return {'error': 'Missing required property: password'}
  enc_password = passlib.hash.sha256_crypt.encrypt(plain_password)

  fullname = author_info.get('full_name')
  if fullname == None:
    request.response.status_int = 400
    # TODO: better error
    return {'error': 'Missing required property: full_name'}

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
    author = mi_schema.models.Author(author_name, email, fullname, enc_password, template)
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

  author_json = miapi.json_renders.author.to_JSON_dictionary(author)
  logging.info("create author %s", author_name)

  # TODO: return the correct code
  return author_json


#################### Author ####################

def view_author(author_context, request):
  author = author_context.author

  author_json = miapi.json_renders.author.to_JSON_dictionary(author)

  if pyramid.security.unauthenticated_userid(request) == author.id:
    miapi.json_renders.author.append_private_JSON(author, author_json)

  # TODO: replace getAuthorFeature with something better. should be passing sessions around
  author_json['features'] = miapi.controllers.feature_utils.get_author_features(
      author.id,
      request)

  return author_json


def update_author(author_context, request):
  author = author_context.author

  author_info = request.json_body
  plain_password = author_info.get('password')
  if plain_password:
    author.password = passlib.hash.sha256_crypt.encrypt(plain_password)

  fullname = author_info.get('fullname')
  if fullname:
    author.full_name = fullname

  email = author_info.get('email')
  if email:
    author.email = email

  template = author_info.get('template')
  if template:
    author.template = template

  tagline = author_info.get('tagline')
  if tagline:
    author.tagline = tagline

  data_access.flush()

  # TODO: return the correct code
  return miapi.json_renders.author.to_JSON_dictionary(author)


def delete_author(author_context, request):
  author = author_context.author

  data_access.author.delete_author(author)
  data_access.author_reservation.delete_author_reservation(author.author_name)

  logging.info("deleted author: %s" % author.id)

  # TODO: return correct code (delete http code?)
  return {}


def view_author_topstories(author_context, request):
  author = author_context.author

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  # TODO: story limit should be configurable
  story_limit = 5

  top_stories = data_access.service_event.query_service_events_page(author.id, story_limit)
  events = []
  for event in top_stories:
    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author.id,
        event.service_id)

    event_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        event,
        me_asm,
        asm,
        author)
    if event_obj:
      events.append(event_obj)

  return events
