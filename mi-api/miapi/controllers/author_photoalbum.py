from sqlalchemy import and_

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, AuthorServiceMap

import tim_commons.db
import data_access.service
import miapi.resource
import miapi.controllers.author_utils


def add_views(configuration):
  # PhotoAblums
  configuration.add_view(
    list_photo_albums,
    context=miapi.resource.PhotoAlbums,
    request_method='GET',
    permission='read',
    renderer='jsonp',
    http_cache=0)


def list_photo_albums(photo_albums_context, request):
  author_id = photo_albums_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author %s' % author_id}

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  albums = []

  # get all well know albums first
  for album, asm, author in tim_commons.db.Session(). \
    query(ServiceEvent, AuthorServiceMap, Author). \
    join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                ServiceEvent.service_id == AuthorServiceMap.service_id)). \
    join(Author, ServiceEvent.author_id == Author.id). \
    filter(and_(ServiceEvent.author_id == author_id,
                ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                ServiceEvent.service_id == data_access.service.name_to_id('me'))). \
    order_by(ServiceEvent.id):

    album_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        album,
        me_asm,
        asm,
        author)
    if album_obj['post_type_detail']['photo_album']['photo_count'] > 0:
      albums.append(album_obj)

  # get all other albums
  for album, asm, author in tim_commons.db.Session(). \
    query(ServiceEvent, AuthorServiceMap, Author). \
    join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                ServiceEvent.service_id == AuthorServiceMap.service_id)). \
    join(Author, ServiceEvent.author_id == Author.id). \
    filter(and_(ServiceEvent.author_id == author_id,
                ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                ServiceEvent.service_id != data_access.service.name_to_id('me'))). \
    order_by(ServiceEvent.create_time.desc()):

    album_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        album,
        me_asm,
        asm,
        author)
    if album_obj['post_type_detail']['photo_album']['photo_count'] > 0:
      albums.append(album_obj)

  # if only 2 albums exist and they contain the same number of photos remove the
  # first (which is the 'all photos' album)
  if len(albums) == 2 and (albums[0]['post_type_detail']['photo_album']['photo_count'] ==
                           albums[1]['post_type_detail']['photo_album']['photo_count']):
    albums.pop(0)

  return {'author': miapi.controllers.get_service_author_fragment(request, me_asm, author),
          'photo_albums': albums,
          'paging': {'prev': None, 'next': None}}
