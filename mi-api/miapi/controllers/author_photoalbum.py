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

  # MetaPhotoAlbums
  configuration.add_view(
      list_meta_photo_albums,
      context=miapi.resource.MetaPhotoAlbums,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def list_photo_albums(photo_albums_context, request):
  author = photo_albums_context.author

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  album_events = data_access.service_event.query_photo_albums(author.id)

  albums = []
  for album_event in album_events:
    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author.id,
        album_event.service_id)

    album_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        album_event,
        me_asm,
        asm,
        author)

    if album_obj:
      albums.append(album_obj)

  return albums


def list_meta_photo_albums(meta_photo_albums_context, request):
  author = meta_photo_albums_context.author

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  album_events = data_access.service_event.query_meta_photo_albums(author.id)

  albums = []
  for album_event in album_events:
    album_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        album_event,
        me_asm,
        me_asm,
        author)
    if album_obj['post_type_detail']['photo_album']['photo_count'] > 0:
      albums.append(album_obj)

  return albums
