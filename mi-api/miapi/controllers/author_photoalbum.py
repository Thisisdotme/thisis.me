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

  max_page_limit = miapi.tim_config['api']['max_page_limit']
  page_limit = min(request.params.get('count', max_page_limit), max_page_limit)

  # get the query parameters
  since_date, since_service_id, since_event_id = miapi.controllers.parse_page_param(
      request.params.get('since'))
  until_date, until_service_id, until_event_id = miapi.controllers.parse_page_param(
      request.params.get('until'))

  album_events = data_access.service_event.query_photo_albums_page(
      author.id,
      page_limit,
      since_date=since_date,
      since_service_id=since_service_id,
      since_event_id=since_event_id,
      until_date=until_date,
      until_service_id=until_service_id,
      until_event_id=until_event_id)

  prev_link = None
  next_link = None
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

      param_value = miapi.controllers.create_page_param(
          album_event.create_time,
          album_event.service_id,
          album_event.event_id)

      if prev_link is None:
        prev_link = request.resource_url(
            photo_albums_context,
            query={'since': param_value, 'count': page_limit})
      next_link = request.resource_url(
          photo_albums_context,
          query={'until': param_value, 'count': page_limit})

  return {'entries': albums,
          'paging': {'prev': prev_link, 'next': next_link}}


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
