from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from mi_schema.models import (
    Author,
    ServiceObjectType,
    ServiceEvent,
    Relationship,
    AuthorServiceMap)

import miapi.controllers.author_utils
import miapi.resource
import data_access.author
import tim_commons.db


def add_views(configuration):
  configuration.add_view(
      get_photos,
      context=miapi.resource.Photos,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def get_photos(photos_context, request):
  author_id = photos_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author %s' % author_id}

  album_id = photos_context.album_id

  try:
    album = tim_commons.db.Session().query(ServiceEvent). \
            filter_by(id=album_id, type_id=ServiceObjectType.PHOTO_ALBUM_TYPE). \
            one()
  except NoResultFound:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown album %s' % album_id}

  photos = []

  # check for the ALL well-known album and handle specially
  if album.event_id == ServiceEvent.make_well_known_service_event_id(ServiceEvent.ALL_PHOTOS_ID, author_id):
    for event, asm, author in tim_commons.db.Session(). \
        query(ServiceEvent, AuthorServiceMap, Author). \
        join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                    ServiceEvent.service_id == AuthorServiceMap.service_id)). \
        join(Author, ServiceEvent.author_id == Author.id). \
        filter(and_(ServiceEvent.author_id == author_id,
                    ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
        order_by(ServiceEvent.create_time.desc()). \
        limit(200):
      photo = miapi.controllers.author_utils.createServiceEvent(
          request,
          event,
          asm,
          author)
      if photo:
        photos.append(photo)
  else:
    # handle photos for other albums with relationship mappings
    for event, asm, author in tim_commons.db.Session(). \
        query(ServiceEvent, AuthorServiceMap, Author). \
        join(Relationship, and_(Relationship.child_author_id == ServiceEvent.author_id,
                                Relationship.child_service_id == ServiceEvent.service_id,
                                Relationship.child_service_event_id == ServiceEvent.event_id)). \
        join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                    ServiceEvent.service_id == AuthorServiceMap.service_id)). \
        join(Author, ServiceEvent.author_id == Author.id). \
        filter(and_(Relationship.parent_author_id == author_id,
                    Relationship.parent_service_id == album.service_id,
                    Relationship.parent_service_event_id == album.event_id)). \
        order_by(ServiceEvent.create_time.desc()):
      photo = miapi.controllers.author_utils.createServiceEvent(
          request,
          event,
          asm,
          author)
      if photo:
        photos.append(photo)

  return {'author': miapi.controllers.get_tim_author_fragment(request, author.author_name),
          'photos': photos,
          'paging': {'prev': None, 'next': None}}
